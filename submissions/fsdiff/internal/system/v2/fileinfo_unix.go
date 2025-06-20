//go:build unix

package v2

import (
	"io/fs"
	"syscall"

	"golang.org/x/sys/unix"
)

func GetFileInfo(path string, info fs.FileInfo) *FileInfo {
	stat, ok := info.Sys().(*syscall.Stat_t)
	if !ok {
		return &FileInfo{}
	}

	perm := uint16(info.Mode().Perm() & 0777)
	special := uint16(info.Mode() & (fs.ModeSetuid | fs.ModeSetgid | fs.ModeSticky))

	meta := &FileMetadata{}

	// --- Get SELinux label ---
	label := getXattr(path, "security.selinux")
	if label != "" {
		meta.SELinux = map[string]string{"label": label}
	}

	// --- Get xattrs ---
	xattrs := make(map[string]string)
	if keys := listXattr(path); len(keys) > 0 {
		for _, key := range keys {
			if val := getXattr(path, key); val != "" {
				xattrs[key] = val
			}
		}
	}
	if len(xattrs) > 0 {
		meta.Xattrs = xattrs
	}

	// If nothing present, drop metadata to nil
	if meta.SELinux == nil && meta.Xattrs == nil {
		meta = nil
	}

	return &FileInfo{
		Permissions: perm | special,
		OwnerID:     stat.Uid,
		GroupID:     stat.Gid,
		Metadata:    meta,
	}
}

// getXattr fetches an extended attribute value as string
func getXattr(path, attr string) string {
	// First call to get size
	sz, err := unix.Getxattr(path, attr, nil)
	if err != nil || sz <= 0 {
		return ""
	}
	buf := make([]byte, sz)
	_, err = unix.Getxattr(path, attr, buf)
	if err != nil {
		return ""
	}
	return string(buf)
}

// listXattr returns a list of xattr keys
func listXattr(path string) []string {
	// First call to get size
	sz, err := unix.Listxattr(path, nil)
	if err != nil || sz <= 0 {
		return nil
	}
	buf := make([]byte, sz)
	sz, err = unix.Listxattr(path, buf)
	if err != nil || sz <= 0 {
		return nil
	}

	// Split null-delimited list
	var keys []string
	start := 0
	for i, b := range buf {
		if b == 0 {
			if i > start {
				keys = append(keys, string(buf[start:i]))
			}
			start = i + 1
		}
	}
	return keys
}
