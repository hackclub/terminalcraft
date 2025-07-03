#ifndef XSH_H
#define XSH_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h> // For chdir, fork, execvp, usleep (on POSIX)
#include <signal.h>
#include <ctype.h>  // For isdigit

#ifdef _WIN32
#include <io.h>     // For isatty
#include <lmcons.h> // For UNLEN and GetUserName
// MinGW often provides dirent.h, otherwise a custom version might be needed for Windows
#include <dirent.h> 
#include <windows.h> // For Sleep, CreateProcess, etc.
#include <conio.h>   // For _getch, _putch
#else
#include <pwd.h>    // For getpwuid
#include <sys/types.h> // For uid_t, pid_t
#include <dirent.h> // For directory operations
#include <sys/wait.h> // For waitpid
#endif

#define XSH_RL_BUFSIZE 1024
#define XSH_MAXLINE 1024
#define XSH_TOK_BUFSIZE 64
#define XSH_TOK_DELIM " \t\r\n\a"
#define XSH_HISTORY_SIZE 100
#define TAB_KEY 9

// Constants for network client (can be moved to a network specific header later)
#define SERVER_IP "172.29.176.1"
#define SERVER_PORT 12345
#define BUFFER_SIZE 1024


// Forward declarations from Xshell.c or future utils.c
char* build_prompt(void);
#ifdef _WIN32
// usleep is not standard on Windows, print_slow might need adjustment
// For simplicity, assuming usleep is available or polyfilled if used directly.
// Or, print_slow could be adapted to use Sleep().
void print_slow(const char *text, unsigned int delay_us); // Changed to unsigned int for Sleep compatibility if adapted
#else
void print_slow(const char *text, useconds_t delay);
#endif


// Forward declarations for functions/variables in other modules
extern char *builtin_str[]; // Definition will be in builtins.c
int xsh_num_builtins(void);   // Definition will be in builtins.c

extern int history_count;                 // Definition will be in history.c
extern char *history[XSH_HISTORY_SIZE]; // Definition will be in history.c
// void add_to_history(const char *line); // Example for history.c

// Function prototype for xsh_execute (defined in Xshell.c)
int xsh_execute(char **args);

#endif // XSH_H
