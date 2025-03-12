cmake_minimum_required(VERSION 3.28.3)
project(bicycle C)

set(CMAKE_C_STANDARD 23)

add_executable(bicycle
        src/main.c
        src/core/card.h
        src/core/card.c
        src/core/deck.h
        src/core/deck.c
        src/core/clock.h
        src/core/clock.c
        src/games/baccarat.h
        src/games/baccarat.c)
add_subdirectory(src/cargs)
target_link_libraries(bicycle cargs)