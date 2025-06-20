package diff

import (
	"path/filepath"
	"sort"
	"strings"
)

// === MATCHER HELPER FUNCTIONS ===

func pathExactMatch(target string) func(string) bool {
	return func(path string) bool {
		return path == target
	}
}

func pathExactAny(targets ...string) func(string) bool {
	return func(path string) bool {
		for _, target := range targets {
			if path == target {
				return true
			}
		}
		return false
	}
}

func pathPrefixMatch(prefix string) func(string) bool {
	return func(path string) bool {
		return strings.HasPrefix(path, prefix)
	}
}

func pathPrefixAny(prefixes ...string) func(string) bool {
	return func(path string) bool {
		for _, prefix := range prefixes {
			if strings.HasPrefix(path, prefix) {
				return true
			}
		}
		return false
	}
}

func pathSuffixMatch(suffix string) func(string) bool {
	return func(path string) bool {
		return strings.HasSuffix(path, suffix)
	}
}

func pathContainsMatch(substring string) func(string) bool {
	return func(path string) bool {
		return strings.Contains(path, substring)
	}
}

func pathContainsAny(substrings ...string) func(string) bool {
	return func(path string) bool {
		for _, substring := range substrings {
			if strings.Contains(path, substring) {
				return true
			}
		}
		return false
	}
}

func pathMatchesAny(patterns ...string) func(string) bool {
	return func(path string) bool {
		for _, pattern := range patterns {
			if matched, _ := filepath.Match(pattern, path); matched {
				return true
			}
			if matched, _ := filepath.Match(pattern, filepath.Base(path)); matched {
				return true
			}
		}
		return false
	}
}

// === MAIN ANALYSIS FUNCTION ===

// GetCriticalChanges analyzes a diff result for critical changes
func (r *Result) GetCriticalChanges() []CriticalChange {
	var critical []CriticalChange
	rules := GetCriticalityRules()

	// Check added files
	for path, record := range r.Added {
		for _, rule := range rules {
			if rule.Matcher(path) {
				if severity, exists := rule.Severity[ChangeAdded]; exists {
					critical = append(critical, CriticalChange{
						Path:     path,
						Type:     ChangeAdded,
						Record:   record,
						Severity: severity,
						Reason:   rule.Description,
						Category: rule.Category,
					})
				}
				break // Only match first rule for each file
			}
		}
	}

	// Check modified files
	for path, change := range r.Modified {
		for _, rule := range rules {
			if rule.Matcher(path) {
				if severity, exists := rule.Severity[ChangeModified]; exists {
					critical = append(critical, CriticalChange{
						Path:     path,
						Type:     ChangeModified,
						Record:   change.NewRecord,
						Severity: severity,
						Reason:   rule.Description,
						Category: rule.Category,
					})
				}
				break // Only match first rule for each file
			}
		}
	}

	// Check deleted files
	for path, record := range r.Deleted {
		for _, rule := range rules {
			if rule.Matcher(path) {
				if severity, exists := rule.Severity[ChangeDeleted]; exists {
					critical = append(critical, CriticalChange{
						Path:     path,
						Type:     ChangeDeleted,
						Record:   record,
						Severity: severity,
						Reason:   rule.Description,
						Category: rule.Category,
					})
				}
				break // Only match first rule for each file
			}
		}
	}

	// Sort by severity (highest first)
	sort.Slice(critical, func(i, j int) bool {
		return critical[i].Severity > critical[j].Severity
	})

	return critical
}

// GetCriticalChangesByCategory returns critical changes filtered by category
func (r *Result) GetCriticalChangesByCategory(category string) []CriticalChange {
	allCritical := r.GetCriticalChanges()
	var filtered []CriticalChange

	for _, change := range allCritical {
		if change.Category == category {
			filtered = append(filtered, change)
		}
	}

	return filtered
}

// GetCriticalChangesBySeverity returns critical changes above a minimum severity
func (r *Result) GetCriticalChangesBySeverity(minSeverity int) []CriticalChange {
	allCritical := r.GetCriticalChanges()
	var filtered []CriticalChange

	for _, change := range allCritical {
		if change.Severity >= minSeverity {
			filtered = append(filtered, change)
		}
	}

	return filtered
}

// GetSecurityCriticalChanges returns only security-related critical changes
func (r *Result) GetSecurityCriticalChanges() []CriticalChange {
	securityCategories := []string{
		"authentication", "authorization", "remote-access",
		"privileged-access", "access-control", "network-security",
	}

	allCritical := r.GetCriticalChanges()
	var filtered []CriticalChange

	for _, change := range allCritical {
		for _, category := range securityCategories {
			if change.Category == category {
				filtered = append(filtered, change)
				break
			}
		}
	}

	return filtered
}
