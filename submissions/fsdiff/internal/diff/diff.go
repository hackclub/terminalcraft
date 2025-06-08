package diff

import (
	"fmt"
	"path/filepath"
	"sort"
	"strings"
	"time"

	"pkg.jsn.cam/jsn/cmd/fsdiff/internal/snapshot"
	systemv2 "pkg.jsn.cam/jsn/cmd/fsdiff/internal/system/v2"
)

// New creates a new differ
func New(config *Config) *Differ {
	if config == nil {
		config = &Config{}
	}

	return &Differ{
		config: config,
		ignorer: &PathIgnorer{
			patterns: config.IgnorePatterns,
		},
	}
}

// Compare compares two snapshots and returns the differences
func (d *Differ) Compare(baseline, current *snapshot.Snapshot) *Result {
	startTime := time.Now()

	if d.config.Verbose {
		fmt.Printf("🔍 Comparing snapshots...\n")
		fmt.Printf("   Baseline: %d files (%s)\n",
			baseline.Stats.FileCount, baseline.SystemInfo.Timestamp.Format("2006-01-02 15:04:05"))
		fmt.Printf("   Current:  %d files (%s)\n",
			current.Stats.FileCount, current.SystemInfo.Timestamp.Format("2006-01-02 15:04:05"))
	}

	result := &Result{
		Baseline:  baseline,
		Current:   current,
		Added:     make(map[string]*snapshot.FileRecord),
		Modified:  make(map[string]*ChangeDetail),
		Deleted:   make(map[string]*snapshot.FileRecord),
		Generated: time.Now(),
	}

	// Use Merkle tree comparison for efficiency if available
	if baseline.Tree != nil && current.Tree != nil {
		d.compareMerkleTrees(baseline, current, result)
	} else {
		d.compareBruteForce(baseline, current, result)
	}

	// Calculate summary
	result.Summary = d.calculateSummary(result, time.Since(startTime))

	if d.config.Verbose {
		fmt.Printf("✅ Comparison completed in %v\n", time.Since(startTime))
		fmt.Printf("   Changes: %d added, %d modified, %d deleted\n",
			result.Summary.AddedCount, result.Summary.ModifiedCount, result.Summary.DeletedCount)
	}

	return result
}

// compareMerkleTrees uses Merkle tree comparison for efficient diff
func (d *Differ) compareMerkleTrees(baseline, current *snapshot.Snapshot, result *Result) {
	if d.config.Verbose {
		fmt.Printf("🌳 Using Merkle tree comparison...\n")
	}

	// Quick check: if root hashes are the same, no changes
	if baseline.MerkleRoot == current.MerkleRoot {
		if d.config.Verbose {
			fmt.Printf("✅ Merkle roots match - no changes detected\n")
		}
		return
	}

	if d.config.Verbose {
		fmt.Printf("🔍 Merkle roots differ - performing detailed comparison\n")
		fmt.Printf("   Baseline: %x\n", baseline.MerkleRoot)
		fmt.Printf("   Current:  %x\n", current.MerkleRoot)
	}

	// Since merkle roots differ, fall back to brute force comparison
	// In a full implementation, you could do more sophisticated tree comparison
	d.compareBruteForce(baseline, current, result)
}

