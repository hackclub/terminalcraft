package scanner

import (
	"encoding/binary"
	"fmt"
	"io"
	"os"
	"testing"
	"time"

	"github.com/cespare/xxhash/v2"
	"golang.org/x/sys/unix"
)

// Test file sizes
var testSizes = []struct {
	name string
	size int64
}{
	{"1KB", 1024},
	{"4KB", 4 * 1024},
	{"64KB", 64 * 1024},
	{"256KB", 256 * 1024},
	{"1MB", 1024 * 1024},
	{"10MB", 10 * 1024 * 1024},
	{"100MB", 100 * 1024 * 1024},
}

// createTestFile creates a temporary file with deterministic content
func createTestFile(b *testing.B, size int64) string {
	b.Helper()

	tmpfile, err := os.CreateTemp(b.TempDir(), "hashbench")
	if err != nil {
		b.Fatal(err)
	}

	// Write deterministic content
	written := int64(0)
	block := make([]byte, 4096)
	for i := range block {
		block[i] = byte(i % 256)
	}

	for written < size {
		toWrite := size - written
		if toWrite > int64(len(block)) {
			toWrite = int64(len(block))
		}
		n, err := tmpfile.Write(block[:toWrite])
		if err != nil {
			b.Fatal(err)
		}
		written += int64(n)
	}

	tmpfile.Close()
	return tmpfile.Name()
}

// Original implementation
func hashFileOriginal(path string, buffer []byte) (string, error) {
	file, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer file.Close()

	hash := xxhash.New()
	for {
		n, err := file.Read(buffer)
		if n > 0 {
			_, _ = hash.Write(buffer[:n])
		}
		if err == io.EOF {
			break
		}
		if err != nil {
			return "", err
		}
	}

	return fmt.Sprintf("%x", hash.Sum(nil)), nil
}

// Optimized with io.Copy
func hashFileIOCopy(path string, buffer []byte) (string, error) {
	file, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer file.Close()

	hash := xxhash.New()
	_, err = io.CopyBuffer(hash, file, buffer)
	if err != nil {
		return "", err
	}

	return fmt.Sprintf("%x", hash.Sum(nil)), nil
}

// Using mmap for larger files
func hashFileMmap(path string, buffer []byte) (string, error) {
	file, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer file.Close()

	stat, err := file.Stat()
	if err != nil {
		return "", err
	}

	// Only mmap files larger than 1MB
	if stat.Size() > 1024*1024 {
		data, err := unix.Mmap(int(file.Fd()), 0, int(stat.Size()), unix.PROT_READ, unix.MAP_PRIVATE)
		if err != nil {
			// Fall back to regular reading
			hash := xxhash.New()
			_, err = io.CopyBuffer(hash, file, buffer)
			if err != nil {
				return "", err
			}
			return fmt.Sprintf("%x", hash.Sum(nil)), nil
		}
		defer unix.Munmap(data)

		hash := xxhash.New()
		_, _ = hash.Write(data)
		return fmt.Sprintf("%x", hash.Sum(nil)), nil
	}

	// For smaller files, use regular reading
	hash := xxhash.New()
	_, err = io.CopyBuffer(hash, file, buffer)
	if err != nil {
		return "", err
	}
	return fmt.Sprintf("%x", hash.Sum(nil)), nil
}

// Sample-based hashing for very large files
func hashFileSampled(path string, buffer []byte) (string, error) {
	stat, err := os.Stat(path)
	if err != nil {
		return "", err
	}

	file, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer file.Close()

	hash := xxhash.New()

	// Always hash file metadata
	binary.Write(hash, binary.LittleEndian, stat.Size())
	binary.Write(hash, binary.LittleEndian, stat.ModTime().UnixNano())

	// For files over 100MB, sample instead of reading everything
	if stat.Size() > 100*1024*1024 {
		// Read first 1MB
		_, err = io.CopyN(hash, file, 1024*1024)
		if err != nil && err != io.EOF {
			return "", err
		}

		// Read middle 1MB
		file.Seek(stat.Size()/2, 0)
		_, err = io.CopyN(hash, file, 1024*1024)
		if err != nil && err != io.EOF {
			return "", err
		}

		// Read last 1MB
		file.Seek(-1024*1024, 2)
		_, err = io.Copy(hash, file)
		if err != nil {
			return "", err
		}
	} else {
		// For smaller files, hash everything
		_, err = io.CopyBuffer(hash, file, buffer)
		if err != nil {
			return "", err
		}
	}

	return fmt.Sprintf("%x", hash.Sum(nil)), nil
}

// Benchmark runner for each method
func runBenchmark(b *testing.B, name string, size int64, hashFunc func(string, []byte) (string, error), bufSize int) {
	b.Run(fmt.Sprintf("%s_%s_buf%dKB", name, formatSize(size), bufSize/1024), func(b *testing.B) {
		filename := createTestFile(b, size)
		buffer := make([]byte, bufSize)

		b.ResetTimer()
		b.SetBytes(size)

		for i := 0; i < b.N; i++ {
			_, err := hashFunc(filename, buffer)
			if err != nil {
				b.Fatal(err)
			}
		}
	})
}

