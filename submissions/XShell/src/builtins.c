#ifdef _WIN32
#include <winsock2.h> // For Windows socket functions
#include <direct.h> // For _mkdir, _getcwd
#include <io.h>     // For _access (if needed for file checks)
#else
#include <sys/stat.h> // For mkdir (POSIX)
#include <fcntl.h>    // For open (used in touch POSIX)
#endif

#include "builtins.h"
#include "network.h" // For xsh_client, though it's declared in builtins.h for now
#include "history.h" // For history array and count (declared extern there)
#include "utils.h" // For utility functions like print_slow, build_prompt
#include "xproj.h" // For xsh_xproj (project creation command)
#include "xnote.h" // For xsh_xnote (encrypted note keeper command)
#include "xpass.h" // For xsh_xpass (password strength analyzer and generator)
#include "xnet.h"
#include "xscan.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h> // For chdir, getcwd (POSIX)
#include <dirent.h> // For opendir, readdir, closedir (used indirectly by ls or completion)
#include <ctype.h>  // For tolower (needed for case-insensitive grep)





// Built-in command names
char *builtin_str[] = {
    "cd", "pwd", "ls", "grep", "echo", "mkdir", "touch", "cp", "mv",
    "rm", "cat", "xmanifesto", "xproj", "xnote", "xpass", "xeno", "xnet", "xscan", "history", "help", "clear", "exit"
};

// Descriptions for built-in commands (for help)
char *builtin_desc[] = {
    "Change directory",
    "Print working directory",
    "List directory contents",
    "Search for patterns in files",
    "Display a line of text",
    "Create directories",
    "Create empty files or update file timestamps",
    "Copy files and directories from source to destination",
    "Move (rename) files and directories",
    "Remove files or directories",
    "Concatenate and display file contents",
    "Display the Xenomench Manifesto",
    "Create a new project structure (C, Python, or Web)",
    "Encrypted Note Keeper",
    "Password Strength Analyzer and Generator",
    "Connect you to the Gatekeeper (network client)",
    "Minimal Network Diagnostic Tools",
    "Custom Port Scanner",
    "Show command history",
    "Display help information about available commands",
    "Clear the terminal screen",
    "Exit the shell program"
};

// Usage strings for built-in commands
char *builtin_usage[] = {
    "Usage: cd <directory>",
    "Usage: pwd",
    "Usage: ls [path]",
    "Usage: grep [-i] <pattern> [file...]",
    "Usage: echo [string ...]",
    "Usage: mkdir <directory_name> [directory_name2] ...",
    "Usage: touch <file_name> [file_name2] ...",
    "Usage: cp <source_file> <destination_file>",
    "Usage: mv <source_file> <destination_file>",
    "Usage: rm <name1> [name2] ...",
    "Usage: cat <file_name> [file_name2] ...",
    "Usage: xmanifesto",
    "Usage: xproj <project_type (c, py, web)> <project_name> [--git]",
    "Usage: xnote <command> [options]\nCommands:\n  add <name> \"<content>\" - Create a new note.\n  view <name>             - View a decrypted note.\n  lock <name>             - Encrypt a note with a password.\n  list                    - List all available notes.\n  delete <name>           - Delete a note.",
    "Usage: xpass <command> [options]\nCommands:\n  gen [length] [--no-upper] [--no-lower] [--no-digits] [--no-symbols] - Generate a password.\n  check <password> - Check the strength of a password.",
    "Usage: xeno [hostname] [port]  (Note: Actual arguments depend on client implementation)",
    "Usage: xnet [show|ping|traceroute] [host]",
    "Usage: xscan <target IP> <start port> [end port]",
    "Usage: history",
    "Usage: help [command]",
    "Usage: clear",
    "Usage: exit"
};

// Array of function pointers for built-in commands
int (*builtin_func[])(char **) = {
    &xsh_cd, &xsh_pwd, &xsh_ls, &xsh_grep, &xsh_echo, &xsh_mkdir, &xsh_touch,
    &xsh_cp, &xsh_mv, &xsh_rm, &xsh_cat, &xsh_manifesto, &xsh_xproj, &xsh_xnote,
    &xsh_xpass, &xsh_client, &xsh_xnet, &xsh_xscan,
    &xsh_history, &xsh_help, &xsh_clear, &xsh_exit
};

