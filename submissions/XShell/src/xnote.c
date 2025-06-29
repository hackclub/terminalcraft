#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// --- Platform-specific includes ---
#ifdef _WIN32
#include <windows.h>
#else // POSIX
#include <unistd.h>
#include <termios.h>
#include <dirent.h>
#endif

// --- Encryption includes ---
// OpenSSL dependency removed for simplicity.
// WARNING: The encryption implemented is a simple XOR cipher based on the user's
// password. It is NOT cryptographically secure and should not be used for
// sensitive data. This change is for demonstration and ease of compilation only.

// --- Project includes ---
#include "xnote.h"
#include "xsh.h"

// --- Defines for Encryption ---
#define BUF_SIZE 4096

// --- Forward Declarations ---
static void get_note_path(const char *name, char *path_buffer, size_t buffer_size);
static void get_password(const char *prompt, char *password, size_t size);
static int encrypt_decrypt_file(FILE *in_file, FILE *out_file, const unsigned char *password, int do_encrypt);

/**
 * @brief Handles 'xnote add <name> "content..."'
 */
static int handle_xnote_add(char **args) {
    if (args[2] == NULL || args[3] == NULL) {
        fprintf(stderr, "xsh: xnote: Usage: xnote add <name> \"<content>\"\n");
        return 1;
    }
    char note_path[XSH_MAXLINE];
    get_note_path(args[2], note_path, sizeof(note_path));
    FILE *fp = fopen(note_path, "w");
    if (fp == NULL) {
        perror("xsh: xnote: failed to open file for writing");
        return 1;
    }
    for (int i = 3; args[i] != NULL; i++) {
        fprintf(fp, "%s%s", args[i], (args[i+1] != NULL ? " " : ""));
    }
    fclose(fp);
    printf("Note '%s' added. Use 'xnote lock %s' to encrypt it.\n", args[2], args[2]);
    return 1;
}

/**
 * @brief Handles 'xnote lock <name>'
 */
static int handle_xnote_lock(char **args) {
    if (args[2] == NULL) {
        fprintf(stderr, "xsh: xnote: Usage: xnote lock <name>\n");
        return 1;
    }
    char password[XSH_MAXLINE];
    get_password("Enter password to lock note: ", password, sizeof(password));
    if (strlen(password) == 0) {
        fprintf(stderr, "xsh: xnote: password cannot be empty.\n");
        return 1;
    }

    char note_path[XSH_MAXLINE], temp_path[XSH_MAXLINE + 5];
    get_note_path(args[2], note_path, sizeof(note_path));
    snprintf(temp_path, sizeof(temp_path), "%s.temp", note_path);

    FILE *input_fp = fopen(note_path, "rb");
    if (!input_fp) {
        perror("xsh: xnote: could not open note file to lock");
        return 1;
    }
    FILE *output_fp = fopen(temp_path, "wb");
    if (!output_fp) {
        perror("xsh: xnote: could not create temp file");
        fclose(input_fp);
        return 1;
    }

    if (encrypt_decrypt_file(input_fp, output_fp, (unsigned char*)password, 1) != 0) {
        fprintf(stderr, "xsh: xnote: encryption failed.\n");
        fclose(input_fp);
        fclose(output_fp);
        remove(temp_path);
        return 1;
    }

    fclose(input_fp);
    fclose(output_fp);
    remove(note_path);
    rename(temp_path, note_path);
    printf("Note '%s' has been locked (encrypted).\n", args[2]);
    return 1;
}

/**
 * @brief Handles 'xnote view <name>'
 */
static int handle_xnote_view(char **args) {
    if (args[2] == NULL) {
        fprintf(stderr, "xsh: xnote: Usage: xnote view <name>\n");
        return 1;
    }
    char password[XSH_MAXLINE];
    get_password("Enter password to view note: ", password, sizeof(password));
    if (strlen(password) == 0) {
        fprintf(stderr, "xsh: xnote: password cannot be empty.\n");
        return 1;
    }

    char note_path[XSH_MAXLINE];
    get_note_path(args[2], note_path, sizeof(note_path));
    FILE *fp = fopen(note_path, "rb");
    if (!fp) {
        perror("xsh: xnote: could not open note file to view");
        return 1;
    }

    printf("--- Viewing Note: %s ---\n", args[2]);
    if (encrypt_decrypt_file(fp, stdout, (unsigned char*)password, 0) != 0) {
        fprintf(stderr, "\n--- Decryption failed: Incorrect password or corrupted file. ---\n");
    } else {
        printf("\n--- End of Note ---\n");
    }
    fclose(fp);
    return 1;
}

/**
 * @brief Handles 'xnote delete <name>'
 */
