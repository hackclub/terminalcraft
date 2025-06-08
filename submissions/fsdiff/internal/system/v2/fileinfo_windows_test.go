//go:build windows

package system

import (
	"os"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestGetFileInfo_Windows(t *testing.T) {
	tmp := t.TempDir()
	path := tmp + `\testfile.txt`

	err := os.WriteFile(path, []byte("hello windows"), 0644)
	require.NoError(t, err)

	info, err := os.Lstat(path)
	require.NoError(t, err)

	fi := GetFileInfo(path, info)

	// Permissions should reflect readonly/hidden/system bits (or zero)
	require.LessOrEqual(t, fi.Permissions, uint16(7))

	// Owner and Group should not be zero (SIDs present)
	require.NotZero(t, fi.OwnerID)
	require.NotZero(t, fi.GroupID)

	// Metadata is nil for now
	require.Nil(t, fi.Metadata)
}
