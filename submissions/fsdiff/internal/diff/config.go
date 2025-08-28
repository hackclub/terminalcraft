package diff

import (
	"time"

	"pkg.jsn.cam/jsn/cmd/fsdiff/internal/snapshot"
)

// Config holds diff configuration
type Config struct {
	IgnorePatterns []string
	Verbose        bool
	ShowHashes     bool
	OnlyChanges    bool
}

// Differ handles comparing snapshots
type Differ struct {
	config  *Config
	ignorer *PathIgnorer
}

// Result represents the comparison between two snapshots
type Result struct {
	Generated time.Time                       `json:"generated"`
	Baseline  *snapshot.Snapshot              `json:"baseline"`
	Current   *snapshot.Snapshot              `json:"current"`
	Added     map[string]*snapshot.FileRecord `json:"added"`
	Modified  map[string]*ChangeDetail        `json:"modified"`
	Deleted   map[string]*snapshot.FileRecord `json:"deleted"`
	Summary   Summary                         `json:"summary"`
}

// ChangeDetail represents details about a modified file
type ChangeDetail struct {
	OldRecord *snapshot.FileRecord `json:"old_record"`
	NewRecord *snapshot.FileRecord `json:"new_record"`
	Changes   []string             `json:"changes"`
}

// Summary contains summary statistics
type Summary struct {
	AddedCount     int           `json:"added_count"`
	ModifiedCount  int           `json:"modified_count"`
	DeletedCount   int           `json:"deleted_count"`
	TotalChanges   int           `json:"total_changes"`
	AddedSize      int64         `json:"added_size"`
	DeletedSize    int64         `json:"deleted_size"`
	SizeDiff       int64         `json:"size_diff"`
	ComparisonTime time.Duration `json:"comparison_time"`
}

// PathIgnorer handles ignore pattern matching for diffs
type PathIgnorer struct {
	patterns []string
}

// ChangeType represents the type of change
type ChangeType string

const (
	ChangeAdded    ChangeType = "added"
	ChangeModified ChangeType = "modified"
	ChangeDeleted  ChangeType = "deleted"
)
