//go:build windows
// +build windows

package cmd

import (
	"syscall"
)

// hideFile for Windows uses SetFileAttributes to mark a directory as hidden.
func hideFile(path string) error {
	ptr, err := syscall.UTF16PtrFromString(path)
	if err != nil {
		return err
	}
	// FILE_ATTRIBUTE_HIDDEN = 0x02
	return syscall.SetFileAttributes(ptr, syscall.FILE_ATTRIBUTE_HIDDEN)
}
