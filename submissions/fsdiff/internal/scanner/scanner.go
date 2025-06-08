package scanner

import (
	"fmt"
	"runtime"
	"sync"
	"sync/atomic"
	"time"

	"pkg.jsn.cam/jsn/cmd/fsdiff/internal/merkle"

	"golang.org/x/sys/unix"
	"pkg.jsn.cam/jsn/cmd/fsdiff/internal/snapshot"
	"pkg.jsn.cam/jsn/cmd/fsdiff/internal/system"
)

type Config struct {
	IgnorePatterns []string
	Workers        int
	BufferSize     int
	Verbose        bool
}

type Scanner struct {
	config  *Config
	stats   *ScanStats
	ignorer *PathIgnorer
	hasher  *Hasher
	walker  *Walker
}

type ScanStats struct {
	StartTime      time.Time
	FilesProcessed int64
	DirsProcessed  int64
	BytesProcessed int64
	Errors         int64
}

func New(config *Config) *Scanner {
	if config.BufferSize == 0 {
		config.BufferSize = 256 * 1024
	}
	if config.Workers == 0 {
		config.Workers = runtime.NumCPU() * 2
	}

	// Increase file descriptor limit
	var rLimit unix.Rlimit
	if err := unix.Getrlimit(unix.RLIMIT_NOFILE, &rLimit); err == nil {
		rLimit.Cur = rLimit.Max
		unix.Setrlimit(unix.RLIMIT_NOFILE, &rLimit)
	}

	return &Scanner{
		config:  config,
		stats:   &ScanStats{},
		ignorer: newPathIgnorer(config.IgnorePatterns),
		hasher:  newHasher(config.Workers, config.BufferSize),
		walker:  newWalker(config.Workers * 4),
	}
}

func (s *Scanner) ScanFilesystem(rootPath string) (*snapshot.Snapshot, error) {
	s.stats.StartTime = time.Now()

	if s.config.Verbose {
		fmt.Printf("🚀 Starting scan: %d workers, %dKB buffers\n",
			s.config.Workers, s.config.BufferSize/1024)
	}

	// Start progress monitor
	ctx := make(chan struct{})
	if s.config.Verbose {
		go s.progressMonitor(ctx)
	}

	// Start result collector
	results := make(chan *FileResult, s.config.Workers*10)
	files := make(map[string]*snapshot.FileRecord)

	var collectorWg sync.WaitGroup
	collectorWg.Add(1)
	go func() {
		defer collectorWg.Done()
		for result := range results {
			if result.Error != nil {
				atomic.AddInt64(&s.stats.Errors, 1)
				continue
			}
			files[result.Record.Path] = result.Record

			if result.Record.IsDir {
				atomic.AddInt64(&s.stats.DirsProcessed, 1)
			} else {
				atomic.AddInt64(&s.stats.FilesProcessed, 1)
				atomic.AddInt64(&s.stats.BytesProcessed, result.Record.Size)
			}
		}
	}()

	// Walk and process
	err := s.walker.Walk(rootPath, s.ignorer, s.hasher, results)

	close(results)
	collectorWg.Wait()
	close(ctx)

	// Build snapshot
	duration := time.Since(s.stats.StartTime)
	snap := &snapshot.Snapshot{
		SystemInfo: system.GetSystemInfo(rootPath),
		Files:      files,
		MerkleRoot: merkle.CalculateMerkleRoot(files),
		Stats: snapshot.ScanStats{
			FileCount:    int(atomic.LoadInt64(&s.stats.FilesProcessed)),
			DirCount:     int(atomic.LoadInt64(&s.stats.DirsProcessed)),
			TotalSize:    atomic.LoadInt64(&s.stats.BytesProcessed),
			ErrorCount:   int(atomic.LoadInt64(&s.stats.Errors)),
			ScanDuration: duration,
		},
	}

	if s.config.Verbose {
		s.printSummary(snap)
	}

	return snap, err
}

func (s *Scanner) progressMonitor(ctx <-chan struct{}) {
	ticker := time.NewTicker(2 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ctx:
			return
		case <-ticker.C:
			files := atomic.LoadInt64(&s.stats.FilesProcessed)
			dirs := atomic.LoadInt64(&s.stats.DirsProcessed)
			bytes := atomic.LoadInt64(&s.stats.BytesProcessed)
			elapsed := time.Since(s.stats.StartTime)
			rate := float64(files+dirs) / elapsed.Seconds()

			fmt.Printf("📊 %d files, %d dirs, %s | %.0f items/sec\n",
				files, dirs, formatBytes(bytes), rate)
		}
	}
}

func (s *Scanner) printSummary(snap *snapshot.Snapshot) {
	fmt.Printf("✅ Scan complete: %d files, %d dirs, %s in %v (%.0f files/sec)\n",
		snap.Stats.FileCount, snap.Stats.DirCount,
		formatBytes(snap.Stats.TotalSize), snap.Stats.ScanDuration,
		float64(snap.Stats.FileCount)/snap.Stats.ScanDuration.Seconds())

	if snap.Stats.ErrorCount > 0 {
		fmt.Printf("⚠️  Errors: %d\n", snap.Stats.ErrorCount)
	}
}

func formatBytes(bytes int64) string {
	const unit = 1024
	if bytes < unit {
		return fmt.Sprintf("%d B", bytes)
	}
	div, exp := int64(unit), 0
	for n := bytes / unit; n >= unit; n /= unit {
		div *= unit
		exp++
	}
	return fmt.Sprintf("%.1f %cB", float64(bytes)/float64(div), "KMGTPE"[exp])
}
