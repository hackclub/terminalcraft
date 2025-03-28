# Please use the makefile if something goes wrong
#

cmake_minimum_required(VERSION 3.10)

project(clippyman)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS_DEBUG "${CMAKE_CXX_FLAGS_DEBUG} -ggdb3 -O0 -DDEBUG=1 -Wall -Wextra -Wpedantic -Wno-unused-parameter")

# https://github.com/dacap/clip/blob/main/CMakeLists.txt
if(CMAKE_CXX_COMPILER_ID STREQUAL "AppleClang")
  # Use libc++ explicitly so we can compile for
  # CMAKE_OSX_DEPLOYMENT_TARGET=10.7 or 10.8
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -stdlib=libc++")
endif()

include_directories(include)

file(GLOB
	SRC
	"src/*.cpp"
	"src/clipboard/unix/*.cpp"
	"src/clipboard/wayland/*.cpp"
	"src/clipboard/x11/*.cpp")

if(PLATFORM_WAYLAND)
set(TARGET_NAME clippyman-wayland)
elseif(PLATFORM_XORG)
set(TARGET_NAME clippyman-xorg)
else()
set(TARGET_NAME clippyman)
endif()

add_executable(${TARGET_NAME} ${SRC})

# get git branch
execute_process(
    COMMAND git rev-parse --abbrev-ref HEAD
    OUTPUT_VARIABLE GIT_BRANCH
    OUTPUT_STRIP_TRAILING_WHITESPACE
)

set(VERSION "0.0.1")
target_compile_definitions(${TARGET_NAME} PRIVATE
    VERSION="${VERSION}"
    BRANCH="${GIT_BRANCH}"
)

# https://github.com/libcpr/cpr/blob/5f475522597b8f3721e2440daddeced7a969f24c/CMakeLists.txt#L39
macro(add_option OPTION_NAME OPTION_TEXT OPTION_DEFAULT)
    option(${OPTION_NAME} ${OPTION_TEXT} ${OPTION_DEFAULT})
    if(DEFINED ENV{${OPTION_NAME}})
        # Allow overriding the option through an environment variable
        set(${OPTION_NAME} $ENV{${OPTION_NAME}})
    endif()
    if(${OPTION_NAME})
        add_definitions(-D${OPTION_NAME})
    endif()
    message(STATUS "  ${OPTION_NAME}: ${${OPTION_NAME}}")
endmacro()

message(STATUS "Set flags:")
message(STATUS "=================")
add_option(PLATFORM_WAYLAND "Build clippyman for Wayland" 0)
add_option(PLATFORM_XORG "Build clippyman for X11" 0)
add_option(VARS "Add additional flags to CXXFLAGS" "")
message(STATUS "=================")

if(PLATFORM_WAYLAND)
	target_link_libraries(${TARGET_NAME} PUBLIC -lwayland-client)
	add_definitions(-DPLATFORM_UNIX=0)
	add_definitions(-DPLATFORM_XORG=0)
elseif(PLATFORM_XORG)
        target_link_libraries(${TARGET_NAME} PUBLIC -lxcb -lxcb-xfixes)
	add_definitions(-DPLATFORM_UNIX=0)
	add_definitions(-DPLATFORM_WAYLAND=0)
else()
	add_definitions(-DPLATFORM_UNIX=1)
	add_definitions(-DPLATFORM_XORG=0)
	add_definitions(-DPLATFORM_WAYLAND=0)
endif()

# ncurses
set(CMAKE_CXX_FLAGS "-DNCURSES_STATIC ${CMAKE_CXX_FLAGS}")
target_link_libraries(${TARGET_NAME} PUBLIC -lncurses)

# fmt
add_library(fmt STATIC
	"src/fmt/os.cc"
	"src/fmt/format.cc")
target_link_libraries(${TARGET_NAME} PUBLIC fmt)

# wayclip custom fork
if(PLATFORM_WAYLAND)
if(EXISTS ${CMAKE_SOURCE_DIR}/src/clipboard/wayland/wayclip/protocol/wlr-data-control-unstable-v1.c)
message(STATUS "protocol client code already exists")
else()
execute_process(COMMAND cd ${CMAKE_SOURCE_DIR}/src/clipboard/wayland/wayclip/protocol/ && wayland-scanner private-code wlr-data-control-unstable-v1.xml wlr-data-control-unstable-v1.c
	OUTPUT_QUIET
	OUTPUT_STRIP_TRAILING_WHITESPACE)
endif()
if(EXISTS ${CMAKE_SOURCE_DIR}/src/clipboard/wayland/wayclip/protocol/wlr-data-control-unstable-v1-client-protocol.h)
message(STATUS "protocol header already exists")
else()
execute_process(COMMAND cd ${CMAKE_SOURCE_DIR}/src/clipboard/wayland/wayclip/protocol/ && wayland-scanner client-header wlr-data-control-unstable-v1.xml wlr-data-control-unstable-v1-client-protocol.h
        OUTPUT_QUIET
        OUTPUT_STRIP_TRAILING_WHITESPACE)
endif()

add_library(wayclip STATIC
	"src/clipboard/wayland/wayclip/common.c"
	"src/clipboard/wayland/wayclip/waycopy.c"
	"src/clipboard/wayland/wayclip/waypaste.c"
	"src/clipboard/wayland/wayclip/protocol/wlr-data-control-unstable-v1.c")
target_link_libraries(${TARGET_NAME} PUBLIC wayclip)
endif()
