package report

import (
	"context"
	"fmt"
	"os"
	"sort"
	"time"

	"pkg.jsn.cam/jsn/cmd/fsdiff/internal/diff"
	"pkg.jsn.cam/jsn/cmd/fsdiff/internal/snapshot"
)

//go:generate go tool templ generate

// GenerateHTML creates a detailed HTML report of the differences using templ
func GenerateHTML(result *diff.Result, filename string) error {
	// Prepare data for template
	data := &HTMLReportData{
		Result:            result,
		GeneratedAt:       time.Now(),
		CriticalChanges:   result.GetCriticalChanges(),
		ChangesByType:     result.GetChangesByType(),
		TopLargestAdded:   getTopLargestAddedFiles(result.Added, 10),
		TopLargestDeleted: getTopLargestDeletedFiles(result.Deleted, 10),
	}

	// Create output file
	file, err := os.Create(filename)
	if err != nil {
		return fmt.Errorf("failed to create report file: %v", err)
	}
	defer file.Close()

	// Render template
	ctx := context.Background()
	if err := reportTemplate(data).Render(ctx, file); err != nil {
		return fmt.Errorf("failed to render template: %v", err)
	}

	return nil
}

// HTMLReportData contains all data needed for the HTML report
type HTMLReportData struct {
	Result            *diff.Result
	GeneratedAt       time.Time
	CriticalChanges   []diff.CriticalChange
	ChangesByType     map[diff.ChangeType][]string
	TopLargestAdded   []FileSize
	TopLargestDeleted []FileSize
}

// FileSize represents a file and its size for sorting
type FileSize struct {
	Path string
	Size int64
}

// getTopLargestAddedFiles returns the largest added files
func getTopLargestAddedFiles(files map[string]*snapshot.FileRecord, limit int) []FileSize {
	var fileSizes []FileSize
	for path, record := range files {
		fileSizes = append(fileSizes, FileSize{Path: path, Size: record.Size})
	}
	sort.Slice(fileSizes, func(i, j int) bool {
		return fileSizes[i].Size > fileSizes[j].Size
	})
	if len(fileSizes) > limit {
		fileSizes = fileSizes[:limit]
	}
	return fileSizes
}

// getTopLargestDeletedFiles returns the largest deleted files
func getTopLargestDeletedFiles(files map[string]*snapshot.FileRecord, limit int) []FileSize {
	var fileSizes []FileSize
	for path, record := range files {
		fileSizes = append(fileSizes, FileSize{Path: path, Size: record.Size})
	}
	sort.Slice(fileSizes, func(i, j int) bool {
		return fileSizes[i].Size > fileSizes[j].Size
	})
	if len(fileSizes) > limit {
		fileSizes = fileSizes[:limit]
	}
	return fileSizes
}

// Helper functions for template
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

func formatTime(t time.Time) string {
	return t.Format("2006-01-02 15:04:05")
}

func getChangeIcon(changeType diff.ChangeType) string {
	switch changeType {
	case diff.ChangeAdded:
		return "➕"
	case diff.ChangeModified:
		return "🔄"
	case diff.ChangeDeleted:
		return "❌"
	default:
		return "❓"
	}
}

func getSeverityColorClass(severity int) string {
	if severity >= 8 {
		return "text-red-600 font-bold"
	} else if severity >= 6 {
		return "text-orange-600 font-bold"
	} else if severity >= 4 {
		return "text-yellow-600 font-semibold"
	}
	return "text-green-600"
}

func truncateString(s string, length int) string {
	if len(s) <= length {
		return s
	}
	return s[:length] + "..."
}