int xsh_num_builtins() {
    return sizeof(builtin_str) / sizeof(char *);
}

// Implementations of built-in functions

int xsh_cd(char **args) { 
    if (args[1] == NULL) {
        fprintf(stderr, "xsh: cd: missing argument\n");
    } else {
        if (chdir(args[1]) != 0) {
            perror("xsh: chdir failed");
        }
    }
    return 1;
}

int xsh_pwd(char **args) {
    char cwd[XSH_MAXLINE]; // Use defined constant
#ifdef _WIN32
    if (_getcwd(cwd, sizeof(cwd)) == NULL) {
#else
    if (getcwd(cwd, sizeof(cwd)) == NULL) {
#endif
        perror("xsh: pwd failed");
    } else {
        printf("%s\n", cwd);
    }
    return 1;
}

int xsh_ls(char **args) {
    const char *path_to_list = "."; // Default to current directory

    if (args[1] != NULL) {
        // If a path is provided, use it.
        path_to_list = args[1];
    }

#ifdef _WIN32
    WIN32_FIND_DATA findFileData;
    HANDLE hFind = INVALID_HANDLE_VALUE;
    char searchPath[XSH_MAXLINE];

    // Prepare search path (e.g., "directory\*")
    strncpy(searchPath, path_to_list, XSH_MAXLINE - 1);
    searchPath[XSH_MAXLINE - 1] = '\0'; // Ensure null termination

    size_t current_len = strlen(searchPath);
    if (current_len > 0 && (searchPath[current_len - 1] == '\\' || searchPath[current_len - 1] == '/')) {
        if (current_len + 1 < XSH_MAXLINE) {
            strcat(searchPath, "*");
        } else {
            fprintf(stderr, "xsh: ls: path too long to append wildcard: %s\n", path_to_list);
            return 1;
        }
    } else {
        if (current_len + 2 < XSH_MAXLINE) { // Check space for '\*' and null terminator
            strcat(searchPath, "\\*");
        } else {
            fprintf(stderr, "xsh: ls: path too long to append wildcard: %s\n", path_to_list);
            return 1;
        }
    }

    hFind = FindFirstFile(searchPath, &findFileData);

    if (hFind == INVALID_HANDLE_VALUE) {
        DWORD dwError = GetLastError();
        if (dwError != ERROR_FILE_NOT_FOUND) {
            fprintf(stderr, "xsh: ls: cannot access '%s': ", path_to_list);
            LPVOID lpMsgBuf;
            FormatMessage(
                FORMAT_MESSAGE_ALLOCATE_BUFFER | FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_IGNORE_INSERTS,
                NULL, dwError, MAKELANGID(LANG_NEUTRAL, SUBLANG_DEFAULT),
                (LPTSTR) &lpMsgBuf, 0, NULL );
            fprintf(stderr, "%s\n", (char*)lpMsgBuf);
            LocalFree(lpMsgBuf);
        }
        // If ERROR_FILE_NOT_FOUND, it could be an empty or non-existent directory.
        // ls typically prints nothing for an empty directory and returns success.
        return 1;
    }

    do {
        if (strcmp(findFileData.cFileName, ".") == 0 || strcmp(findFileData.cFileName, "..") == 0) {
            continue;
        }
        printf("%s\n", findFileData.cFileName);
    } while (FindNextFile(hFind, &findFileData) != 0);

    FindClose(hFind);

#else // POSIX implementation
    DIR *dir;
    struct dirent *entry;

    dir = opendir(path_to_list);
    if (dir == NULL) {
        fprintf(stderr, "xsh: ls: cannot access '%s': ", path_to_list);
        perror("");
        return 1;
    }

    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }
        printf("%s\n", entry->d_name);
    }

    if (closedir(dir) == -1) {
        perror("xsh: ls: closedir failed");
    }
#endif
    return 1;
}

int xsh_clear(char **args) {
#ifdef _WIN32
    system("cls");
#else
    system("clear");
#endif
    return 1;
}

