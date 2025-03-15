# Tape Backup and Restore Tool

## Overview

This script provides a command-line utility to back up and restore data using tape drives. It supports using an LTO tape changer and allows you to specify multiple tape slots. The script handles both backup and restoration operations, with real-time progress updates.
## Features

Backup and restore data from a directory to/from a tape drive.
Support for multiple tape slots managed through an LTO tape changer.
Real-time progress bar with estimated time remaining.
Logging of tar output and tape operations.
Option to specify serial numbers for tapes instead of slots.
## Prerequisites

Tape Drive: Ensure that you have a tape drive connected and configured.
Tape Changer: An LTO tape changer (e.g., /dev/sg2) should be properly set up.

Required Tools: Ensure the following tools are installed:
```
tar
mtx
mt
```
## Installation

Clone the Repository:

```
git clone https://github.com/ImNoahDev/ltoBackupTools
cd ltoBackupTools
```
Make the Scripts Executable:

```
chmod +x ltochanger 
chmod +x ltoTarTools 
```
Install required packages
```
sudo apt-get install tar mtx mt
sudo dnf install tar mtx mt
```
## Usage

Command Syntax

```
 ltoTarTools  -o {extract|write} -d <directory> -s <tape_slots> [-t <tape_device>] [-c <changer_device>] [-z <tape_serials>]
```
Options
```
-o: Operation to perform. Options are extract (restore) or write (backup).
-d: Directory to extract to or copy from.
-s: Comma-separated list of tape slots to use (e.g., 1,2,3).
-t: Tape device (e.g., /dev/st0). Default is /dev/st0.
-c: Tape changer device (e.g., /dev/sg2). Default is /dev/sg2.
-z: Comma-separated list of tape serials to use.
```

### Example Commands:
Backup Data:

```
 ltoTarTools  -o write -d /path/to/backup -s 1,2,3 -t /dev/st0 -c /dev/sg2
```
Restore Data:

```
 ltoTarTools  -o extract -d /path/to/restore -s 1,2,3 -t /dev/st0 -c /dev/sg2
```
