# Makefile for XShell

# Compiler and Flags
CC = gcc
# Add -std=c11 for C11 standard features
CFLAGS = -Iinclude -Wall -Wextra -g -std=c11
LDFLAGS =

# Project Structure
SRC_DIR = src
OBJ_DIR = obj
BIN_DIR = bin

# Automatically find all .c files and generate corresponding .o and .d file names
SOURCES = $(wildcard $(SRC_DIR)/*.c)
OBJECTS = $(patsubst $(SRC_DIR)/%.c,$(OBJ_DIR)/%.o,$(SOURCES))
DEPS = $(OBJECTS:.o=.d) # Dependency files for header tracking

# --- OS-Specific Configuration ---
# Default to Unix-like settings
EXECUTABLE = $(BIN_DIR)/Xshell
RM = rm -f
MKDIR_P = mkdir -p

# Check if the OS is Windows
ifeq ($(OS),Windows_NT)
    EXECUTABLE = $(BIN_DIR)/Xshell.exe
    # Link against Winsock2 and IP Helper libraries on Windows
    LDFLAGS += -lws2_32 -liphlpapi
    RM = del /Q /F
	# Windows has no `mkdir -p`, so we create the directory if it doesn't exist.
    MKDIR_P = if not exist $(@D) mkdir $(@D)
else
    # Link against the math library on Unix-like systems (often needed)
    LDFLAGS += -lm
endif

# --- Build Rules ---

# Default target: build the executable
all: $(EXECUTABLE)

# Rule to link the final executable
$(EXECUTABLE): $(OBJECTS)
	@$(MKDIR_P)
	$(CC) $(OBJECTS) -o $@ $(LDFLAGS)
	@echo "XShell built successfully: $@"

# Rule to compile .c files into .o files in the OBJ_DIR
# The -MMD and -MP flags generate dependency files (.d) automatically
$(OBJ_DIR)/%.o: $(SRC_DIR)/%.c
	@$(MKDIR_P)
	$(CC) $(CFLAGS) -MMD -MP -c $< -o $@

# --- Housekeeping Rules ---

# Clean the project
clean:
	-$(RM) $(EXECUTABLE)
	-$(RM) $(OBJECTS)
	-$(RM) $(DEPS)
	-@if exist $(OBJ_DIR) rmdir /S /Q $(OBJ_DIR) 2>nul || rm -rf $(OBJ_DIR)

# Rebuild the project
re: clean all

# Run the shell
run: all
	@echo "Starting XShell..."
	# Use backslashes for the path on Windows
	ifeq ($(OS),Windows_NT)
		.\$(EXECUTABLE)
	else
		./$(EXECUTABLE)
	endif

# Include the generated dependency files. The '-' suppresses errors if they don't exist.
-include $(DEPS)

# Phony targets are not real files
.PHONY: all clean re run
