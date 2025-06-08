//go:build windows

package system

import (
	"io/fs"
	"syscall"

	"golang.org/x/sys/windows"
)

func GetFileInfo(path string, info fs.FileInfo) *FileInfo {
	fi := &FileInfo{}

	// Permissions - map some file attributes to bits
	attr := uint32(0)
	winAttr := info.Sys().(*syscall.Win32FileAttributeData)

	if winAttr.FileAttributes&syscall.FILE_ATTRIBUTE_READONLY != 0 {
		attr |= 1 << 0
	}
	if winAttr.FileAttributes&syscall.FILE_ATTRIBUTE_HIDDEN != 0 {
		attr |= 1 << 1
	}
	if winAttr.FileAttributes&syscall.FILE_ATTRIBUTE_SYSTEM != 0 {
		attr |= 1 << 2
	}
	// You can map more attributes as needed...

	fi.Permissions = uint16(attr)

	// Get owner SID and group SID (hash them to uint32 for compactness)
	ownerSid, groupSid := getOwnerGroupSIDs(path)

	fi.OwnerID = sidToUint32(ownerSid)
	fi.GroupID = sidToUint32(groupSid)

	// Metadata is not supported on Windows in this example
	fi.Metadata = nil

	return fi
}

func getOwnerGroupSIDs(path string) (*windows.SID, *windows.SID) {
	// Open the file
	p, err := windows.UTF16PtrFromString(path)
	if err != nil {
		return nil, nil
	}

	var sd *windows.SECURITY_DESCRIPTOR
	err = windows.GetNamedSecurityInfo(
		p,
		windows.SE_FILE_OBJECT,
		windows.OWNER_SECURITY_INFORMATION|windows.GROUP_SECURITY_INFORMATION,
		nil,
		nil,
		nil,
		nil,
		&sd,
	)
	if err != nil {
		return nil, nil
	}

	var owner, group *windows.SID
	// Get owner SID
	err = windows.GetSecurityDescriptorOwner(sd, &owner, nil)
	if err != nil {
		owner = nil
	}

	// Get group SID
	err = windows.GetSecurityDescriptorGroup(sd, &group, nil)
	if err != nil {
		group = nil
	}

	return owner, group
}

// sidToUint32 hashes a SID to a uint32 value (not cryptographically secure, but consistent)
func sidToUint32(sid *windows.SID) uint32 {
	if sid == nil {
		return 0
	}
	data := sid.IdentifierAuthority().Value[:]
	for _, b := range sid.SubAuthority() {
		data = append(data, byte(b), byte(b>>8), byte(b>>16), byte(b>>24))
	}
	// simple XOR-based hash
	var h uint32
	for _, b := range data {
		h = (h << 5) - h + uint32(b)
	}
	return h
}
