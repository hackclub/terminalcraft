cmake_minimum_required(VERSION 3.30)
project(ASCIIFrame)

set(CMAKE_CXX_STANDARD 17)

add_executable(ASCIIFrame main.cpp
        src/Window.cpp
        src/Window.hpp
        src/Manager.cpp
        src/Manager.hpp)

if (NOT WIN32)
    find_package(Curses REQUIRED)
    include_directories(${CURSES_INCLUDE_DIR})
    target_link_libraries(ASCIIFrame PRIVATE ${CURSES_LIBRARIES})
endif ()