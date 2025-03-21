# Building and Running cpp-snake Game

This document provides instructions on how to build and run the cpp-snake game (using CMake).

## Prerequisites

*   A C++ compiler (e.g., GCC, Clang, MSVC)
*   CMake
*   A terminal or command prompt with proper ascii character support
  - (window cmd and old powershell won't work, use new windows terminal)

## Building the Game

-   **Configure the Project with CMake:**

    Run CMake to configure the project using the `CMakeLists.txt` file.

    (assuming you are in the submission folder)

    ```bash
    cmake ./CMakeLists.txt
    ```

-   **Build the Executable:**

    Use CMake to build the executable.

    ```bash
    cmake --build .
    ```

    Alternatively, you can use `make` (and probably `mingw32-make` on Windows with MinGW):

    ```bash
    make
    ```

    Or on Windows with Visual Studio:

    ```bash
    cmake --build . --config Release # or Debug
    ```

## Running the Game

After the build is successful, the executable will be located in the submisson directory.  The executable name is `cpp-snake(.exe)`

-   **Run the Executable:**

    Execute the game by running the executable:

    ```bash
    ./cpp-snake(.exe)
    ```

    On Windows, the executable might be located in a subdirectory (e.g., `build\Release` or `build\Debug`).  In that case, run the executable from the correct directory:

    ```bash
    .\Release\cpp-snake.exe  #or .\Debug\cpp-snake.exe
    ```

## Thats it, have fun playing!
