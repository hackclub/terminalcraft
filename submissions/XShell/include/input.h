#ifndef INPUT_H
#define INPUT_H

#include "xsh.h" // For common definitions

// Function prototypes for input.c
char *xsh_read_line(void);
char **xsh_split_line(char *line);
char** find_matches(const char* partial, int* match_count);
void display_matches(char** matches, int match_count);
char* complete_command(const char* partial);

#endif // INPUT_H
