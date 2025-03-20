cmake_minimum_required(VERSION 3.10)
project(cpptui LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 11)

add_executable("cpp-snake" "./snake.cpp")


# if(CMAKE_CXX_COMPILER_ID MATCHES "Clang|AppleClang|GNU")
#   target_compile_options(cpptui PRIVATE -Wall -Wextra -Wunreachable-code -Wpedantic)
# endif()
# if(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
#   target_compile_options(cpptui PRIVATE -Wweak-vtables -Wexit-time-destructors -Wglobal-constructors -Wmissing-noreturn)
# endif()
# if(CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
#   target_compile_options(cpptui PRIVATE /W4 /w44265 /w44061 /w44062)
# endif()
