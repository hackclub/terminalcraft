# Cubitr
*A Minimalist 3D Terminal Renderer, with nice movement functionalities*




https://github.com/user-attachments/assets/05424092-1c3c-4257-8af5-c21d6534b29a


## Usage Instructions

- **Arrow keys**: Move up/down/left/right
- **'r'**: Toggle spinning
- **'q'**: Quit

## Build Instructions

This document provides instructions on how to build and run Cubitr on Linux, macOS, and Windows.

### Dependencies

#### Linux / macOS

Ensure you have the following installed:

- GCC
- CMake (version 3.10 or newer)
- ncurses

On Debian-based systems:

```sh
sudo apt install build-essential cmake libncurses-dev
```

On Arch-based systems:

```sh
sudo pacman -S base-devel cmake ncurses
```

On macOS (using Homebrew):

```sh
brew install cmake ncurses
```

#### Windows (MinGW-w64)

Ensure you have:

- MinGW-w64 (installed via MSYS2)
- CMake
- ncurses (from MinGW64 repository)

Install dependencies using MSYS2:

```sh
pacman -S mingw-w64-x86_64-gcc mingw-w64-x86_64-cmake mingw-w64-x86_64-ncurses
```

### Building the Project

#### Linux / macOS

```sh
mkdir build && cd build
cmake ..
make
```

### Windows (MinGW-w64)

```sh
mkdir build && cd build
cmake  -S ..
cmake --build .
```

### Running the Program

After building, run the executable:

```sh
./Cubitr  # Linux/macOS
Cubitr.exe  # Windows
```

### Troubleshooting

- If `ncurses.h` is not found, ensure the development package is installed.
- On Windows, ensure you are using the correct MinGW-w64 environment (MSYS2 MinGW64 shell).
- If `cmake` fails to detect ncurses, try specifying it manually:
  ```sh
  cmake -DCURSES_INCLUDE_PATH=/path/to/ncurses/include -DCURSES_LIBRARY=/path/to/ncurses/lib ..
  ```

