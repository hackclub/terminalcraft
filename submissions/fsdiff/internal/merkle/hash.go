package merkle

import (
	"sort"
	"sync"

	"github.com/cespare/xxhash/v2"
	"pkg.jsn.cam/jsn/cmd/fsdiff/internal/snapshot"
)

func CalculateMerkleRoot(files map[string]*snapshot.FileRecord) uint64 {
	if len(files) == 0 {
		return 0
	}

	// For large file sets, parallelize
	if len(files) > 10000 {
		return calculateMerkleRootParallel(files)
	}

	// Extract and sort paths for deterministic ordering
	paths := make([]string, 0, len(files))
	for path := range files {
		paths = append(paths, path)
	}
	sort.Strings(paths)

	// Hash all file hashes together
	hasher := xxhash.New()
	for _, path := range paths {
		record := files[path]
		hasher.WriteString(path)
		hasher.WriteString(record.Hash)
	}

	return hasher.Sum64()
}

func calculateMerkleRootParallel(files map[string]*snapshot.FileRecord) uint64 {
	// Extract paths
	paths := make([]string, 0, len(files))
	for path := range files {
		paths = append(paths, path)
	}
	sort.Strings(paths)

	// Split into chunks for parallel processing
	numWorkers := 4
	chunkSize := (len(paths) + numWorkers - 1) / numWorkers

	var wg sync.WaitGroup
	partialHashes := make([]uint64, numWorkers)

	for i := 0; i < numWorkers; i++ {
		start := i * chunkSize
		end := start + chunkSize
		if end > len(paths) {
			end = len(paths)
		}
		if start >= end {
			continue
		}

		wg.Add(1)
		go func(workerID, start, end int) {
			defer wg.Done()

			hasher := xxhash.New()
			for j := start; j < end; j++ {
				path := paths[j]
				record := files[path]
				hasher.WriteString(path)
				hasher.WriteString(record.Hash)
			}
			partialHashes[workerID] = hasher.Sum64()
		}(i, start, end)
	}

	wg.Wait()

	// Combine partial hashes
	finalHasher := xxhash.New()
	for _, h := range partialHashes {
		finalHasher.Write([]byte{
			byte(h), byte(h >> 8), byte(h >> 16), byte(h >> 24),
			byte(h >> 32), byte(h >> 40), byte(h >> 48), byte(h >> 56),
		})
	}

	return finalHasher.Sum64()
}
