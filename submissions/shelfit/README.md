# Shelfit - Quick Notes & Snippets CLI

A lightweight, fast command-line tool for storing and retrieving notes, links, and code snippets.

## Installation

### Windows
Because sqlite3.lib is included in the package, you can install it with the following command:
```bash
cargo install shelfit
```

### Linux
You may need to install the sqlite3 development library before installing the program:
```bash
sudo apt install libsqlite3-dev
cargo install shelfit
```

## Build 
To build the project, run the following command:
```bash
cargo build
```
If you are on linux, you may need to install the sqlite3 development library first:
```bash
sudo apt install libsqlite3-dev
```

## Usage

### Add a note
```bash
shelfit save "This is a note"
```
#### with a tag
```bash
shelfit save "This is a note" -t tag1
```
#### with a url
```bash
shelfit save "This is a note" https://example.com
```

### List all notes
```bash
shelfit list
```

### Search notes
```bash
shelfit search "query"
```

### Delete a note
```bash
shelfit delete 1
```

### Export notes
```bash
shelfit export /path/to/export.json
```

### Copy a note to clipboard
```bash
shelfit copy 1
```
