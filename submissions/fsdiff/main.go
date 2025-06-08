package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"os"
	"runtime"
	"strings"

	"pkg.jsn.cam/jsn/cmd/fsdiff/pkg/fsdiff"

	"pkg.jsn.cam/jsn/cmd/fsdiff/internal/diff"
	"pkg.jsn.cam/jsn/cmd/fsdiff/internal/report"
	"pkg.jsn.cam/jsn/cmd/fsdiff/internal/scanner"
	"pkg.jsn.cam/jsn/cmd/fsdiff/internal/snapshot"

	_ "net/http/pprof"
)

var (
	workers = flag.Int("workers", runtime.NumCPU()*2, "Number of worker goroutines")
	verbose = flag.Bool("v", true, "Verbose output")
	debug   = flag.Bool("d", false, "Enable pprof profiling on port 6060")
	ignore  = flag.String("ignore", "", "Comma-separated list of paths/patterns to ignore (e.g., '.cache,node_modules,*.log')")
)

func main() {
	flag.Parse()

	if len(flag.Args()) < 1 {
		printUsage()
		os.Exit(1)
	}

	if *debug {
		go func() {
			log.Println(http.ListenAndServe("localhost:6060", nil)) // Starts pprof server
		}()
	}

	command := flag.Args()[0]

	switch command {
	case "snapshot":
		handleSnapshot()
	case "diff":
		handleDiff()
	case "live":
		handleLive()
	case "version":
		fmt.Printf("fsdiff version %s\n", fsdiff.Version)
	default:
		fmt.Printf("Unknown command: %s\n", command)
		printUsage()
		os.Exit(1)
	}
}

func printUsage() {
	fmt.Printf("Filesystem Diff Tool v%s\n\n", fsdiff.Version)
	fmt.Println("USAGE:")
	fmt.Println("  fsdiff [options] <command> [args...]")
	fmt.Println("")
	fmt.Println("COMMANDS:")
	fmt.Println("  snapshot <root_path> <output_file>    Create filesystem snapshot")
	fmt.Println("  diff <baseline> <current> [report]    Compare two snapshots")
	fmt.Println("  live <baseline> <root_path> [report]  Compare baseline to live filesystem")
	fmt.Println("  version                               Show version information")
	fmt.Println("")
	fmt.Println("OPTIONS:")
	fmt.Printf("  -workers int    Number of parallel workers (default: %d)\n", runtime.NumCPU()*2)
	fmt.Println("  -v              Verbose output")
	fmt.Println("  -d              Enable pprof profiling on port 6060")
	fmt.Println("  -ignore string  Comma-separated ignore patterns (e.g., '.cache,*.tmp')")
	fmt.Println("")
	fmt.Println("EXAMPLES:")
	fmt.Println("  fsdiff snapshot / baseline.snap")
	fmt.Println("  fsdiff diff baseline.snap current.snap changes.html")
	fmt.Println("  fsdiff -ignore '.cache,node_modules' live baseline.snap /")
	fmt.Println("  fsdiff -workers 8 -v snapshot /home/user user-snapshot.snap")
}

