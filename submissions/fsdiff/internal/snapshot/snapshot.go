package snapshot

import (
	"compress/gzip"
	"encoding/gob"
	"fmt"
	"io/fs"
	"os"
	"time"

	"pkg.jsn.cam/jsn/cmd/fsdiff/internal/system"
	systemv2 "pkg.jsn.cam/jsn/cmd/fsdiff/internal/system/v2"
	"pkg.jsn.cam/jsn/cmd/fsdiff/pkg/fsdiff"
)

// FileRecord represents a single file's metadata and hash
type FileRecord struct {
	ModTime  time.Time          `json:"mod_time"`
	Path     string             `json:"path"`
	Hash     string             `json:"hash"`
	Size     int64              `json:"size"`
	Mode     fs.FileMode        `json:"mode"`
	IsDir    bool               `json:"is_dir"`
	FileInfo *systemv2.FileInfo `json:"file_info,omitempty"` // v2 metadata (permissions, ownership, xattrs, selinux)
}

// ScanStats contains statistics about the filesystem scan
type ScanStats struct {
	FileCount    int           `json:"file_count"`
	DirCount     int           `json:"dir_count"`
	TotalSize    int64         `json:"total_size"`
	ErrorCount   int           `json:"error_count"`
	ScanDuration time.Duration `json:"scan_duration"`
}

// SimpleMerkleData contains just the essential merkle information for serialization
type SimpleMerkleData struct {
	RootHash  uint64 `json:"root_hash"`
	LeafCount int    `json:"leaf_count"`
	Depth     int    `json:"depth"`
}

// Snapshot represents a complete filesystem snapshot
type Snapshot struct {
	Tree       interface{}            `json:"-"` // Don't serialize tree - will be rebuilt
	Files      map[string]*FileRecord `json:"files"`
	SystemInfo system.SystemInfo      `json:"system_info"`
	Version    string                 `json:"version"`
	Stats      ScanStats              `json:"stats"`
	MerkleData SimpleMerkleData       `json:"merkle_data"` // Store essential merkle info
	MerkleRoot uint64                 `json:"merkle_root"`
}

// SnapshotHeader contains metadata for quick snapshot inspection
type SnapshotHeader struct {
	Created    time.Time         `json:"created"`
	SystemInfo system.SystemInfo `json:"system_info"`
	Version    string            `json:"version"`
	Stats      ScanStats         `json:"stats"`
	MerkleRoot uint64            `json:"merkle_root"`
}

// Save saves a snapshot to disk with compression
func Save(snapshot *Snapshot, filename string) error {
	snapshot.Version = fsdiff.SnapshotVersion

	// Extract merkle data before serialization
	if snapshot.Tree != nil {
		// If tree exists, extract its essential data
		// This is a simplified approach to avoid serializing the complex tree
		snapshot.MerkleData = SimpleMerkleData{
			RootHash:  snapshot.MerkleRoot,
			LeafCount: snapshot.Stats.FileCount,
			Depth:     calculateSimpleDepth(len(snapshot.Files)),
		}
	}

	// Clear the tree reference to avoid serialization issues
	originalTree := snapshot.Tree
	snapshot.Tree = nil

	// Create the file
	file, err := os.Create(filename)
	if err != nil {
		return fmt.Errorf("failed to create snapshot file: %v", err)
	}
	defer file.Close()

	// Create gzip writer for compression
	gzWriter, err := gzip.NewWriterLevel(file, gzip.BestCompression)
	if err != nil {
		return fmt.Errorf("failed to create gzip writer: %v", err)
	}
	defer gzWriter.Close()

	// Set gzip header metadata
	gzWriter.Name = filename
	gzWriter.Comment = fmt.Sprintf("fsdiff snapshot v%s - %s",
		fsdiff.Version, snapshot.SystemInfo.String())
	gzWriter.ModTime = time.Now()

	// Encode the snapshot
	encoder := gob.NewEncoder(gzWriter)
	if err := encoder.Encode(snapshot); err != nil {
		// Restore tree reference
		snapshot.Tree = originalTree
		return fmt.Errorf("failed to encode snapshot: %v", err)
	}

	// Ensure all data is written
	if err := gzWriter.Close(); err != nil {
		snapshot.Tree = originalTree
		return fmt.Errorf("failed to close gzip writer: %v", err)
	}

	// Restore tree reference
	snapshot.Tree = originalTree

	// Get final file size
	stat, err := file.Stat()
	if err == nil {
		if snapshot.Stats.TotalSize > 0 {
			compressionRatio := float64(stat.Size()) / float64(snapshot.Stats.TotalSize) * 100
			fmt.Printf("💾 Snapshot saved: %s (%.1f MB, %.1f%% compression)\n",
				filename, float64(stat.Size())/1024/1024, compressionRatio)
		} else {
			fmt.Printf("💾 Snapshot saved: %s (%.1f MB)\n",
				filename, float64(stat.Size())/1024/1024)
		}
	}

	return nil
}

