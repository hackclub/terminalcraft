#include "utils.h"
#include <stdio.h>
#include <string.h>

#ifdef _WIN32
#include <windows.h> // For Sleep(), GetUserName(), FindFirstFile, etc.
#include <lmcons.h>  // For UNLEN
#include <direct.h>  // For rmdir on some MinGW versions, though RemoveDirectory is preferred
#else
#include <unistd.h>  // For gethostname(), getpwuid(), getuid(), usleep(), rmdir, remove
#include <sys/utsname.h> // For uname()
#include <pwd.h>     // For getpwuid()
#include <dirent.h>  // For opendir, readdir, closedir
#include <sys/stat.h> // For lstat, S_ISDIR
#endif

// Implementation of utility functions

void print_slow(const char *text, unsigned int delay_ms) {
    for (const char *p = text; *p != '\0'; p++) {
        putchar(*p);
        fflush(stdout);
#ifdef _WIN32
        Sleep(delay_ms);
#else
        usleep(delay_ms * 1000); // Convert ms to microseconds for usleep
#endif
    }
}

char* build_prompt(void) {
    static char prompt[XSH_MAXLINE];
    char cwd[XSH_MAXLINE];
    char short_cwd[XSH_MAXLINE];
    char username[XSH_MAXLINE];
    
    // Get username
#ifdef _WIN32
    DWORD username_size = XSH_MAXLINE;
    if (!GetUserNameA(username, &username_size)) {
        strcpy(username, "user");
    }
#else
    char *user_env = getenv("USER");
    if (user_env) {
        strncpy(username, user_env, XSH_MAXLINE - 1);
        username[XSH_MAXLINE - 1] = '\0';
    } else {
        strcpy(username, "user");
    }
#endif
    
    // Get current directory
#ifdef _WIN32
    if (_getcwd(cwd, sizeof(cwd)) == NULL) {
        strcpy(cwd, "unknown");
    }
#else
    if (getcwd(cwd, sizeof(cwd)) == NULL) {
        strcpy(cwd, "unknown");
    }
#endif
    
    // Extract just the current folder name for a cleaner prompt (cross-platform)
    char *last_slash = strrchr(cwd, '/');
    char *last_backslash = strrchr(cwd, '\\');
    char *separator = NULL;

    // Find the last path separator by comparing pointer addresses
    if (last_slash > last_backslash) {
        separator = last_slash;
    } else {
        separator = last_backslash;
    }

    if (separator != NULL && *(separator + 1) != '\0') {
        // If a separator is found and it's not the last character, use the part after it
        strcpy(short_cwd, separator + 1);
    } else {
        // Otherwise (no separator, or it's the last char like "C:\\"), use the full path
        strcpy(short_cwd, cwd);
    }
    
    sprintf(prompt, "\x1b[1;36mxsh\x1b[0m@\x1b[1;35m%s\x1b[0m:\x1b[32m%s\x1b[0m:\x1b[33m%d\x1b[0m> ", 
            username, short_cwd, history_count+1);
    
    return prompt;
}

// Helper function for case-insensitive strstr
char *strcasestr_custom(const char *haystack, const char *needle) {
    if (!haystack || !needle) return NULL;
    if (!*needle) return (char *)haystack; // Empty needle matches everything

    while (*haystack) {
        const char *h_ptr = haystack;
        const char *n_ptr = needle;
        // Compare characters case-insensitively
        while (*h_ptr && *n_ptr && (tolower((unsigned char)*h_ptr) == tolower((unsigned char)*n_ptr))) {
            h_ptr++;
            n_ptr++;
        }
        // If needle is exhausted, it\'s a match
        if (!*n_ptr) {
            return (char *)haystack; // Return start of match in original haystack
        }
        haystack++; // Move to next character in haystack
    }
    return NULL; // No match found
}

// Helper function to process a single stream (file or stdin) for grep
void process_grep_stream(FILE *fp, const char *pattern, int case_insensitive, const char *filename_to_print) {
    char line[XSH_MAXLINE];

    while (fgets(line, sizeof(line), fp)) {
        char *match_found = NULL;
        if (case_insensitive) {
            match_found = strcasestr_custom(line, pattern);
        } else {
            match_found = strstr(line, pattern);
        }

        if (match_found) {
            if (filename_to_print) { // Only print filename if it's provided (i.e., multiple files mode)
                printf("%s:", filename_to_print);
            }
            fputs(line, stdout);
        }
    }
}

