cmake_minimum_required(VERSION 3.12)
project(bicycle CXX)

set(CMAKE_CXX_STANDARD 23)

add_executable(bicycle
        bicycle.cpp
        core/card.h
        core/card.cpp
        core/deck.h
        core/deck.cpp
        games/baccarat.h
        games/baccarat.cpp)
add_subdirectory(cargs)
target_link_libraries(bicycle cargs)
target_compile_features(bicycle PUBLIC cxx_std_23)