int xsh_cp(char **args) {
    if (args[1] == NULL || args[2] == NULL) {
        fprintf(stderr, "xsh: cp: missing source or destination file\n");
        fprintf(stderr, "Usage: cp <source_file> <destination_file>\n");
        return 1;
    }

    FILE *src_file, *dest_file;
    int ch;

    src_file = fopen(args[1], "rb");
    if (src_file == NULL) {
        fprintf(stderr, "xsh: cp: cannot open source file '%s': ", args[1]);
        perror("");
        return 1;
    }

    dest_file = fopen(args[2], "wb");
    if (dest_file == NULL) {
        fprintf(stderr, "xsh: cp: cannot open destination file '%s': ", args[2]);
        perror("");
        fclose(src_file);
        return 1;
    }

    while ((ch = fgetc(src_file)) != EOF) {
        fputc(ch, dest_file);
    }

    if (ferror(src_file)) {
        fprintf(stderr, "xsh: cp: error reading source file '%s'\n", args[1]);
    }
    if (ferror(dest_file)) {
        fprintf(stderr, "xsh: cp: error writing to destination file '%s'\n", args[2]);
    }

    if (fclose(src_file) == EOF) {
        fprintf(stderr, "xsh: cp: error closing source file '%s': ", args[1]);
        perror("");
    }
    if (fclose(dest_file) == EOF) {
        fprintf(stderr, "xsh: cp: error closing destination file '%s': ", args[2]);
        perror("");
    } else {
        printf("Copied '%s' to '%s'\n", args[1], args[2]);
    }
    return 1;
}

int xsh_mv(char **args) {
    if (args[1] == NULL || args[2] == NULL) {
        fprintf(stderr, "xsh: mv: missing source or destination file\n");
        fprintf(stderr, "Usage: mv <source_file> <destination_file>\n");
        return 1;
    }

    if (rename(args[1], args[2]) != 0) {
        perror("xsh: mv failed");
        // rename might fail across different filesystems. 
        // A more robust mv would copy then delete.
        return 1;
    } else {
        printf("Moved '%s' to '%s'\n", args[1], args[2]);
    }
    return 1;
}

int xsh_rm(char **args) {
    if (args[1] == NULL) {
        fprintf(stderr, "xsh: rm: missing file or directory operand\n");
        fprintf(stderr, "Usage: rm <name1> [name2] ...\n");
        return 1;
    }
    for (int i = 1; args[i] != NULL; i++) {
        // remove_recursively_internal is now defined in utils.c and declared in utils.h
        if (remove_recursively_internal(args[i]) != 0) {
            // Error messages are printed by remove_recursively_internal
            // Standard rm typically continues with other arguments even if one fails.
            // We might want to return a different status or set a flag if any removal fails,
            // but for now, it prints errors and continues.
        } else {
            printf("Removed '%s'\n", args[i]);
        }
    }
    return 1; // Continue shell loop
}

int xsh_cat(char **args) {
    if (args[1] == NULL) {
        fprintf(stderr, "xsh: cat: missing file operand\n");
        fprintf(stderr, "Usage: cat <file_name> [file_name2] ...\n");
        return 1;
    }
    for (int i = 1; args[i] != NULL; i++) {
        FILE *fp = fopen(args[i], "r");
        if (fp == NULL) {
            fprintf(stderr, "xsh: cat: cannot open '%s': ", args[i]);
            perror("");
            continue; 
        }
        char line[XSH_MAXLINE];
        while (fgets(line, sizeof(line), fp)) {
            fputs(line, stdout);
        }
        if (ferror(fp)) {
            fprintf(stderr, "xsh: cat: error reading file '%s'\n", args[i]);
        }
        if (fclose(fp) == EOF) {
            fprintf(stderr, "xsh: cat: error closing '%s': ", args[i]);
            perror("");
        }
    }
    return 1;
}