// Function to recursively remove files and directories
int remove_recursively_internal(const char *path) {
#ifndef _WIN32 // POSIX implementation
    struct stat path_stat;
    // Use lstat to get info about the path itself (e.g. a symlink, not what it points to)
    if (lstat(path, &path_stat) != 0) {
        fprintf(stderr, "xsh: rm: cannot stat '%s': ", path);
        perror("");
        return -1;
    }

    if (S_ISDIR(path_stat.st_mode)) { // It's a directory
        DIR *dir = opendir(path);
        if (!dir) {
            fprintf(stderr, "xsh: rm: cannot open directory '%s': ", path);
            perror("");
            return -1;
        }
        struct dirent *entry;
        int ret = 0; // Assume success initially for directory content removal
        char entry_path[XSH_MAXLINE]; // XSH_MAXLINE should be defined in xsh.h, included via utils.h

        while ((entry = readdir(dir)) != NULL) {
            if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
                continue;
            }
            snprintf(entry_path, sizeof(entry_path), "%s/%s", path, entry->d_name);
            if (remove_recursively_internal(entry_path) != 0) {
                ret = -1; // Mark error, but try to continue deleting other files/dirs
            }
        }
        closedir(dir);

        if (ret == 0) { // Only try to remove dir if all contents were removed successfully
            if (rmdir(path) != 0) {
                fprintf(stderr, "xsh: rm: cannot remove directory '%s': ", path);
                perror("");
                return -1;
            }
        } else {
            // Error message for content removal already printed by recursive calls or above.
            // We can add a specific message here if needed, e.g.:
            // fprintf(stderr, "xsh: rm: failed to remove all contents of directory '%s', cannot remove directory itself\\n", path);
            return -1; // Error occurred while deleting contents
        }
    } else { // It's a file or symlink
        if (remove(path) != 0) { // remove() handles files and symlinks
            fprintf(stderr, "xsh: rm: cannot remove '%s': ", path);
            perror("");
            return -1;
        }
    }
    return 0; // Success

#else // Windows implementation
    WIN32_FIND_DATA findFileData;
    HANDLE hFind = INVALID_HANDLE_VALUE;
    char search_path[XSH_MAXLINE];
    char entry_path[XSH_MAXLINE]; // XSH_MAXLINE from xsh.h
    DWORD dwAttrs = GetFileAttributes(path);

    if (dwAttrs == INVALID_FILE_ATTRIBUTES) {
        fprintf(stderr, "xsh: rm: cannot get attributes for '%s' (Error %lu)\\n", path, GetLastError());
        return -1;
    }

    if (dwAttrs & FILE_ATTRIBUTE_DIRECTORY) { // It's a directory
        // Ensure path is not "." or ".." before trying to delete its contents,
        // though GetFileAttributes should handle this.
        // Construct search path for directory contents
        snprintf(search_path, sizeof(search_path), "%s\\\\*", path);

        hFind = FindFirstFile(search_path, &findFileData);
        if (hFind == INVALID_HANDLE_VALUE) {
            if (GetLastError() == ERROR_FILE_NOT_FOUND) {
                // Directory is empty, proceed to remove it
            } else {
                fprintf(stderr, "xsh: rm: error finding first file in '%s' (Error %lu)\\n", path, GetLastError());
                return -1; // Error other than empty directory
            }
        }
        
        int ret = 0; // Assume success for content removal
        if (hFind != INVALID_HANDLE_VALUE) { // If directory is not empty or FindFirstFile didn't fail for other reasons
            do {
                if (strcmp(findFileData.cFileName, ".") == 0 || strcmp(findFileData.cFileName, "..") == 0) {
                    continue;
                }
                snprintf(entry_path, sizeof(entry_path), "%s\\\\%s", path, findFileData.cFileName);
                if (remove_recursively_internal(entry_path) != 0) {
                    ret = -1; // Mark error, but try to continue
                }
            } while (FindNextFile(hFind, &findFileData) != 0);
            FindClose(hFind);
        }


        if (ret == 0) { // Only try to remove dir if all contents were removed successfully
            if (!RemoveDirectory(path)) {
                fprintf(stderr, "xsh: rm: cannot remove directory '%s' (Error %lu)\\n", path, GetLastError());
                return -1;
            }
        } else {
            // fprintf(stderr, "xsh: rm: failed to remove all contents of directory '%s'\\n", path);
            return -1; // Error occurred while deleting contents
        }
    } else { // It's a file (or reparse point not handled as directory)
        if (!DeleteFile(path)) {
            fprintf(stderr, "xsh: rm: cannot remove file '%s' (Error %lu)\\n", path, GetLastError());
            return -1;
        }
    }
    return 0; // Success
#endif
}

int create_file_with_content(const char *path, const char *content) {
    if (path == NULL || content == NULL) {
        fprintf(stderr, "xsh: xproj: create_file_with_content: path or content is NULL\n");
        return -1;
    }

    FILE *fp = fopen(path, "w");
    if (fp == NULL) {
        fprintf(stderr, "xsh: xproj: cannot create file '%s': ", path);
        perror("fopen");
        return -1;
    }
    fprintf(fp, "%s", content);
    fclose(fp);
    return 0;
}