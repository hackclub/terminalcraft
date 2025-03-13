# Clippyman
A simple and perfomant, multi-platform clipboard manager.

# Dependencies
Only `ncurses`\
Search online how to install in your OS.

# Building
```bash
# PLATFORM can be xorg, wayland or unix
# it will be added in the binary name at the end
# e.g clippyman-wayland
# For all OS it's best to use PLATFORM=unix
make PLATFORM=unix DEBUG=0
```
Alternatively if you wish to use cmake
```bash
mkdir build && cd $_
# here you need to specify the platform like -DPLATFORM_WAYLAND or -DPLATFORM_UNIX
cmake .. -DPLATFORM_UNIX=1 -DCMAKE_BUILD_TYPE=Release
make
```