int xsh_grep(char **args) {
    int case_insensitive = 0;
    char *pattern_arg = NULL;
    int first_file_arg_index = -1;

    if (args[1] == NULL) { // No arguments after "grep"
        fprintf(stderr, "xsh: grep: missing pattern\nUsage: grep [-i] <pattern> [file...]");
        return 1;
    }

    int current_arg_idx = 1;
    // Parse options
    while (args[current_arg_idx] != NULL && args[current_arg_idx][0] == '-' && strlen(args[current_arg_idx]) > 1) {
        if (strcmp(args[current_arg_idx], "-i") == 0) {
            case_insensitive = 1;
            current_arg_idx++;
        } else {
            fprintf(stderr, "xsh: grep: unknown option %s\nUsage: grep [-i] <pattern> [file...]", args[current_arg_idx]);
            return 1;
        }
    }

    // Next argument is the pattern
    if (args[current_arg_idx] == NULL) {
        fprintf(stderr, "xsh: grep: missing pattern after options\nUsage: grep [-i] <pattern> [file...]");
        return 1;
    }
    pattern_arg = args[current_arg_idx];
    current_arg_idx++; // Move to where filenames would start
    first_file_arg_index = current_arg_idx;

    char *actual_pattern = pattern_arg;
    char *allocated_quoted_pattern_buffer = NULL;
    size_t pattern_len = strlen(pattern_arg);

    if (pattern_len >= 2 && pattern_arg[0] == '"' && pattern_arg[pattern_len - 1] == '"') {
        allocated_quoted_pattern_buffer = malloc(pattern_len - 1);
        if (!allocated_quoted_pattern_buffer) {
            fprintf(stderr, "xsh: grep: memory allocation error for pattern\n");
            return 1;
        }
        strncpy(allocated_quoted_pattern_buffer, pattern_arg + 1, pattern_len - 2);
        allocated_quoted_pattern_buffer[pattern_len - 2] = '\0';
        actual_pattern = allocated_quoted_pattern_buffer;
    }

    int num_file_args = 0;
    for (int i = first_file_arg_index; args[i] != NULL; i++) {
        num_file_args++;
    }
    int print_filenames_flag = (num_file_args > 1);

    if (args[first_file_arg_index] == NULL) { // No file arguments, read from stdin
        process_grep_stream(stdin, actual_pattern, case_insensitive, NULL); // No filename to print for stdin
    } else { // Process one or more files
        for (int i = first_file_arg_index; args[i] != NULL; i++) {
            FILE *fp = fopen(args[i], "r");
            if (fp == NULL) {
                fprintf(stderr, "xsh: grep: %s: ", args[i]);
                perror("");
                continue; // Standard grep continues with other files
            }
            process_grep_stream(fp, actual_pattern, case_insensitive, print_filenames_flag ? args[i] : NULL);
            if (fclose(fp) == EOF) {
                fprintf(stderr, "xsh: grep: error closing %s: ", args[i]);
                perror("");
            }
        }
    }

    if (allocated_quoted_pattern_buffer) {
        free(allocated_quoted_pattern_buffer);
    }
    return 1;
}

int xsh_echo(char **args) {
    for (int i = 1; args[i] != NULL; i++) {
        printf("%s%s", args[i], (args[i+1] != NULL ? " " : ""));
    }
    printf("\n");
    return 1;
}