func handleSnapshot() {
	args := flag.Args()[1:]
	if len(args) != 2 {
		fmt.Println("Usage: fsdiff snapshot <root_path> <output_file>")
		os.Exit(1)
	}

	rootPath := args[0]
	outputFile := args[1]

	// Parse ignore patterns
	ignorePatterns := parseIgnorePatterns(*ignore)

	// Create scanner with configuration
	config := &scanner.Config{
		Workers:        *workers,
		Verbose:        *verbose,
		IgnorePatterns: ignorePatterns,
	}

	fmt.Printf("🔍 Scanning filesystem: %s\n", rootPath)
	fmt.Printf("⚙️  Using %d workers\n", *workers)
	if len(ignorePatterns) > 0 {
		fmt.Printf("🚫 Ignoring patterns: %s\n", strings.Join(ignorePatterns, ", "))
	}

	s := scanner.New(config)
	snap, err := s.ScanFilesystem(rootPath)
	if err != nil {
		fmt.Printf("❌ Error scanning filesystem: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("💾 Saving snapshot to: %s\n", outputFile)
	if err := snapshot.Save(snap, outputFile); err != nil {
		fmt.Printf("❌ Error saving snapshot: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("✅ Snapshot created successfully!\n")
	fmt.Printf("   Files: %d, Directories: %d\n", snap.Stats.FileCount, snap.Stats.DirCount)
	fmt.Printf("   Size: %s, Duration: %v\n", formatBytes(snap.Stats.TotalSize), snap.Stats.ScanDuration)
}

func handleDiff() {
	args := flag.Args()[1:]
	if len(args) < 2 || len(args) > 3 {
		fmt.Println("Usage: fsdiff diff <baseline> <current> [report_file]")
		os.Exit(1)
	}

	baselineFile := args[0]
	currentFile := args[1]
	reportFile := ""
	if len(args) == 3 {
		reportFile = args[2]
	}

	// Parse ignore patterns for diff
	ignorePatterns := parseIgnorePatterns(*ignore)

	fmt.Printf("📖 Loading baseline: %s\n", baselineFile)
	baseline, err := snapshot.Load(baselineFile)
	if err != nil {
		fmt.Printf("❌ Error loading baseline: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("📖 Loading current: %s\n", currentFile)
	current, err := snapshot.Load(currentFile)
	if err != nil {
		fmt.Printf("❌ Error loading current snapshot: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("🔍 Comparing snapshots...\n")
	config := &diff.Config{
		IgnorePatterns: ignorePatterns,
		Verbose:        *verbose,
	}

	d := diff.New(config)
	result := d.Compare(baseline, current)

	// Print summary
	printDiffSummary(result)

	// Generate report if requested
	if reportFile != "" {
		fmt.Printf("📄 Generating report: %s\n", reportFile)
		if err := report.GenerateHTML(result, reportFile); err != nil {
			fmt.Printf("❌ Error generating report: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("✅ Report saved successfully!\n")
	}
}

func handleLive() {
	args := flag.Args()[1:]
	if len(args) < 2 || len(args) > 3 {
		fmt.Println("Usage: fsdiff live <baseline> <root_path> [report_file]")
		os.Exit(1)
	}

	baselineFile := args[0]
	rootPath := args[1]
	reportFile := ""
	if len(args) == 3 {
		reportFile = args[2]
	}

	// Parse ignore patterns
	ignorePatterns := parseIgnorePatterns(*ignore)

	fmt.Printf("📖 Loading baseline: %s\n", baselineFile)
	baseline, err := snapshot.Load(baselineFile)
	if err != nil {
		fmt.Printf("❌ Error loading baseline: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("🔍 Scanning current filesystem: %s\n", rootPath)
	scanConfig := &scanner.Config{
		Workers:        *workers,
		Verbose:        *verbose,
		IgnorePatterns: ignorePatterns,
	}

	s := scanner.New(scanConfig)
	current, err := s.ScanFilesystem(rootPath)
	if err != nil {
		fmt.Printf("❌ Error scanning filesystem: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("🔍 Comparing with baseline...\n")
	diffConfig := &diff.Config{
		IgnorePatterns: ignorePatterns,
		Verbose:        *verbose,
	}

	d := diff.New(diffConfig)
	result := d.Compare(baseline, current)

	// Print summary
	printDiffSummary(result)

	// Generate report if requested
	if reportFile != "" {
		fmt.Printf("📄 Generating report: %s\n", reportFile)
		if err := report.GenerateHTML(result, reportFile); err != nil {
			fmt.Printf("❌ Error generating report: %v\n", err)
			os.Exit(1)
		}
		fmt.Printf("✅ Report saved successfully!\n")
	}
}

func parseIgnorePatterns(ignore string) []string {
	if ignore == "" {
		return nil
	}
	patterns := strings.Split(ignore, ",")
	result := make([]string, 0, len(patterns))
	for _, pattern := range patterns {
		pattern = strings.TrimSpace(pattern)
		if pattern != "" {
			result = append(result, pattern)
		}
	}
	return result
}

func printDiffSummary(result *diff.Result) {
	fmt.Println("\n" + strings.Repeat("=", 60))
	fmt.Println("📊 FILESYSTEM DIFF SUMMARY")
	fmt.Println(strings.Repeat("=", 60))

	fmt.Printf("Baseline: %s (%s) - %s\n",
		result.Baseline.SystemInfo.Hostname,
		result.Baseline.SystemInfo.Distro,
		result.Baseline.SystemInfo.Timestamp.Format("2006-01-02 15:04:05"))

	fmt.Printf("Current:  %s (%s) - %s\n\n",
		result.Current.SystemInfo.Hostname,
		result.Current.SystemInfo.Distro,
		result.Current.SystemInfo.Timestamp.Format("2006-01-02 15:04:05"))

	summary := result.Summary
	fmt.Printf("📈 CHANGES:\n")
	fmt.Printf("   Added:    %d files/directories\n", summary.AddedCount)
	fmt.Printf("   Modified: %d files/directories\n", summary.ModifiedCount)
	fmt.Printf("   Deleted:  %d files/directories\n", summary.DeletedCount)
	fmt.Printf("   Total:    %d changes\n\n", summary.TotalChanges)

	if summary.TotalChanges == 0 {
		fmt.Println("✅ No changes detected!")
		return
	}

	// Show critical changes (common attack indicators)
	criticalChanges := findCriticalChanges(result)
	if len(criticalChanges) > 0 {
		fmt.Printf("🚨 CRITICAL CHANGES:\n")
		for _, change := range criticalChanges {
			fmt.Printf("   %s %s\n", change.Type, change.Path)
		}
		fmt.Println()
	}

	// Show sample of changes
	showSampleChanges("Added", result.Added, 5)
	showSampleChanges("Modified", result.Modified, 5)
	showSampleChanges("Deleted", result.Deleted, 5)
}

type CriticalChange struct {
	Type string
	Path string
}

func findCriticalChanges(result *diff.Result) []CriticalChange {
	var critical []CriticalChange

	criticalPaths := []string{
		"/etc/passwd", "/etc/shadow", "/etc/sudoers",
		"/bin/", "/sbin/", "/usr/bin/", "/usr/sbin/",
		"/boot/", "/etc/systemd/", "/etc/cron",
		"/.ssh/", "/root/", "/home/",
	}

	checkCritical := func(path, changeType string) {
		for _, critPath := range criticalPaths {
			if strings.Contains(path, critPath) {
				critical = append(critical, CriticalChange{
					Type: changeType,
					Path: path,
				})
				break
			}
		}
	}

	for path := range result.Added {
		checkCritical(path, "ADDED")
	}
	for path := range result.Modified {
		checkCritical(path, "MODIFIED")
	}
	for path := range result.Deleted {
		checkCritical(path, "DELETED")
	}

	return critical
}

func showSampleChanges(changeType string, changes interface{}, limit int) {
	var count int
	var paths []string

	// Handle different types of change maps
	switch c := changes.(type) {
	case map[string]*snapshot.FileRecord:
		count = len(c)
		for path := range c {
			paths = append(paths, path)
			if len(paths) >= limit {
				break
			}
		}
	case map[string]*diff.ChangeDetail:
		count = len(c)
		for path := range c {
			paths = append(paths, path)
			if len(paths) >= limit {
				break
			}
		}
	default:
		return // Unknown type
	}

	if count == 0 {
		return
	}

	fmt.Printf("📁 %s (%d total):\n", changeType, count)
	for i, path := range paths {
		if i >= limit {
			fmt.Printf("   ... and %d more\n", count-limit)
			break
		}
		icon := getChangeIcon(changeType)
		fmt.Printf("   %s %s\n", icon, path)
	}
	fmt.Println()
}

func getChangeIcon(changeType string) string {
	switch changeType {
	case "Added":
		return "+"
	case "Modified":
		return "~"
	case "Deleted":
		return "-"
	default:
		return "?"
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