static int handle_xnote_delete(char **args) {
    if (args[2] == NULL) {
        fprintf(stderr, "xsh: xnote: Usage: xnote delete <name>\n");
        return 1;
    }
    char note_path[XSH_MAXLINE];
    get_note_path(args[2], note_path, sizeof(note_path));
    if (remove(note_path) == 0) {
        printf("Note '%s' deleted.\n", args[2]);
    } else {
        perror("xsh: xnote: failed to delete note");
    }
    return 1;
}

/**
 * @brief Handles 'xnote list'
 */
static int handle_xnote_list(char **args) {
    printf("Available notes:\n");
#ifdef _WIN32
    WIN32_FIND_DATA fd;
    HANDLE hFind = FindFirstFile("*.xdata", &fd);
    if (hFind == INVALID_HANDLE_VALUE) {
        printf("  (no notes found)\n");
        return 1;
    }
    do {
        char *dot = strrchr(fd.cFileName, '.');
        if (dot && strcmp(dot, ".xdata") == 0) {
            *dot = '\0';
            printf("  - %s\n", fd.cFileName);
        }
    } while (FindNextFile(hFind, &fd) != 0);
    FindClose(hFind);
#else // POSIX
    DIR *d = opendir(".");
    struct dirent *dir;
    int found = 0;
    if (d) {
        while ((dir = readdir(d)) != NULL) {
            char *dot = strrchr(dir->d_name, '.');
            if (dot && strcmp(dot, ".xdata") == 0) {
                *dot = '\0';
                printf("  - %s\n", dir->d_name);
                found = 1;
            }
        }
        closedir(d);
    }
    if (!found) printf("  (no notes found)\n");
#endif
    return 1;
}



int xsh_xnote(char **args) {
    if (args[1] == NULL || strcmp(args[1], "help") == 0) {
        fprintf(stderr, "xnote: Encrypted Note Keeper\nUsage: xnote <command> [options]\nCommands:\n");
        fprintf(stderr, "  add <name> \"<content>\" - Create a new note.\n");
        fprintf(stderr, "  view <name>             - View a decrypted note.\n");
        fprintf(stderr, "  lock <name>             - Encrypt a note with a password.\n");
        fprintf(stderr, "  list                    - List all available notes.\n");
        fprintf(stderr, "  delete <name>           - Delete a note.\n");
        return 1;
    }
    if (strcmp(args[1], "add") == 0) return handle_xnote_add(args);
    if (strcmp(args[1], "view") == 0) return handle_xnote_view(args);
    if (strcmp(args[1], "lock") == 0) return handle_xnote_lock(args);
    if (strcmp(args[1], "list") == 0) return handle_xnote_list(args);
    if (strcmp(args[1], "delete") == 0) return handle_xnote_delete(args);
    
    fprintf(stderr, "xsh: xnote: unknown subcommand '%s'. Use 'xnote help'.\n", args[1]);
    return 1;
}

// --- Helper Functions ---

static void get_note_path(const char *name, char *path_buffer, size_t buffer_size) {
    snprintf(path_buffer, buffer_size, "%s.xdata", name);
}

/**
 * @brief Securely reads a password from the console without echoing.
 */
static void get_password(const char *prompt, char *password, size_t size) {
    printf("%s", prompt);
    fflush(stdout);
#ifdef _WIN32
    HANDLE hStdin = GetStdHandle(STD_INPUT_HANDLE);
    DWORD mode = 0;
    GetConsoleMode(hStdin, &mode);
    SetConsoleMode(hStdin, mode & (~ENABLE_ECHO_INPUT));
#else
    struct termios oldt, newt;
    tcgetattr(STDIN_FILENO, &oldt);
    newt = oldt;
    newt.c_lflag &= ~ECHO;
    tcsetattr(STDIN_FILENO, TCSANOW, &newt);
#endif
    if (fgets(password, size, stdin) != NULL) {
        password[strcspn(password, "\r\n")] = 0;
    } else {
        password[0] = '\0';
    }
#ifdef _WIN32
    SetConsoleMode(hStdin, mode);
#else
    tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
#endif
    printf("\n");
}

/**
 * @brief Encrypts or decrypts a file using a simple password-based XOR cipher.
 * This is NOT a secure method of encryption.
 * @param in_file Input file stream.
 * @param out_file Output file stream.
 * @param password The user's password, used as the XOR key.
 * @param do_encrypt Unused, as XOR is a symmetric operation.
 * @return 0 on success, -1 on failure.
 */
static int encrypt_decrypt_file(FILE *in_file, FILE *out_file, const unsigned char *password, int do_encrypt) {
    (void)do_encrypt; // Suppress unused parameter warning
    int c;
    size_t i = 0;
    size_t key_len = strlen((const char *)password);

    if (key_len == 0) {
        fprintf(stderr, "Error: Password cannot be empty for encryption/decryption.\n");
        return -1;
    }

    while ((c = fgetc(in_file)) != EOF) {
        fputc(c ^ password[i % key_len], out_file);
        i++;
    }
    
    return 0;
}