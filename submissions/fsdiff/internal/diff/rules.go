package diff

import (
	"pkg.jsn.cam/jsn/cmd/fsdiff/internal/snapshot"
)

// CriticalChange represents a security-relevant change
type CriticalChange struct {
	Record   *snapshot.FileRecord `json:"record"`
	Path     string               `json:"path"`
	Type     ChangeType           `json:"type"`
	Reason   string               `json:"reason"`
	Category string               `json:"category"`
	Severity int                  `json:"severity"` // 1-10 scale
}

// CriticalityRule defines how to detect and score critical changes
type CriticalityRule struct {
	Matcher     func(path string) bool
	Severity    map[ChangeType]int
	Name        string
	Category    string
	Description string
}

// GetCriticalityRules returns all hardcoded criticality rules
// Edit this function to add/modify/remove rules
func GetCriticalityRules() []CriticalityRule {
	return []CriticalityRule{
		// === AUTHENTICATION & AUTHORIZATION ===
		{
			Name:        "user-accounts",
			Category:    "authentication",
			Description: "User account database modified",
			Matcher:     pathExactMatch("/etc/passwd"),
			Severity:    map[ChangeType]int{ChangeAdded: 10, ChangeModified: 10, ChangeDeleted: 10},
		},
		{
			Name:        "password-hashes",
			Category:    "authentication",
			Description: "Password hash database modified",
			Matcher:     pathExactMatch("/etc/shadow"),
			Severity:    map[ChangeType]int{ChangeAdded: 10, ChangeModified: 10, ChangeDeleted: 9},
		},
		{
			Name:        "sudo-config",
			Category:    "authorization",
			Description: "Sudo privileges configuration modified",
			Matcher:     pathExactMatch("/etc/sudoers"),
			Severity:    map[ChangeType]int{ChangeAdded: 10, ChangeModified: 10, ChangeDeleted: 9},
		},
		{
			Name:        "group-membership",
			Category:    "authentication",
			Description: "Group membership database modified",
			Matcher:     pathExactMatch("/etc/group"),
			Severity:    map[ChangeType]int{ChangeAdded: 8, ChangeModified: 8, ChangeDeleted: 7},
		},

		// === SYSTEM BINARIES ===
		{
			Name:        "system-binaries",
			Category:    "system-integrity",
			Description: "Critical system binary modified",
			Matcher:     pathPrefixAny("/bin/", "/sbin/", "/usr/bin/", "/usr/sbin/"),
			Severity:    map[ChangeType]int{ChangeAdded: 8, ChangeModified: 9, ChangeDeleted: 7},
		},
		{
			Name:        "boot-binaries",
			Category:    "boot-security",
			Description: "Boot-related binary modified",
			Matcher:     pathPrefixMatch("/boot/"),
			Severity:    map[ChangeType]int{ChangeAdded: 9, ChangeModified: 9, ChangeDeleted: 8},
		},

		// === SSH & REMOTE ACCESS ===
		{
			Name:        "ssh-keys",
			Category:    "remote-access",
			Description: "SSH keys or configuration modified",
			Matcher:     pathContainsAny("/.ssh/", "/etc/ssh/"),
			Severity:    map[ChangeType]int{ChangeAdded: 8, ChangeModified: 8, ChangeDeleted: 7},
		},
		{
			Name:        "ssh-host-keys",
			Category:    "remote-access",
			Description: "SSH host keys modified",
			Matcher:     pathMatchesAny("/etc/ssh/ssh_host_*"),
			Severity:    map[ChangeType]int{ChangeAdded: 9, ChangeModified: 9, ChangeDeleted: 8},
		},

		// === SYSTEM SERVICES ===
		{
			Name:        "systemd-services",
			Category:    "service-management",
			Description: "Systemd service configuration modified",
			Matcher:     pathPrefixAny("/etc/systemd/", "/lib/systemd/", "/usr/lib/systemd/"),
			Severity:    map[ChangeType]int{ChangeAdded: 6, ChangeModified: 7, ChangeDeleted: 5},
		},
		{
			Name:        "init-scripts",
			Category:    "service-management",
			Description: "System initialization script modified",
			Matcher:     pathPrefixMatch("/etc/init.d/"),
			Severity:    map[ChangeType]int{ChangeAdded: 7, ChangeModified: 7, ChangeDeleted: 6},
		},

		// === SCHEDULED TASKS ===
		{
			Name:        "cron-system",
			Category:    "scheduled-tasks",
			Description: "System cron configuration modified",
			Matcher:     pathPrefixAny("/etc/cron", "/var/spool/cron/"),
			Severity:    map[ChangeType]int{ChangeAdded: 7, ChangeModified: 7, ChangeDeleted: 6},
		},
		{
			Name:        "crontab-files",
			Category:    "scheduled-tasks",
			Description: "Crontab file modified",
			Matcher:     pathSuffixMatch("crontab"),
			Severity:    map[ChangeType]int{ChangeAdded: 8, ChangeModified: 8, ChangeDeleted: 7},
		},

		// === PRIVILEGED ACCESS ===
		{
			Name:        "root-directory",
			Category:    "privileged-access",
			Description: "Root user directory modified",
			Matcher:     pathPrefixMatch("/root/"),
			Severity:    map[ChangeType]int{ChangeAdded: 8, ChangeModified: 8, ChangeDeleted: 7},
		},
		{
			Name:        "root-profile",
			Category:    "privileged-access",
			Description: "Root user profile modified",
			Matcher:     pathExactAny("/root/.bashrc", "/root/.profile", "/root/.bash_profile"),
			Severity:    map[ChangeType]int{ChangeAdded: 9, ChangeModified: 9, ChangeDeleted: 8},
		},

		// === SECURITY CONFIGURATION ===
		{
			Name:        "pam-config",
			Category:    "access-control",
			Description: "PAM authentication configuration modified",
			Matcher:     pathPrefixMatch("/etc/pam.d/"),
			Severity:    map[ChangeType]int{ChangeAdded: 7, ChangeModified: 8, ChangeDeleted: 6},
		},
		{
			Name:        "security-limits",
			Category:    "access-control",
			Description: "Security limits configuration modified",
			Matcher:     pathPrefixMatch("/etc/security/"),
			Severity:    map[ChangeType]int{ChangeAdded: 6, ChangeModified: 7, ChangeDeleted: 5},
		},

		// === NETWORK CONFIGURATION ===
		{
			Name:        "hosts-file",
			Category:    "network-security",
			Description: "System hosts file modified",
			Matcher:     pathExactMatch("/etc/hosts"),
			Severity:    map[ChangeType]int{ChangeAdded: 6, ChangeModified: 6, ChangeDeleted: 5},
		},
		{
			Name:        "dns-config",
			Category:    "network-security",
			Description: "DNS configuration modified",
			Matcher:     pathExactMatch("/etc/resolv.conf"),
			Severity:    map[ChangeType]int{ChangeAdded: 5, ChangeModified: 6, ChangeDeleted: 5},
		},
		{
			Name:        "network-interfaces",
			Category:    "network-security",
			Description: "Network interface configuration modified",
			Matcher:     pathPrefixMatch("/etc/network/"),
			Severity:    map[ChangeType]int{ChangeAdded: 5, ChangeModified: 6, ChangeDeleted: 5},
		},

		// === PACKAGE MANAGEMENT ===
		{
			Name:        "apt-config",
			Category:    "package-security",
			Description: "APT package manager configuration modified",
			Matcher:     pathPrefixMatch("/etc/apt/"),
			Severity:    map[ChangeType]int{ChangeAdded: 4, ChangeModified: 5, ChangeDeleted: 4},
		},
		{
			Name:        "yum-config",
			Category:    "package-security",
			Description: "YUM package manager configuration modified",
			Matcher:     pathPrefixAny("/etc/yum/", "/etc/yum.conf"),
			Severity:    map[ChangeType]int{ChangeAdded: 4, ChangeModified: 5, ChangeDeleted: 4},
		},

		// === KERNEL & MODULES ===
		{
			Name:        "kernel-modules",
			Category:    "kernel-security",
			Description: "Kernel module configuration modified",
			Matcher:     pathPrefixAny("/etc/modules", "/etc/modprobe"),
			Severity:    map[ChangeType]int{ChangeAdded: 7, ChangeModified: 8, ChangeDeleted: 6},
		},
		{
			Name:        "sysctl-config",
			Category:    "kernel-security",
			Description: "Kernel parameter configuration modified",
			Matcher:     pathContainsMatch("sysctl"),
			Severity:    map[ChangeType]int{ChangeAdded: 6, ChangeModified: 7, ChangeDeleted: 5},
		},

		// === APPLICATION SPECIFIC ===
		{
			Name:        "web-server-config",
			Category:    "application-security",
			Description: "Web server configuration modified",
			Matcher:     pathPrefixAny("/etc/apache2/", "/etc/nginx/", "/etc/httpd/"),
			Severity:    map[ChangeType]int{ChangeAdded: 5, ChangeModified: 6, ChangeDeleted: 4},
		},
		{
			Name:        "database-config",
			Category:    "application-security",
			Description: "Database configuration modified",
			Matcher:     pathPrefixAny("/etc/mysql/", "/etc/postgresql/", "/var/lib/mysql/", "/var/lib/postgresql/"),
			Severity:    map[ChangeType]int{ChangeAdded: 6, ChangeModified: 7, ChangeDeleted: 5},
		},
	}
}
