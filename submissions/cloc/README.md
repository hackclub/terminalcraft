# cloc

## Description
cloc (Count LOC) is a simple terminal utility to easily count lines of code in a file / project. 

## Why I Made This?
I created cloc to provide a lightweight and easy to use terminal-based LOC counter with flexible ignore patterns.  
Unlike existing tools, it supports recursive ignore patterns and simple wildcard filtering to streamline codebase analysis without making it too complex.

## Features
 - Counts lines of code in files and directories recursively
 - Allows easy exclusion of files, directories, and patterns with wildcards
 - Simple help menu and thorough documentation
 - .clocignore file to handle many ignore patterns in large projects

## Installation
### Windows, Linux & Mac
#### Python
1. Make sure you have a recent version of Python installed.
2. Run the command `pip install plazma-cloc` to install.
3. Done.

#### Binary (Usefull on Raspberry Pi)
1. Download the binary from the releases page on GitHub
2. Use `./cloc` to run the binary.
> Note: You may want to add the binary's directory to your system `PATH` so you can run cloc from anywhere without needing the `./`.

## Running The Binary
You can run the pre-built Linux binary directly from the terminal without installing Python as such:

```bash
./cloc -h
./cloc /path/to/project --ignore "*.test"
```

> Note: See **Usage** below for more information on how to use...

## Usage
> Note: If using the binary, replace 'cloc' with './cloc'. If using the pip installation, replace 'cloc' with 'python -m cloc'.

1. Open a terminal and run the command `cloc <PATH_TO_FILE_OR_PROJECT>`
2. For help run the command `cloc -h`

To narrow the file types down use the `--ignore` flag.
This flag allows you to ignore certain files, directories and file extensions.

### Ignoring singular files
To ignore one file use `cloc your_project_folder --ignore your_file.txt`

You can also ignore multiple files with this same syntax.

E.G. `cloc your_project_folder --ignore "your_file.txt" "your_other_file.txt"`

> Note: It is good practice to surround each file / directory / extension in quotation marks to avoid your terminal getting confused

### Ignoring singular directories
To ignore one directory use `cloc your_project_folder --ignore your_directory/`

You can also ignore multiple directories with this same syntax.

E.G. `cloc your_project_folder --ignore "your_directory/" "your_other_directory/"`

> Note: Ensure to add a '/' character to the end of your directory name so the program knows it is a directory

### Ignoring files with certain file extensions
To ignore all files with a certain file extension use: `cloc your_project_folder --ignore "*.txt"`

> Note: The '*' character is a wildcard character and tells the program it means every file with the file extension after the wildcard.

Then after the wildcard you enter the file extension. E.G. ".txt" or ".exe"...

You can also ignore multiple file extensions with the same syntax as before.
`cloc your_project_folder --ignore "*.txt" "*.exe" "*.json"`

### Ignoring all directories with the same name
To ignore all directories with the same name use a similar ignore pattern as before:
`cloc your_project_folder --ignore your_directory/*`

> Note: You must append `/*` to the end of the directory name so that the program knows it is a recursive directory ignore.

You can ignore multiple directories using a similar command:
`cloc your_project_folder --ignore "your_directory/*" "your_other_directory/*"`

### Using .clocignore to ingore many patterns
In large projects (or just for convenience) you may wish to use a .clocignore file to handle many patterns.

A .clocignore file should look something like this:
```.clocignore
a_file.txt
a_directory/
*.test
a_repetitive_directory/*
```

The .clocignore just contains all of your `--ignore` arguments in a file format. Each ignore pattern is placed on a new line.

To open a .clocignore simply run cloc with the `--clocignore <YOUR_CLOCIGNORE_FILE>` flag.
An example of this is: `cloc your_project_folder --clocignore .clocignore`

> Note: The `.clocignore` file you provide as an argument should be relative to where you are running the `cloc` executable from (where your terminal is).
> The `--clocignore` flag will override the `--ignore` flag.