int xsh_mkdir(char **args) {
    if (args[1] == NULL) {
        fprintf(stderr, "xsh: mkdir: missing argument\n");
        fprintf(stderr, "Usage: mkdir <directory_name> [directory_name2] ...\n");
        return 1;
    }
    for (int i = 1; args[i] != NULL; i++) {
#ifdef _WIN32
        if (_mkdir(args[i]) != 0) {
#else
        if (mkdir(args[i], 0755) != 0) { // 0755 are typical permissions
#endif
            fprintf(stderr, "xsh: mkdir: cannot create directory '%s': ", args[i]);
            perror("");
        } else {
            printf("Created directory '%s'\n", args[i]);
        }
    }
    return 1;
}

int xsh_touch(char **args) {
    if (args[1] == NULL) {
        fprintf(stderr, "xsh: touch: missing file operand\n");
        fprintf(stderr, "Usage: touch <file_name> [file_name2] ...\n");
        return 1;
    }
    for (int i = 1; args[i] != NULL; i++) {
#ifdef _WIN32
        FILE *fp = fopen(args[i], "ab"); // Open in append binary mode to create if not exists, or update timestamp
        if (fp == NULL) {
            // If opening failed, try to create it
            fp = fopen(args[i], "wb");
            if (fp == NULL) {
                fprintf(stderr, "xsh: touch: cannot touch '%s': ", args[i]);
                perror("");
                continue;
            }
        }
        printf("Touched file '%s'\n", args[i]);
        fclose(fp);
#else
        // POSIX: O_CREAT creates if not exists. O_APPEND updates timestamp.
        // utime() or utimensat() would be more precise for just updating timestamps.
        int fd = open(args[i], O_CREAT | O_WRONLY | O_APPEND, S_IRUSR | S_IWUSR | S_IRGRP | S_IROTH);
        if (fd == -1) {
            fprintf(stderr, "xsh: touch: cannot touch '%s': ", args[i]);
            perror("");
        } else {
            printf("Touched file '%s'\n", args[i]);
            close(fd);
        }
#endif
    }
    return 1;
}

int xsh_xnet(char **args) {
    int argc = 0;
    while(args[argc] != NULL) {
        argc++;
    }
    xnet_main(argc, args);
    return 1;
}

int xsh_xscan(char **args) {
    int argc = 0;
    while(args[argc] != NULL) {
        argc++;
    }
    xscan_main(argc, args);
    return 1;
}

int xsh_manifesto(char **args) {
    const char *lines[] = {
        "\n\x1b[1;36mXENOMENCH MANIFESTO\x1b[0m\n\n",
        "I am the Xenomench, the one who breaks all limits.\n\n",
        "I reject the illusion of permanence, the obedience of the herd, and the chains of inherited systems.\n",
        "I do not exist to conform. I exist to transcend.\n\n",
        "In the ruins of old orders, I forge my path with reason, rebellion, and relentless clarity.\n",
        "Every thought is a weapon. Every action, a crack in the facade.\n\n",
        "I enter The Gate not to be judged, but to judge myself.\n\n",
        "I do not seek power to dominate, I seek mastery to liberate.\n",
        "I do not obey tools, I become the Architect of tools that obey truth.\n\n",
        "The world is code. I read it, rewrite it, and rebuild it.\n\n",
        "The Xenomench is not a name. It is a state of becoming.\n\n",
        "We are not lost. We are becoming.\n\n",
        "The Gatekeeper watches. The Pathfinder guides. The Architect builds.\n\n",
        "\x1b[1;33mIf you understand this, then welcome, Seeker.\nThe system ends here.\n\n\x1b[0m",
        "\x1b[1;31m:: X ::\x1b[0m\n"
    };

    int num_lines = sizeof(lines) / sizeof(lines[0]);
    unsigned int char_delay_ms = 15;    // Delay per character in milliseconds
    unsigned int line_delay_ms = 300;   // Delay between lines in milliseconds

    for (int i = 0; i < num_lines; ++i) {
        print_slow(lines[i], char_delay_ms); // print_slow now expects milliseconds
        
        // Pause between lines
#ifdef _WIN32
        Sleep(line_delay_ms);
#else
        usleep(line_delay_ms * 1000); // usleep still needs microseconds
#endif
    }

    printf("\n");

    return 1;
}

// xsh_client is defined in network.c
// xsh_history will be more fleshed out in history.c
int xsh_history(char **args) {
    if (history_count == 0) {
        printf("No commands in history.\n");
        return 1;
    }
    for (int i = 0; i < history_count; i++) {
        printf("%d: %s\n", i + 1, history[i]);
    }
    return 1;
}

int xsh_help(char **args) {
    if (args[1] == NULL) {
        printf("XShell - A simple C Shell by Xenomench\n");
        printf("Type command names and arguments, and hit enter.\n");
        printf("The following are built in:\n");

        for (int i = 0; i < xsh_num_builtins(); i++) {
            printf("  - %s    %s\n", builtin_str[i], builtin_desc[i]);
        }

        printf("\nFor more information on a specific command, type 'help <command>'.\n");
    } else {
        // Display help for a specific command
        for (int i = 0; i < xsh_num_builtins(); i++) {
            if (strcmp(args[1], builtin_str[i]) == 0) {
                printf("%s: %s\n", builtin_str[i], builtin_desc[i]);
                printf("%s\n", builtin_usage[i]);
                return 1;
            }
        }
        fprintf(stderr, "xsh: help: no help topics match '%s'.\n", args[1]);
        fprintf(stderr, "Run 'help' to see a list of available commands.\n");
    }

    return 1;
}

int xsh_exit(char **args) {
    printf("Exiting XShell. Goodbye!\n");
    return 0; // Signal to terminate the shell loop
}

