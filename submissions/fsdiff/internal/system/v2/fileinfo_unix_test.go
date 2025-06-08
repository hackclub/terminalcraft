//go:build unix

package v2

import (
	"os"
	"testing"

	"github.com/stretchr/testify/require"
	"golang.org/x/sys/unix"
)

func TestGetFileInfo_Basic(t *testing.T) {
	tmp := t.TempDir()
	path := tmp + "/testfile"
	require.NoError(t, os.WriteFile(path, []byte("hi"), 0754))

	err := unix.Setxattr(path, "user.testattr", []byte("testvalue"), 0)
	require.NoError(t, err)

	info, err := os.Lstat(path)
	require.NoError(t, err)

	fi := GetFileInfo(path, info)

	require.Equal(t, uint16(0754), fi.Permissions&0777)
	require.NotZero(t, fi.OwnerID)
	require.NotZero(t, fi.GroupID)
	require.NotNil(t, fi.Metadata)
	require.Contains(t, fi.Metadata.Xattrs, "user.testattr")
	require.Equal(t, "testvalue", fi.Metadata.Xattrs["user.testattr"])
}

func TestGetFileInfo_EmptyXattrs(t *testing.T) {
	tmp := t.TempDir()
	path := tmp + "/plainfile"
	require.NoError(t, os.WriteFile(path, []byte("plain"), 0600))

	info, err := os.Lstat(path)
	require.NoError(t, err)

	fi := GetFileInfo(path, info)
	require.Equal(t, uint16(0600), fi.Permissions&0777)
	require.NotZero(t, fi.OwnerID)
	require.NotZero(t, fi.GroupID)
	require.Nil(t, fi.Metadata) // no xattrs or selinux
}

func TestGetFileInfo_SELinux_SkipIfNotPresent(t *testing.T) {
	tmp := t.TempDir()
	path := tmp + "/selinuxfile"
	require.NoError(t, os.WriteFile(path, []byte("a"), 0644))

	// Try to manually set a fake SELinux label (may fail without root)
	_ = unix.Setxattr(path, "security.selinux", []byte("system_u:object_r:tmp_t:s0"), 0)

	info, err := os.Lstat(path)
	require.NoError(t, err)

	fi := GetFileInfo(path, info)

	// Not all systems support SELinux — so we test presence *if available*
	if fi.Metadata != nil && fi.Metadata.SELinux != nil {
		require.Contains(t, fi.Metadata.SELinux["label"], ":")
	}
}
