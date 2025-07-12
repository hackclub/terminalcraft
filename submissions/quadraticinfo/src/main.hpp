#pragma once

#include "equation.hpp"
#include <cstdio>
#include <cmath>
#include <cstdint>
#include <memory>

#if defined(_WIN32) || defined(_WIN64)
#include <Windows.h>    
#endif

#define ESC "\x1b"
#define GRAPH_OFFSET_X 50
#define GRAPH_OFFSET_Y 2
#define OPEN_OFFSET 2
#define GRAPH_WIDTH 25
#define GRAPH_HEIGHT 15
#define LABEL(text) ESC "[32m" text ESC "[0m: "