// compareBruteForce performs traditional file-by-file comparison
func (d *Differ) compareBruteForce(baseline, current *snapshot.Snapshot, result *Result) {
	if d.config.Verbose {
		fmt.Printf("📊 Using brute force comparison...\n")
	}

	// Create a set of all unique paths
	allPaths := make(map[string]bool)
	for path := range baseline.Files {
		allPaths[path] = true
	}
	for path := range current.Files {
		allPaths[path] = true
	}

	processed := 0
	total := len(allPaths)

	for path := range allPaths {
		if d.ignorer.ShouldIgnore(path) {
			continue
		}

		baselineRecord, inBaseline := baseline.Files[path]
		currentRecord, inCurrent := current.Files[path]

		if !inBaseline && inCurrent {
			// File was added
			result.Added[path] = currentRecord
		} else if inBaseline && !inCurrent {
			// File was deleted
			result.Deleted[path] = baselineRecord
		} else if inBaseline {
			// File exists in both - check if modified
			if !d.filesEqual(baselineRecord, currentRecord) {
				changes := d.detectChanges(baselineRecord, currentRecord)
				result.Modified[path] = &ChangeDetail{
					OldRecord: baselineRecord,
					NewRecord: currentRecord,
					Changes:   changes,
				}
			}
		}

		processed++
		if d.config.Verbose && processed%10000 == 0 {
			fmt.Printf("📊 Processed %d/%d files (%.1f%%)\n",
				processed, total, float64(processed)/float64(total)*100)
		}
	}
}

// filesEqual checks if two file records are equal
func (d *Differ) filesEqual(a, b *snapshot.FileRecord) bool {
	if a.IsDir && b.IsDir {
		// For directories, compare metadata
		return a.Mode == b.Mode &&
			a.ModTime.Equal(b.ModTime) &&
			fileInfoEqual(a.FileInfo, b.FileInfo)
	}

	if a.IsDir != b.IsDir {
		return false
	}

	// For files, compare hash, size, and metadata
	return a.Hash == b.Hash &&
		a.Size == b.Size &&
		a.Mode == b.Mode &&
		fileInfoEqual(a.FileInfo, b.FileInfo)
}

// fileInfoEqual compares v2 FileInfo structures
func fileInfoEqual(a, b *systemv2.FileInfo) bool {
	if a == nil && b == nil {
		return true
	}
	if a == nil || b == nil {
		return false
	}

	// Compare basic permissions and ownership
	if a.OwnerID != b.OwnerID || a.GroupID != b.GroupID || a.Permissions != b.Permissions {
		return false
	}

	// Compare metadata if present
	if (a.Metadata == nil) != (b.Metadata == nil) {
		return false
	}

	if a.Metadata != nil && b.Metadata != nil {
		// Compare SELinux labels
		if !mapsEqual(a.Metadata.SELinux, b.Metadata.SELinux) {
			return false
		}

		// Compare xattrs
		if !mapsEqual(a.Metadata.Xattrs, b.Metadata.Xattrs) {
			return false
		}
	}

	return true
}

// mapsEqual compares two string maps
func mapsEqual(a, b map[string]string) bool {
	if len(a) != len(b) {
		return false
	}
	for k, v := range a {
		if b[k] != v {
			return false
		}
	}
	return true
}

// detectChanges identifies what specifically changed about a file
func (d *Differ) detectChanges(old,
	new *snapshot.FileRecord) []string {
	var changes []string

	if old.Hash != new.Hash && old.Hash != "" && new.Hash != "" {
		changes = append(changes, "content")
	}

	if old.Size != new.Size {
		changes = append(changes, fmt.Sprintf("size (%d → %d)", old.Size, new.Size))
	}

	if old.Mode != new.Mode {
		changes = append(changes, fmt.Sprintf("permissions (%s → %s)", old.Mode, new.Mode))
	}

	if !old.ModTime.Equal(new.ModTime) {
		changes = append(changes, fmt.Sprintf("mtime (%s → %s)",
			old.ModTime.Format("2006-01-02 15:04:05"),
			new.ModTime.Format("2006-01-02 15:04:05")))
	}

	// Check v2 FileInfo changes
	if old.FileInfo != nil && new.FileInfo != nil {
		if old.FileInfo.OwnerID != new.FileInfo.OwnerID {
			changes = append(changes, fmt.Sprintf("uid (%d → %d)", old.FileInfo.OwnerID, new.FileInfo.OwnerID))
		}

		if old.FileInfo.GroupID != new.FileInfo.GroupID {
			changes = append(changes, fmt.Sprintf("gid (%d → %d)", old.FileInfo.GroupID, new.FileInfo.GroupID))
		}

		if old.FileInfo.Permissions != new.FileInfo.Permissions {
			changes = append(changes, fmt.Sprintf("permissions (%04o → %04o)", old.FileInfo.Permissions, new.FileInfo.Permissions))
		}

		// Check metadata changes
		if old.FileInfo.Metadata != nil || new.FileInfo.Metadata != nil {
			metaChanges := d.detectMetadataChanges(old.FileInfo.Metadata, new.FileInfo.Metadata)
			changes = append(changes, metaChanges...)
		}
	} else if (old.FileInfo == nil) != (new.FileInfo == nil) {
		changes = append(changes, "metadata")
	}

	if len(changes) == 0 {
		changes = append(changes, "unknown")
	}

	return changes
}

