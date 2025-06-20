#ifndef HISTORY_H
#define HISTORY_H

#include "xsh.h" // For XSH_HISTORY_SIZE

// External declarations for history variables and functions
// Definitions will be in history.c
extern char *history[XSH_HISTORY_SIZE];
extern int history_count;

// Function prototypes for history.c
void add_to_history(const char *line);
void display_history(void); // Corresponds to the part of xsh_history that prints
// int xsh_history_cmd(char **args); // If we want `history` to be a command handled by this module

#endif // HISTORY_H
