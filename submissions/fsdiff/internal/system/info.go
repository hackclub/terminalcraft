package system

import (
	"os"
	"runtime"
	"strings"
	"time"
)

// SystemInfo contains metadata about the system when snapshot was taken
type SystemInfo struct {
	Timestamp    time.Time     `json:"timestamp"`
	Hostname     string        `json:"hostname"`
	OS           string        `json:"os"`
	Arch         string        `json:"arch"`
	Distro       string        `json:"distro"`
	KernelVer    string        `json:"kernel_version"`
	ScanRoot     string        `json:"scan_root"`
	GoVersion    string        `json:"go_version"`
	ScanDuration time.Duration `json:"scan_duration"`
	CPUCount     int           `json:"cpu_count"`
}

func (s *SystemInfo) String() string {
	return strings.Join([]string{
		"Hostname: " + s.Hostname,
		"OS: " + s.OS,
		"Arch: " + s.Arch,
		"Distro: " + s.Distro,
		"Kernel Version: " + s.KernelVer,
		"Timestamp: " + s.Timestamp.Format(time.RFC3339),
		"Scan Root: " + s.ScanRoot,
	}, "\n")
}

// GetSystemInfo gathers comprehensive system metadata
func GetSystemInfo(scanRoot string) SystemInfo {
	hostname, _ := os.Hostname()

	return SystemInfo{
		Hostname:  hostname,
		OS:        runtime.GOOS,
		Arch:      runtime.GOARCH,
		Distro:    detectDistro(),
		KernelVer: getKernelVersion(),
		Timestamp: time.Now(),
		ScanRoot:  scanRoot,
		CPUCount:  runtime.NumCPU(),
		GoVersion: runtime.Version(),
	}
}

// detectDistro attempts to detect the Linux distribution
func detectDistro() string {
	// Try /etc/os-release first (standard)
	if data, err := os.ReadFile("/etc/os-release"); err == nil {
		lines := strings.Split(string(data), "\n")
		for _, line := range lines {
			if strings.HasPrefix(line, "PRETTY_NAME=") {
				value := strings.Split(line, "=")[1]
				return strings.Trim(value, "\"")
			}
		}
		// Fallback to NAME if PRETTY_NAME not found
		for _, line := range lines {
			if strings.HasPrefix(line, "NAME=") {
				value := strings.Split(line, "=")[1]
				return strings.Trim(value, "\"")
			}
		}
	}

	// Try other common files
	distroFiles := map[string]string{
		"/etc/redhat-release": "Red Hat",
		"/etc/debian_version": "Debian",
		"/etc/ubuntu_version": "Ubuntu",
		"/etc/centos-release": "CentOS",
		"/etc/fedora-release": "Fedora",
		"/etc/arch-release":   "Arch Linux",
		"/etc/alpine-release": "Alpine Linux",
	}

	for file, distro := range distroFiles {
		if _, err := os.Stat(file); err == nil {
			if data, err := os.ReadFile(file); err == nil {
				content := strings.TrimSpace(string(data))
				if content != "" {
					return distro + " (" + content + ")"
				}
				return distro
			}
			return distro
		}
	}

	// Fallback based on OS
	switch runtime.GOOS {
	case "linux":
		return "Linux (unknown distribution)"
	case "darwin":
		return "macOS"
	case "windows":
		return "Windows"
	case "freebsd":
		return "FreeBSD"
	case "openbsd":
		return "OpenBSD"
	case "netbsd":
		return "NetBSD"
	default:
		return runtime.GOOS
	}
}

// getKernelVersion attempts to get the kernel version
func getKernelVersion() string {
	switch runtime.GOOS {
	case "linux":
		// Try /proc/version
		if data, err := os.ReadFile("/proc/version"); err == nil {
			parts := strings.Split(string(data), " ")
			if len(parts) >= 3 {
				return parts[2]
			}
		}

		// Try uname via /proc/sys/kernel/osrelease
		if data, err := os.ReadFile("/proc/sys/kernel/osrelease"); err == nil {
			return strings.TrimSpace(string(data))
		}

	case "darwin":
		// Try to get macOS version
		if data, err := os.ReadFile("/System/Library/CoreServices/SystemVersion.plist"); err == nil {
			content := string(data)
			if idx := strings.Index(content, "<key>ProductVersion</key>"); idx != -1 {
				start := strings.Index(content[idx:], "<string>") + idx + 8
				end := strings.Index(content[start:], "</string>") + start
				if start > idx && end > start {
					return content[start:end]
				}
			}
		}

	case "windows":
		// Windows version detection would require more complex logic
		return "Windows"
	}

	return "unknown"
}
