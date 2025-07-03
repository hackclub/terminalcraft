#!/usr/bin/env lua
if not arg[1] then
	print("OCConfigReader <path/to/config.plist>")
	os.exit(1)
end

local f = io.open(arg[1])
if not f then
	print("Failed to open file (Wrong path?)")
	os.exit(1)
end
local data = f:read("a")
f:close()

local parse = require "floxlist"
local plist = parse(data)

local detected = true

local function check(text)
	print(text)
	detected = true
end

local function section()
	if detected then
		detected = false
		print()
	end
end

local bootarg = plist.NVRAM.Add["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["boot-args"]
local ssdts = {}
local ssdtalt = {}
local drivers = {}
local driversalt = {}
local kexts = {}
local kextsalt = {}
local tools = {}

local function kitchensinked(...)
	local tocheck = {...}
	for k, v in pairs(tocheck) do
		local match = table.concat(kextsalt, " "):match(v)
		if not match then -- Allows rough match
			return
		end
		tocheck[k] = match -- Make sure to use the regex result
	end
	check(table.concat(tocheck, ", ").." are all present")
end
local function kitchensinkedwithmsg(msg, ...) -- MONOSODIUM GLUTAMATE!!!
	local tocheck = {...}
	for k, v in pairs(tocheck) do
		local match = table.concat(kextsalt, " "):match(v)
		if not match then -- Allows rough match
			return
		end
		tocheck[k] = match -- Make sure to use the regex result
	end
	check(msg)
end

for _, v in pairs(plist.ACPI.Add) do
	ssdts[v.Path:match("(.+).aml")] = true
	table.insert(ssdtalt, v.Path:match("(.+).aml"))
end

for _, v in pairs(plist.UEFI.Drivers) do
	drivers[v.Path:match("(.+).efi")] = true
	table.insert(driversalt, v.Path:match("(.+).efi"))
end

for _, v in pairs(plist.Kernel.Add) do
	kexts[v.BundlePath:match("(.+).kext")] = v
	table.insert(kextsalt, v.BundlePath:match("(.+).kext"))
end

for _, v in pairs(plist.Misc.Tools) do
	tools[v.Name:match("(.+).efi")] = true
end

section() -- Info, nothing too bad

check "Kexts:"
for i = 1, #kextsalt, 2 do
	check(kextsalt[i].." "..(kextsalt[i+1] or ""))
end

check "\nSSDTs:"
for i = 1, #ssdtalt, 2 do
	check(ssdtalt[i].." "..(ssdtalt[i+1] or ""))
end

check "\nDrivers:"
for i = 1, #driversalt, 2 do
	check(driversalt[i].." "..(driversalt[i+1] or ""))
end
check("")

for _, v in pairs(plist.Kernel.Patch) do
	if v.Comment:match("AuthenticAMD") then
		check "This is an AMD machine"
		break
	end
end

if bootarg:match("nvme=-1") then
	check "NVME is disabled"
end

if bootarg:match("-[ri][ag][df]x?vesa") or bootarg:match("nv_disable=1") then -- Super awful, but this means igfx or rad
	check "One or more VESA arg is enabled"
end

if drivers["OpenCanopy.efi"] then
	check "OpenCanopy is present (should be post-install stuff)"
end

check("SecureBootModel is "..plist.Misc.Security.SecureBootModel)
check("SMBIOS is "..plist.PlatformInfo.Generic.SystemProductName)
if plist.Misc.Security.ScanPolicy ~= 0 then
	check("ScanPolicy is set to "..plist.Misc.Security.ScanPolicy.." (can be normal)")
end

section() -- Oddness/not advisable

local badkexts = {"USBPorts", "UTBDefault", "USBInjectAll", "(IO80211[a-zA-Z0-9]+) "}

local matches = {}
for _, v in pairs(badkexts) do
	local match = table.concat(kextsalt, " "):match(v)
	if match then
		table.insert(matches, match)
	end
end
if matches[1] then
	check("Detected "..table.concat(matches, ", "))
end

if #plist.Misc.Tools > 10 then
	check "More than 10 tools detected"
end

if ssdts["SSDT-WIFI"] then
	check "SSDT-WIFI is present"
end

if plist.NVRAM.Add["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["csr-active-config"] == "030A0000" then
	check "SIP is disabled" -- Nobody would disable the entire SIP over filesystem and kext signing, and OpCore Simplify already uses weird value, so...
end

if bootarg:match("-v$") or bootarg:match("-v ") then
	if not bootarg:match("keepsyms=1") then
		check "Verbose is enabled, but keepsyms is absent"
	end
	if not bootarg:match("debug=0x") and not plist.Kernel.Quirks.LapicKernelPanic then
		check "Verbose is enabled, but debug=0x argument nor LapicKernelPanic is present"
	end
end

if bootarg:match("-no_compat_check") then
	check "SMBIOS compatibility check is disabled"
end

if drivers.OpenHfsPlus then
	check "OpenHfsPlus is being used"
end

if tools.CleanNvram then
	check "CleanNvram is being used"
end

section() -- Actual issues

if #plist.UEFI.Drivers > 40 then
	check "More than 40 drivers detected"
end

if table.concat(driversalt):match("Hfs.+Hfs") then
	check "More than 2 HFS+ drivers exists"
end

kitchensinked("IntelMausi", "IntelSnowMausi")
kitchensinked("AppleALC", "AppleALCU")
kitchensinked("WhateverGreen", "Noot[ed]*R[Xed]*") -- Hacky, but it detects both
kitchensinked("BrcmPatchRAM2", "BrcmPatchRAM3") -- Having those two already tells it well
kitchensinked("IntelBluetoothFirmware", "BrcmPatchRAM[1-3]?") -- If BrcmPatchRAM4 comes out, we will be doomed.
kitchensinked("BlueToolFixup", "[a-zA-Z]+BluetoothInjector") -- Show the full name
kitchensinked("AirportItlwm", " (Itlwm)") -- Messy, but at least it won't pickup AirportItlwm as Itlwm
kitchensinked("USBMap", "UTBMap")
kitchensinked("UTBMap", "UTBDefault")

kitchensinkedwithmsg("USBMap does not depend on USBToolBox, but it is still detected")
kitchensinkedwithmsg("All VirtualSMC plugins are there (but it can be normal)",
	"SMCProcessor", "SMCSuperIO", "SMCLightSensor", "SMCDellSensor", "SMCBatteryManager")
kitchensinkedwithmsg("All VoodooI2C plugins are present",
	"VoodooI2CAtmelMXT", "VoodooI2CELAN", "VoodooI2CFTE", "VoodooI2CHID", "VoodooI2CSynaptics")

local trigger = false
for k in pairs(kexts) do
	if k == "USBMap" or k == "UTBMap" or k == "USBPorts" or k == "UTBDefault" or k == "USBInjectAll" then
		if trigger then
			check "Two or more USB map Kexts detected"
			break
		end
		trigger = true
	end
end
if not trigger then
	check "USB maps not found"
end

local hasutb = false
local hastoolbox = false
for k in pairs(kexts) do
	if k == "UTBMap" or k == "UTBDefault" then
		hasutb = true
	end
	if k == "USBToolBox" then
		hastoolbox = true
	end
end
if hasutb and not hastoolbox then
	check "UTBMap or UTBDefault exists, but USBToolBox is not there"
end

local platforminfo = plist.PlatformInfo.Generic
if platforminfo.SystemProductName == "iMac19,1" and platforminfo.SystemSerialNumber:sub(1, 4) == "W000" then
	check "PlatformInfo is not set up"
end

local audiopath = plist.DeviceProperties.Add["PciRoot(0x0)/Pci(0x1b,0x0)"] or {}
if audiopath["AAPL,ig-platform-id"] or audiopath["AAPL,snb-platform-id"] or audiopath["framebuffer-patch-enable"] then
	check "iGPU properties are injected to audio device"
end

local igpupath = plist.DeviceProperties.Add["PciRoot(0x0)/Pci(0x2,0x0)"] or {}
if #igpupath > 15 then
	check "iGPU properties are bloated"
end

if kexts.Lilu.Comment == "Patch engine" and kexts.Lilu.MinKernel == "8.0.0" then
	check "OC Clean Snapshot or configurator equivalent is not done"
end

if ssdts["SSDT-EC"] then
	for k in pairs(ssdts) do
		if k:sub(1,8) == "SSDT-EC-" then
			check "SSDTTime SSDT-EC is present, but prebuilt SSDT-EC is also present" break
		end
	end
end

section() -- Prebuilt/autotool/configurator

for _, v in pairs(plist.Kernel.Add) do
	if v.Arch == "x86_64" then
		check "Arch is set to x86_64" break
	end
end

if string.match(data, "<data>[	 \n]+[a-zA-Z0-9=+/]+[ 	\n]+</data>") then
	check "Detected <data> with newline/whitespaces before </data>"
end

-- Thanks CorpNewt!
if plist.Misc.Boot.Timeout == 10 and plist.Misc.Debug.Target == 0 and plist.Misc.Boot.PickerMode == "External" 
	and plist.NVRAM.Add["7C436110-AB2A-4BBB-A880-FE41995C9F82"]["prev-lang:kbd"] == "en:252" then
	check "Failed specific autotool detection"
end

if type(plist.UEFI.Drivers[1]) == "string" then
	check "OpenCore is outdated(old Drivers schema)"
end

if ssdts["MaLd0n"] then
	check "MaLd0n.aml is present"
end

for _, v in pairs(kexts) do
	if v.Comment:match("V[0-9.]+") then
		check "One or more Kext comment has a version" break
	end
end

for _, v in pairs(kexts) do
	if v.Comment == "" then
		check "One or more Kext comment is empty" break
	end
end

print()