// detectMetadataChanges compares metadata and returns human-readable change descriptions
func (d *Differ) detectMetadataChanges(oldMeta, newMeta *systemv2.FileMetadata) []string {
	var changes []string

	// Handle nil cases
	if oldMeta == nil && newMeta == nil {
		return changes
	}
	if oldMeta == nil {
		if newMeta.SELinux != nil {
			changes = append(changes, "selinux added")
		}
		if newMeta.Xattrs != nil {
			changes = append(changes, fmt.Sprintf("xattrs added (%d)", len(newMeta.Xattrs)))
		}
		return changes
	}
	if newMeta == nil {
		if oldMeta.SELinux != nil {
			changes = append(changes, "selinux removed")
		}
		if oldMeta.Xattrs != nil {
			changes = append(changes, fmt.Sprintf("xattrs removed (%d)", len(oldMeta.Xattrs)))
		}
		return changes
	}

	// Compare SELinux
	if !mapsEqual(oldMeta.SELinux, newMeta.SELinux) {
		if oldLabel, ok := oldMeta.SELinux["label"]; ok {
			if newLabel, ok := newMeta.SELinux["label"]; ok {
				changes = append(changes, fmt.Sprintf("selinux (%s → %s)", oldLabel, newLabel))
			} else {
				changes = append(changes, "selinux removed")
			}
		} else if _, ok := newMeta.SELinux["label"]; ok {
			changes = append(changes, "selinux added")
		}
	}

	// Compare xattrs
	if !mapsEqual(oldMeta.Xattrs, newMeta.Xattrs) {
		added := 0
		removed := 0
		modified := 0

		// Check for removed/modified
		for k, oldVal := range oldMeta.Xattrs {
			if newVal, exists := newMeta.Xattrs[k]; !exists {
				removed++
			} else if newVal != oldVal {
				modified++
			}
		}

		// Check for added
		for k := range newMeta.Xattrs {
			if _, exists := oldMeta.Xattrs[k]; !exists {
				added++
			}
		}

		if added > 0 || removed > 0 || modified > 0 {
			changes = append(changes, fmt.Sprintf("xattrs (+%d -%d ~%d)", added, removed, modified))
		}
	}

	return changes
}

// calculateSummary calculates summary statistics
func (d *Differ) calculateSummary(result *Result, duration time.Duration) Summary {
	summary := Summary{
		AddedCount:     len(result.Added),
		ModifiedCount:  len(result.Modified),
		DeletedCount:   len(result.Deleted),
		ComparisonTime: duration,
	}

	summary.TotalChanges = summary.AddedCount + summary.ModifiedCount + summary.DeletedCount

	// Calculate size changes
	for _, record := range result.Added {
		summary.AddedSize += record.Size
	}

	for _, record := range result.Deleted {
		summary.DeletedSize += record.Size
	}

	summary.SizeDiff = summary.AddedSize - summary.DeletedSize

	return summary
}

// ShouldIgnore checks if a path should be ignored during diff
func (i *PathIgnorer) ShouldIgnore(path string) bool {
	for _, pattern := range i.patterns {
		if i.matchPattern(path, pattern) {
			return true
		}
	}
	return false
}

