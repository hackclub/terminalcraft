//go:build !windows
// +build !windows

package cmd

// hideFile for non‐Windows is a no‐op (it does nothing).
func hideFile(path string) error {
	return nil
}
