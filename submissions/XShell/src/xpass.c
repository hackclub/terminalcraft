#ifdef _WIN32
#define _CRT_RAND_S // Required for rand_s() on Windows
#endif
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <ctype.h>
#include <math.h>

#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#include <fcntl.h>
#endif

#include "xpass.h"

// Define colors
#define COLOR_RESET "\x1b[0m"
#define COLOR_RED "\x1b[31m"
#define COLOR_GREEN "\x1b[32m"
#define COLOR_YELLOW "\x1b[33m"
#define COLOR_BLUE "\x1b[36m"
#define COLOR_BOLD_GREEN "\x1b[1;32m"


// Custom log2 function for cross-platform compatibility
static double xsh_log2(double x) {
    return log(x) / log(2.0);
}

// Platform-independent secure random number generation
static int secure_random(unsigned int max) {
#ifdef _WIN32
    unsigned int num;
    rand_s(&num);
    return num % max;
#else
    unsigned int num;
    int fd = open("/dev/urandom", O_RDONLY);
    if (fd != -1) {
        read(fd, &num, sizeof(num));
        close(fd);
        return num % max;
    }
    // Fallback to less secure method
    return rand() % max;
#endif
}

static void calculate_entropy(const char *password);
static void print_xpass_usage(void);
static void generate_password(int length, int use_upper, int use_lower, int use_digits, int use_symbols);
static void handle_gen(char **args);
static void handle_check(char **args);

static void calculate_entropy(const char *password) {
    if (password == NULL || *password == '\0') {
        printf("Password is empty. Entropy: 0 bits (Extremely Weak)\n");
        return;
    }

    int length = strlen(password);
    int pool_size = 0;
    int has_lower = 0, has_upper = 0, has_digit = 0, has_symbol = 0;

    for (int i = 0; i < length; i++) {
        if (islower(password[i])) has_lower = 1;
        else if (isupper(password[i])) has_upper = 1;
        else if (isdigit(password[i])) has_digit = 1;
        else has_symbol = 1;
    }

    if (has_lower) pool_size += 26;
    if (has_upper) pool_size += 26;
    if (has_digit) pool_size += 10;
    if (has_symbol) pool_size += 32;

    if (pool_size == 0) {
        printf("Could not determine character pool. Entropy: 0 bits.\n");
        return;
    }

    double entropy = length * (xsh_log2(pool_size));

    printf("Password: '%.*s...'\n", length > 4 ? 4 : length, password);
    printf("Length: %d\n", length);
    printf("Character Pool Size (N): %d\n", pool_size);
    printf("Entropy (E = L * log2(N)): %.2f bits\n", entropy);
    printf("Strength: ");

    if (entropy < 28) printf("%sVery Weak%s\n", COLOR_RED, COLOR_RESET);
    else if (entropy < 36) printf("%sWeak%s\n", COLOR_RED, COLOR_RESET);
    else if (entropy < 60) printf("%sModerate%s\n", COLOR_YELLOW, COLOR_RESET);
    else if (entropy < 128) printf("%sStrong%s\n", COLOR_GREEN, COLOR_RESET);
    else printf("%sVery Strong%s\n", COLOR_BLUE, COLOR_RESET);
}

static void generate_password(int length, int use_upper, int use_lower, int use_digits, int use_symbols) {
    const char *LOWERCASE = "abcdefghijklmnopqrstuvwxyz";
    const char *UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const char *DIGITS = "0123456789";
    const char *SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?";
    
    char char_pool[128] = {0};
    char *password;

    if (use_lower) strcat(char_pool, LOWERCASE);
    if (use_upper) strcat(char_pool, UPPERCASE);
    if (use_digits) strcat(char_pool, DIGITS);
    if (use_symbols) strcat(char_pool, SYMBOLS);

    if (strlen(char_pool) == 0) {
        fprintf(stderr, "xpass: gen: Cannot generate password. All character sets are disabled.\n");
        return;
    }

    password = (char*)malloc(length + 1);
    if (!password) {
        fprintf(stderr, "xpass: gen: Memory allocation failed.\n");
        return;
    }

    #ifdef _WIN32
    // Windows-specific initialization for random
    #else
    // Seed for fallback method
    srand((unsigned int)time(NULL));
    #endif

    int pool_len = strlen(char_pool);
    for (int i = 0; i < length; i++) {
        password[i] = char_pool[secure_random(pool_len)];
    }
    password[length] = '\0';

    printf("Generated Password: %s%s%s\n", COLOR_BOLD_GREEN, password, COLOR_RESET);
    calculate_entropy(password);
    
    free(password);
}

static void handle_gen(char **args) {
    int length = 16;
    int use_upper = 1, use_lower = 1, use_digits = 1, use_symbols = 1;

    for (int i = 0; args[i] != NULL; i++) {
        if (strcmp(args[i], "--no-upper") == 0) use_upper = 0;
        else if (strcmp(args[i], "--no-lower") == 0) use_lower = 0;
        else if (strcmp(args[i], "--no-digits") == 0) use_digits = 0;
        else if (strcmp(args[i], "--no-symbols") == 0) use_symbols = 0;
        else {
            int num = atoi(args[i]);
            if (num > 0 && num <= 256) {
                length = num;
            } else if (num > 256) {
                fprintf(stderr, "xpass: gen: Max length is 256. Using default 16.\n");
            }
        }
    }
    generate_password(length, use_upper, use_lower, use_digits, use_symbols);
}

static void handle_check(char **args) {
    if (args[0] == NULL) {
        fprintf(stderr, "xpass: check: missing password to check.\n");
        print_xpass_usage();
        return;
    }
    calculate_entropy(args[0]);
}

static void print_xpass_usage(void) {
    printf("xpass – Password Strength Analyzer + Generator\n");
    printf("Usage: xpass <command> [options]\n\n");
    printf("Commands:\n");
    printf("  gen [length] [flags]   Generate a new password.\n");
    printf("                         Default length: 16. Max: 256.\n");
    printf("                         Flags:\n");
    printf("                           --no-upper    Exclude uppercase letters.\n");
    printf("                           --no-lower    Exclude lowercase letters.\n");
    printf("                           --no-digits   Exclude digits.\n");
    printf("                           --no-symbols  Exclude symbols.\n\n");
    printf("  check <password>       Check the strength of a given password by its entropy.\n\n");
    printf("  help                   Show this help message.\n");
}

/**
 * @brief Password generator and strength analyzer
 * 
 * @param args Command line arguments
 * @return int Status code (1 for success)
 */
int xsh_xpass(char **args) {
    if (args[1] == NULL || strcmp(args[1], "help") == 0) {
        print_xpass_usage();
    } else if (strcmp(args[1], "gen") == 0) {
        handle_gen(args + 2);
    } else if (strcmp(args[1], "check") == 0) {
        handle_check(args + 2);
    } else {
        fprintf(stderr, "xpass: unknown command '%s'. Use 'xpass help' for usage.\n", args[1]);
    }
    return 1;
}