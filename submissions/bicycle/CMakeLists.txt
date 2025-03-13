cmake_minimum_required(VERSION 2.8)
project(bicycle C)

set(CMAKE_CXX_STANDARD 23)

add_executable(bicycle
        src/bicycle.cpp
        src/core/card.h
        src/core/card.cpp
        src/core/deck.h
        src/core/deck.cpp
        src/games/baccarat.h
        src/games/baccarat.cpp)
add_subdirectory(src/cargs)
target_link_libraries(bicycle cargs)