// Main benchmark functions
func BenchmarkHashMethods(b *testing.B) {
	bufferSizes := []int{
		64 * 1024,  // 64KB (original)
		128 * 1024, // 128KB
		256 * 1024, // 256KB
		512 * 1024, // 512KB
	}

	methods := []struct {
		name string
		fn   func(string, []byte) (string, error)
	}{
		{"Original", hashFileOriginal},
		{"IOCopy", hashFileIOCopy},
		{"Mmap", hashFileMmap},
		{"Sampled", hashFileSampled},
	}

	for _, size := range testSizes {
		for _, bufSize := range bufferSizes {
			for _, method := range methods {
				runBenchmark(b, method.name, size.size, method.fn, bufSize)
			}
		}
	}
}

// Specific benchmarks for different scenarios
func BenchmarkSmallFiles(b *testing.B) {
	sizes := []int64{1024, 4096, 8192}
	buffer := make([]byte, 64*1024)

	for _, size := range sizes {
		filename := createTestFile(b, size)

		b.Run(fmt.Sprintf("Original_%d", size), func(b *testing.B) {
			b.SetBytes(size)
			for i := 0; i < b.N; i++ {
				hashFileOriginal(filename, buffer)
			}
		})

	}
}

func BenchmarkLargeFiles(b *testing.B) {
	sizes := []int64{10 * 1024 * 1024, 100 * 1024 * 1024}
	buffer := make([]byte, 256*1024)

	for _, size := range sizes {
		filename := createTestFile(b, size)

		b.Run(fmt.Sprintf("IOCopy_%s", formatSize(size)), func(b *testing.B) {
			b.SetBytes(size)
			for i := 0; i < b.N; i++ {
				hashFileIOCopy(filename, buffer)
			}
		})

		b.Run(fmt.Sprintf("Mmap_%s", formatSize(size)), func(b *testing.B) {
			b.SetBytes(size)
			for i := 0; i < b.N; i++ {
				hashFileMmap(filename, buffer)
			}
		})

		b.Run(fmt.Sprintf("Sampled_%s", formatSize(size)), func(b *testing.B) {
			b.SetBytes(size)
			for i := 0; i < b.N; i++ {
				hashFileSampled(filename, buffer)
			}
		})
	}
}

// Benchmark syscall overhead
func BenchmarkSyscallOverhead(b *testing.B) {
	// Create files of different sizes
	files := make(map[string]string)
	for _, size := range testSizes {
		files[size.name] = createTestFile(b, size.size)
	}

	// Test with different buffer sizes to measure syscall impact
	bufferSizes := []int{4096, 16384, 65536, 262144, 1048576}

	for sizeName, filename := range files {
		for _, bufSize := range bufferSizes {
			b.Run(fmt.Sprintf("Size_%s_Buffer_%d", sizeName, bufSize), func(b *testing.B) {
				buffer := make([]byte, bufSize)
				info, _ := os.Stat(filename)
				b.SetBytes(info.Size())

				for i := 0; i < b.N; i++ {
					file, err := os.Open(filename)
					if err != nil {
						b.Fatal(err)
					}

					hash := xxhash.New()
					totalRead := int64(0)
					syscalls := 0

					for {
						n, err := file.Read(buffer)
						if n > 0 {
							hash.Write(buffer[:n])
							totalRead += int64(n)
							syscalls++
						}
						if err == io.EOF {
							break
						}
						if err != nil {
							b.Fatal(err)
						}
					}

					file.Close()

					if i == 0 {
						b.Logf("File: %s, Buffer: %d, Syscalls: %d", sizeName, bufSize, syscalls)
					}
				}
			})
		}
	}
}

// Helper function to format sizes
func formatSize(size int64) string {
	const unit = 1024
	if size < unit {
		return fmt.Sprintf("%dB", size)
	}
	div, exp := int64(unit), 0
	for n := size / unit; n >= unit; n /= unit {
		div *= unit
		exp++
	}
	return fmt.Sprintf("%d%cB", size/div, "KMGTPE"[exp])
}

// Benchmark to compare all methods at once
func BenchmarkComparison(b *testing.B) {
	// Create a mix of file sizes that represents a typical filesystem
	fileDistribution := []struct {
		size  int64
		count int
	}{
		{1024, 100},           // 100 files of 1KB
		{4096, 50},            // 50 files of 4KB
		{64 * 1024, 30},       // 30 files of 64KB
		{1024 * 1024, 10},     // 10 files of 1MB
		{10 * 1024 * 1024, 5}, // 5 files of 10MB
	}

	// Create test files
	var testFiles []string
	for _, dist := range fileDistribution {
		for i := 0; i < dist.count; i++ {
			testFiles = append(testFiles, createTestFile(b, dist.size))
		}
	}

	buffer := make([]byte, 256*1024)

	methods := []struct {
		name string
		fn   func(string, []byte) (string, error)
	}{
		{"Original", hashFileOriginal},
		{"IOCopy", hashFileIOCopy},
		{"Mmap", hashFileMmap},
		{"Sampled", hashFileSampled},
	}

	for _, method := range methods {
		b.Run(method.name, func(b *testing.B) {
			start := time.Now()

			b.ResetTimer()
			for i := 0; i < b.N; i++ {
				for _, file := range testFiles {
					_, err := method.fn(file, buffer)
					if err != nil {
						b.Fatal(err)
					}
				}
			}

			b.StopTimer()
			duration := time.Since(start)
			b.Logf("%s: %v per iteration", method.name, duration/time.Duration(b.N))
		})
	}
}
