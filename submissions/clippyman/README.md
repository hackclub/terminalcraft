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

### Examples
```
$ ./clippyman -i
INFO: Type or Paste the text to save in the clipboard history, then press enter and CTRL+D to save and exit
test
$
```

If you run with `-i` then it will enter in terminal input mode, where you'll Type or Paste the text to save in the clipboard history, then press enter and CTRL+D to save and exit.
It's also possibile to save or copy the output of a program by using pipes.
E.g
```bash
# Save the output of a program
$ echo "test-pipe" | clippyman -i

# Copy the output of a program (x11 only)
$ echo "test-pipe" | clippyman -c

# Copy & Save the output of a program (x11 only)
$ echo "test-pipe" | clippyman -ic
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
