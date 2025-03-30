# Clippyman
A simple and perfomant, multi-platform clipboard manager.

# Dependencies
Only `ncurses` and its devel libraries (e.g `ncurses-devel`)\
Search online how to install in your OS.

# Building
normal Makefile
```bash
# PLATFORM can be x11, wayland or unix
# it will be added in the binary name at the end
# e.g clippyman-wayland
# For all OS it's best to use PLATFORM=unix
make PLATFORM=unix DEBUG=0
```

Alternatively if you wish to use cmake
```bash
mkdir build && cd $_
# here you need to specify the platform like -DPLATFORM_WAYLAND or -DPLATFORM_X11
cmake .. -DCMAKE_BUILD_TYPE=Release
make # or ninja
```

# Usage
if you compiled with normal Makefile then,\
if run with `DEBUG=0`
```bash
$ cd build/release
```
else
```bash
$ cd build/debug
```

Remember that clippyman can be compiled with different binary names, depending on the platform you compiled on.
* `clippyman` if compiled with `PLATFORM=unix` (make) or without `PLATFORM` flags
* `clippyman-x11` if compiled with either `PLATFORM=x11` (make) or `-DPLATFORM_X11=1` (cmake)
* `clippyman-wayland` if compiled with either `PLATFORM=wayland` (make) or `-DPLATFORM_WAYLAND=1` (cmake)

If you have compiled for either x11 or wayland, then when you run the binary without arguments,\
it will listen in the background what you copy for then printing in the terminal and saving it in the clipboard history.

If you run with `-i` then it will enter in terminal input mode, where you'll Type or Paste the text to save in the clipboard history, then press enter and CTRL+D to save and exit

### Synopsis
```
$ ./clippyman -h
Usage: clippyman [OPTIONS]...
    -i, --input                 Enter in terminal input mode (on by default for unix builds)
    -p, --path <path>           Path to where we'll search/save the clipboard history
    -P, --primary [<bool>]      Use the primary clipboard instead
    -S, --silent [<bool>]       Print or Not an info message along the search content you selected
    --wl-seat <name>            The seat for using in wayland (just leave it empty if you don't know what's this)
    -s, --search                Delete/Search clipboard history. At the moment is not possible to search UTF-8 characters
                                Press TAB to switch beetwen search bar and clipboard history.
                                In clipboard history: press 'd' for delete, press enter for output selected text

    -C, --config <path>         Path to the config file to use
    --gen-config [<path>]       Generate default config file to config folder (if path, it will generate to the path)
                                Will ask for confirmation if file exists already

    -h, --help                  Print this help menu
    -V, --version               Print the version along with the git branch it was built

$ ./clippyman
INFO: Type or Paste the text to save in the clipboard history, then press enter and CTRL+D to save and exit
test
$
```

There is also a config that gets generated automatically in `~/.config/clippyman/config.toml`
```toml
[config]
# Path to where we store the clipbpoard history
path = "~/.cache/clippyman/history.json"

# Use the primary clipbpoard instead
primary = false

# The seat for using in wayland (i don't know what that is tbh, just leave it empty)
wl-seat = ""

# Print an info message along the search content you selected
silent = false
```