// Load loads a snapshot from disk
func Load(filename string) (*Snapshot, error) {
	// Open the file
	file, err := os.Open(filename)
	if err != nil {
		return nil, fmt.Errorf("failed to open snapshot file: %v", err)
	}
	defer file.Close()

	// Create gzip reader
	gzReader, err := gzip.NewReader(file)
	if err != nil {
		return nil, fmt.Errorf("failed to create gzip reader: %v", err)
	}
	defer gzReader.Close()

	// Decode the snapshot
	decoder := gob.NewDecoder(gzReader)
	var snapshot Snapshot
	if err := decoder.Decode(&snapshot); err != nil {
		return nil, fmt.Errorf("failed to decode snapshot: %v", err)
	}

	// Create a minimal tree representation for compatibility
	// In a real implementation, you might want to rebuild the full tree
	// For now, we'll create a simple placeholder
	snapshot.Tree = &SimpleMerkleTree{
		RootHash:  snapshot.MerkleRoot,
		LeafCount: snapshot.MerkleData.LeafCount,
		Depth:     snapshot.MerkleData.Depth,
	}

	fmt.Printf("📖 Loaded snapshot: %s (%s) - %d files, %d dirs\n",
		snapshot.SystemInfo.Hostname,
		snapshot.SystemInfo.Timestamp.Format("2006-01-02 15:04:05"),
		snapshot.Stats.FileCount,
		snapshot.Stats.DirCount)

	return &snapshot, nil
}

// SimpleMerkleTree is a minimal tree representation for compatibility
type SimpleMerkleTree struct {
	RootHash  uint64
	LeafCount int
	Depth     int
}

// CompareWith provides a simple comparison method
func (t *SimpleMerkleTree) CompareWith(other interface{}) interface{} {
	if otherTree, ok := other.(*SimpleMerkleTree); ok {
		return &SimpleTreeComparison{
			LeftRoot:  t.RootHash,
			RightRoot: otherTree.RootHash,
			Same:      t.RootHash == otherTree.RootHash,
		}
	}
	return nil
}

// SimpleTreeComparison represents a basic tree comparison
type SimpleTreeComparison struct {
	LeftRoot  uint64
	RightRoot uint64
	Same      bool
}

// calculateSimpleDepth estimates tree depth based on file count
func calculateSimpleDepth(fileCount int) int {
	if fileCount <= 1 {
		return 1
	}
	depth := 1
	nodes := 1
	for nodes < fileCount {
		depth++
		nodes *= 2
	}
	return depth
}

// LoadHeader loads only the header information from a snapshot
func LoadHeader(filename string) (*SnapshotHeader, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, fmt.Errorf("failed to open snapshot file: %v", err)
	}
	defer file.Close()

	gzReader, err := gzip.NewReader(file)
	if err != nil {
		return nil, fmt.Errorf("failed to create gzip reader: %v", err)
	}
	defer gzReader.Close()

	// Try to read just enough to get the header
	decoder := gob.NewDecoder(gzReader)
	var snapshot Snapshot
	if err := decoder.Decode(&snapshot); err != nil {
		return nil, fmt.Errorf("failed to decode snapshot header: %v", err)
	}

	header := &SnapshotHeader{
		Version:    snapshot.Version,
		SystemInfo: snapshot.SystemInfo,
		Stats:      snapshot.Stats,
		MerkleRoot: snapshot.MerkleRoot,
		Created:    snapshot.SystemInfo.Timestamp,
	}

	return header, nil
}

// Validate performs basic validation on a snapshot
func (s *Snapshot) Validate() error {
	if s.Version == "" {
		return fmt.Errorf("missing snapshot version")
	}

	if s.SystemInfo.Hostname == "" {
		return fmt.Errorf("missing system hostname")
	}

	if len(s.Files) == 0 {
		return fmt.Errorf("snapshot contains no files")
	}

	if s.Stats.FileCount == 0 && s.Stats.DirCount == 0 {
		return fmt.Errorf("invalid statistics: no files or directories")
	}

	// Verify file count matches
	actualFiles := 0
	actualDirs := 0
	for _, record := range s.Files {
		if record.IsDir {
			actualDirs++
		} else {
			actualFiles++
		}
	}

	if actualFiles != s.Stats.FileCount {
		fmt.Printf("⚠️  Warning: file count mismatch: expected %d, got %d\n",
			s.Stats.FileCount, actualFiles)
		// Don't fail validation, just warn
		s.Stats.FileCount = actualFiles
	}

	if actualDirs != s.Stats.DirCount {
		fmt.Printf("⚠️  Warning: directory count mismatch: expected %d, got %d\n",
			s.Stats.DirCount, actualDirs)
		// Don't fail validation, just warn
		s.Stats.DirCount = actualDirs
	}

	return nil
}

// GetFileRecord retrieves a file record by path
func (s *Snapshot) GetFileRecord(path string) (*FileRecord, bool) {
	record, exists := s.Files[path]
	return record, exists
}

// Summary returns a summary of the snapshot
func (s *Snapshot) Summary() string {
	return fmt.Sprintf("Snapshot: %s@%s (%d files, %d dirs, %s, scan took %v)",
		s.SystemInfo.Hostname,
		s.SystemInfo.Timestamp.Format("2006-01-02 15:04:05"),
		s.Stats.FileCount,
		s.Stats.DirCount,
		formatBytes(s.Stats.TotalSize),
		s.Stats.ScanDuration.Truncate(time.Second))
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