// matchPattern performs pattern matching for ignore rules
func (i *PathIgnorer) matchPattern(path, pattern string) bool {
	// Handle different pattern types

	// Exact match
	if path == pattern {
		return true
	}

	// Directory name matching (e.g., ".cache" matches any .cache directory)
	pathParts := strings.Split(path, string(filepath.Separator))
	for _, part := range pathParts {
		if part == pattern {
			return true
		}
	}

	// Wildcard matching
	if strings.Contains(pattern, "*") {
		matched, _ := filepath.Match(pattern, filepath.Base(path))
		if matched {
			return true
		}
		// Also try matching the full path
		matched, _ = filepath.Match(pattern, path)
		if matched {
			return true
		}
	}

	// Prefix matching
	if strings.HasPrefix(path, pattern) {
		return true
	}

	// Suffix matching
	if strings.HasSuffix(path, pattern) {
		return true
	}

	// Contains matching (for things like "node_modules")
	if strings.Contains(path, pattern) {
		return true
	}

	return false
}

// GetChangesByType returns changes grouped by type
func (r *Result) GetChangesByType() map[ChangeType][]string {
	changes := make(map[ChangeType][]string)

	for path := range r.Added {
		changes[ChangeAdded] = append(changes[ChangeAdded], path)
	}

	for path := range r.Modified {
		changes[ChangeModified] = append(changes[ChangeModified], path)
	}

	for path := range r.Deleted {
		changes[ChangeDeleted] = append(changes[ChangeDeleted], path)
	}

	// Sort for consistent output
	for _, paths := range changes {
		sort.Strings(paths)
	}

	return changes
}

// FilterChanges filters the diff result based on criteria
func (r *Result) FilterChanges(filter func(path string, changeType ChangeType) bool) *Result {
	filtered := &Result{
		Baseline:  r.Baseline,
		Current:   r.Current,
		Added:     make(map[string]*snapshot.FileRecord),
		Modified:  make(map[string]*ChangeDetail),
		Deleted:   make(map[string]*snapshot.FileRecord),
		Generated: r.Generated,
	}

	for path, record := range r.Added {
		if filter(path, ChangeAdded) {
			filtered.Added[path] = record
		}
	}

	for path, change := range r.Modified {
		if filter(path, ChangeModified) {
			filtered.Modified[path] = change
		}
	}

	for path, record := range r.Deleted {
		if filter(path, ChangeDeleted) {
			filtered.Deleted[path] = record
		}
	}

	// Recalculate summary
	filtered.Summary = Summary{
		AddedCount:    len(filtered.Added),
		ModifiedCount: len(filtered.Modified),
		DeletedCount:  len(filtered.Deleted),
		TotalChanges:  len(filtered.Added) + len(filtered.Modified) + len(filtered.Deleted),
	}

	return filtered
}

// ExportCSV exports the diff results to CSV format
func (r *Result) ExportCSV() [][]string {
	var rows [][]string

	// Header
	rows = append(rows, []string{
		"Path", "Type", "Size", "Mode", "ModTime", "Hash", "Changes",
	})

	// Added files
	for path, record := range r.Added {
		rows = append(rows, []string{
			path, "added", fmt.Sprintf("%d", record.Size),
			record.Mode.String(), record.ModTime.Format("2006-01-02 15:04:05"),
			record.Hash, "",
		})
	}

	// Modified files
	for path, change := range r.Modified {
		rows = append(rows, []string{
			path, "modified", fmt.Sprintf("%d", change.NewRecord.Size),
			change.NewRecord.Mode.String(), change.NewRecord.ModTime.Format("2006-01-02 15:04:05"),
			change.NewRecord.Hash, strings.Join(change.Changes, "; "),
		})
	}

	// Deleted files
	for path, record := range r.Deleted {
		rows = append(rows, []string{
			path, "deleted", fmt.Sprintf("%d", record.Size),
			record.Mode.String(), record.ModTime.Format("2006-01-02 15:04:05"),
			record.Hash, "",
		})
	}

	return rows
}

func maxin() {
	fmt.Printf("hi")
}
