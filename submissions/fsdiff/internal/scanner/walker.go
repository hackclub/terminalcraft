package scanner

import (
	"os"
	"path/filepath"
	"sync"
	"sync/atomic"

	"pkg.jsn.cam/jsn/cmd/fsdiff/internal/snapshot"
	systemv2 "pkg.jsn.cam/jsn/cmd/fsdiff/internal/system/v2"
)

type Walker struct {
	dirQueue chan string
	fileJobs chan FileJob
	results  chan<- *FileResult
	workers  int
}

type FileJob struct {
	Info os.FileInfo
	Path string
}

type FileResult struct {
	Record *snapshot.FileRecord
	Error  error
}

func newWalker(queueSize int) *Walker {
	return &Walker{
		dirQueue: make(chan string, 1000),
		fileJobs: make(chan FileJob, queueSize),
		workers:  0,
	}
}

func (w *Walker) Walk(root string, ignorer *PathIgnorer, hasher *Hasher, results chan<- *FileResult) error {
	w.results = results

	// Add root directory
	rootInfo, err := os.Stat(root)
	if err == nil {
		rootRecord := &snapshot.FileRecord{
			Path:     root,
			Size:     0,
			Mode:     rootInfo.Mode(),
			ModTime:  rootInfo.ModTime(),
			IsDir:    true,
			FileInfo: systemv2.GetFileInfo(root, rootInfo),
		}
		results <- &FileResult{Record: rootRecord}
	}

	// Use atomic counter for active directories
	var activeDirs int64 = 1
	var dirMutex sync.Mutex
	dirClosed := false

	// Start directory workers
	var dirWg sync.WaitGroup
	numDirWorkers := 4

	for i := 0; i < numDirWorkers; i++ {
		dirWg.Add(1)
		go w.dirWorker(&dirWg, ignorer, &activeDirs, &dirMutex, &dirClosed)
	}

	// Start file workers
	var fileWg sync.WaitGroup
	for i := 0; i < hasher.workers; i++ {
		fileWg.Add(1)
		go w.fileWorker(&fileWg, hasher, results)
	}

	// Seed with root
	w.dirQueue <- root

	// Wait for all directories to be processed
	dirWg.Wait()
	close(w.fileJobs)

	// Wait for all files to be processed
	fileWg.Wait()

	return nil
}

func (w *Walker) dirWorker(wg *sync.WaitGroup, ignorer *PathIgnorer, activeDirs *int64, dirMutex *sync.Mutex, dirClosed *bool) {
	defer wg.Done()

	for path := range w.dirQueue {
		entries, err := os.ReadDir(path)
		if err != nil {
			if atomic.AddInt64(activeDirs, -1) == 0 {
				dirMutex.Lock()
				if !*dirClosed {
					*dirClosed = true
					close(w.dirQueue)
				}
				dirMutex.Unlock()
			}
			continue
		}

		for _, entry := range entries {
			fullPath := filepath.Join(path, entry.Name())

			if ignorer.ShouldIgnore(fullPath) {
				continue
			}

			info, err := entry.Info()
			if err != nil {
				continue
			}

			if entry.IsDir() {
				// Add directory record
				dirInfo, err := entry.Info()
				if err == nil {
					dirRecord := &snapshot.FileRecord{
						Path:     fullPath,
						Size:     0,
						Mode:     dirInfo.Mode(),
						ModTime:  dirInfo.ModTime(),
						IsDir:    true,
						FileInfo: systemv2.GetFileInfo(fullPath, dirInfo),
					}
					select {
					case w.results <- &FileResult{Record: dirRecord}:
					default:
					}
				}

				atomic.AddInt64(activeDirs, 1)
				select {
				case w.dirQueue <- fullPath:
				default:
					// Queue full, process synchronously
					w.processDir(fullPath, ignorer)
					atomic.AddInt64(activeDirs, -1)
				}
			} else {
				w.fileJobs <- FileJob{Path: fullPath, Info: info}
			}
		}

		if atomic.AddInt64(activeDirs, -1) == 0 {
			dirMutex.Lock()
			if !*dirClosed {
				*dirClosed = true
				close(w.dirQueue)
			}
			dirMutex.Unlock()
		}
	}
}

func (w *Walker) processDir(path string, ignorer *PathIgnorer) {
	entries, err := os.ReadDir(path)
	if err != nil {
		return
	}

	for _, entry := range entries {
		fullPath := filepath.Join(path, entry.Name())
		if ignorer.ShouldIgnore(fullPath) {
			continue
		}

		info, err := entry.Info()
		if err != nil {
			continue
		}

		if entry.IsDir() {
			// Add directory record
			dirRecord := &snapshot.FileRecord{
				Path:     fullPath,
				Size:     0,
				Mode:     info.Mode(),
				ModTime:  info.ModTime(),
				IsDir:    true,
				FileInfo: systemv2.GetFileInfo(fullPath, info),
			}
			w.results <- &FileResult{Record: dirRecord}

			w.processDir(fullPath, ignorer)
		} else {
			w.fileJobs <- FileJob{Path: fullPath, Info: info}
		}
	}
}

func (w *Walker) fileWorker(wg *sync.WaitGroup, hasher *Hasher, results chan<- *FileResult) {
	defer wg.Done()

	for job := range w.fileJobs {
		record := &snapshot.FileRecord{
			Path:     job.Path,
			Size:     job.Info.Size(),
			Mode:     job.Info.Mode(),
			ModTime:  job.Info.ModTime(),
			IsDir:    job.Info.IsDir(),
			FileInfo: systemv2.GetFileInfo(job.Path, job.Info),
		}

		// Hash regular files
		if job.Info.Mode().IsRegular() {
			hash, err := hasher.HashFile(job.Path, job.Info.Size())
			if err != nil {
				record.Hash = "ERROR"
			} else {
				record.Hash = hash
			}
		}

		results <- &FileResult{Record: record}
	}
}
