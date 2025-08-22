#ifndef UTILS_H
#define UTILS_H

#include "xsh.h" // For useconds_t (on POSIX) and other common defs

// Function prototype for utils.c
// Standardized to take delay in milliseconds
void print_slow(const char *text, unsigned int delay_ms);

char* build_prompt(void);

// Function prototype for case-insensitive string search
char *strcasestr_custom(const char *haystack, const char *needle);

// Helper function to process a single stream (file or stdin) for grep
void process_grep_stream(FILE *fp, const char *pattern, int case_insensitive, const char *filename_to_print);

// Function prototype for recursive removal
int remove_recursively_internal(const char *path);
int create_file_with_content(const char *path, const char *content);

#endif // UTILS_H
