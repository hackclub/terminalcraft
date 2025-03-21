#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <stdarg.h>
#include <time.h>
#include <errno.h> // For errno

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
/* #define _WIN32_WINNT 0x0600 */
#include <windows.h> // Windows API
#include <conio.h>   // Windows-specific header for getch()
#include <wincon.h>  // For CONSOLE_SCREEN_BUFFER_INFO
#include <winbase.h>
#include <io.h>    // For _setmode()
#include <fcntl.h> // For _O_U16TEXT
#include <unistd.h>
#include <direct.h> // For _chdir()
#else
#include <termios.h>   // Terminal control for Linux
#include <unistd.h>    // POSIX API
#include <sys/ioctl.h> // For ioctl() and struct winsize
#include <fcntl.h>     // For fcntl()
#include <sys/stat.h>  // For struct stat
#include <sys/select.h>
#endif

#include "functions.h"
#include "log.h"

// Cross-platform implementation of character input without echo
char getCharNoEcho()
{
#ifdef _WIN32
    // Windows implementation using conio.h
    return getch();
#else
    // Linux implementation using termios
    struct termios oldattr, newattr;
    char ch;

    // Get current terminal attributes
    tcgetattr(STDIN_FILENO, &oldattr);

    // Copy the old attributes to new attributes
    newattr = oldattr;

    // Disable echo and canonical mode (line buffering)
    newattr.c_lflag &= ~(ICANON | ECHO);

    // Set the new terminal attributes
    tcsetattr(STDIN_FILENO, TCSANOW, &newattr);

    // Read a character
    read(STDIN_FILENO, &ch, 1);

    // Restore old terminal attributes
    tcsetattr(STDIN_FILENO, TCSANOW, &oldattr);

    return ch;
#endif
}

/**
 * Displays a menu and gets user selection.
 *
 * @param title The title of the menu
 * @param options Array of option strings to display
 * @param optionCount Number of options
 * @param allowEsc Whether to allow ESC key for exit
 * @return The index of the selected option (0-based) or -1 if ESC was pressed
 */
int getMenuSelection(const char *title, const char **options, int optionCount, bool allowEsc)
{
    printf("\n%s\n", title);

    for (int i = 0; i < optionCount; i++)
    {
        printf("%d. %s\n", i + 1, options[i]);
    }

    char key;
    bool errorDisplayed = false;

    // Wait for a valid keypress
    printf("\n>>> ");
    fflush(stdout);

    while (1)
    {
        key = getCharNoEcho();

        // Check if key is a valid option number
        if (key >= '1' && key <= '0' + optionCount)
        {
            int selection = key - '0';
            printf("%c\n", key);  // Echo the valid key
            return selection - 1; // Return 0-based index
        }
        else if (allowEsc && key == 27)
        { // Escape key
            printf("ESC\n");
            return -1;
        }
        else
        {
            // Clear previous error if there was one
            if (errorDisplayed)
            {
                printf("\r                           \r"); // Clear the line
            }
            printf("\nInvalid key: %c", key);
            // Move cursor one line up
            printf("\033[A");
            printf("\r>>> ");
            fflush(stdout);
            errorDisplayed = true;
        }
    }
}

char *getString(const char *prompt)
{
    printf("%s", prompt);
    printf(">>> ");
    char *buffer = (char *)malloc(256);
    if (buffer == NULL)
    {
        return NULL;
    }
    fgets(buffer, 256, stdin);
    buffer[strcspn(buffer, "\n")] = 0; // Remove trailing newline
    return buffer;
}

/**
 * @brief Processes a given path and performs various checks and transformations based on the operating system.
 *
 * @param path The input path to be processed. It can be a relative or absolute path to either a file or directory.
 * @param mustExist A boolean flag indicating whether the path must exist.
 *                  If true, the function will check if the path exists.
 *                  If false, for files it will check if the parent directory exists.
 *                  For directories, it checks if the parent directory exists.
 * @param isDirectory A boolean flag indicating whether the path is expected to be a directory.
 *                   If true, the function will handle the path as a directory.
 *                   If false, the function will handle the path as a file.
 *
 * The function performs the following operations:
 * - Checks if the path is NULL or empty and returns NULL if it is.
 * - On Windows:
 *   - Replaces forward slashes with backslashes.
 *   - Removes enclosing quotes if present.
 *   - Resolves the path to an absolute path.
 *   - If mustExist=true: Checks if the path exists and returns NULL if it doesn't.
 *   - If mustExist=false: Checks if the parent directory exists (for file creation) and returns NULL if it doesn't.
 *   - Retrieves file attributes if the path exists.
 * - On Linux:
 *   - Removes enclosing quotes if present.
 *   - Resolves the path to an absolute path if it exists or mustExist is true.
 *   - If mustExist=true: Checks if the path exists and returns NULL if it doesn't.
 *   - If mustExist=false: Checks if the parent directory exists (for file creation) and returns NULL if it doesn't.
 *   - Retrieves file attributes if the path exists.
 *
 * Error messages are printed to the standard output in case of failures.
 *
 * @return A newly allocated string containing the processed path, or NULL if an error occurs.
 *         The caller is responsible for freeing the returned string.
 */
char *processPath(const char *path, bool mustExist, bool isDirectory)
{
    // Input validation
    if (path == NULL || strlen(path) == 0)
    {
        printf("Error: Path is NULL or empty\n");
        return NULL;
    }

    // Allocate and initialize buffer
    char *buffer = (char *)malloc(strlen(path) + 1);
    if (buffer == NULL)
    {
        printf("Error: Memory allocation failed\n");
        return NULL;
    }
    strcpy(buffer, path);

    // Remove enclosing quotes if present
    if ((buffer[0] == '\"' && buffer[strlen(buffer) - 1] == '\"') ||
        (buffer[0] == '\'' && buffer[strlen(buffer) - 1] == '\''))
    {
        buffer[strlen(buffer) - 1] = '\0';
        memmove(buffer, buffer + 1, strlen(buffer));
    }

#ifdef _WIN32
    // Windows path processing

    // Replace forward slashes with backslashes
    for (int i = 0; buffer[i]; i++)
    {
        if (buffer[i] == '/')
            buffer[i] = '\\';
    }

    // Convert to absolute path
    char *resolvedPath = _fullpath(NULL, buffer, 0);
    if (resolvedPath == NULL)
    {
        printf("Error: Failed to resolve path\n");
        free(buffer);
        return NULL;
    }

    // Update buffer with resolved path
    free(buffer);
    buffer = (char *)malloc(strlen(resolvedPath) + 1);
    if (buffer == NULL)
    {
        printf("Error: Memory allocation failed\n");
        free(resolvedPath);
        return NULL;
    }
    strcpy(buffer, resolvedPath);
    free(resolvedPath);

    // Handle existence checks
    if (mustExist)
    {
        // Path must exist
        if (_access(buffer, 0) == -1)
        {
            printf("Path does not exist: %s\n", buffer);
            free(buffer);
            return NULL;
        }

        // If it's supposed to be a directory, verify that
        if (isDirectory)
        {
            DWORD attributes = GetFileAttributesA(buffer);
            if (attributes == INVALID_FILE_ATTRIBUTES)
            {
                printf("Error: Failed to get file attributes\n");
                free(buffer);
                return NULL;
            }

            if (!(attributes & FILE_ATTRIBUTE_DIRECTORY))
            {
                printf("Error: Path is not a directory: %s\n", buffer);
                free(buffer);
                return NULL;
            }
        }
    }
    else
    {
        // Path doesn't need to exist
        if (isDirectory)
        {
            // For directories, check if parent directory exists (if this is not root)
            char *lastSlash = strrchr(buffer, '\\');
            if (lastSlash != NULL && lastSlash != buffer) // Not root directory
            {
                char lastChar = *lastSlash;
                *lastSlash = '\0';

                if (_access(buffer, 0) == -1)
                {
                    printf("Parent directory does not exist: %s\n", buffer);
                    free(buffer);
                    return NULL;
                }

                *lastSlash = lastChar;
            }
        }
        else
        {
            // For files, check if parent directory exists
            char *lastSlash = strrchr(buffer, '\\');
            if (lastSlash != NULL)
            {
                char lastChar = *lastSlash;
                *lastSlash = '\0';

                if (_access(buffer, 0) == -1)
                {
                    printf("Directory does not exist: %s\n", buffer);
                    free(buffer);
                    return NULL;
                }

                *lastSlash = lastChar;
            }
        }
    }

#elif __linux__
    // Linux path processing

    if (mustExist || access(buffer, F_OK) != -1)
    {
        // Path exists or must exist
        char *resolvedPath = realpath(buffer, NULL);
        if (resolvedPath == NULL)
        {
            printf("Error: Failed to resolve path\n");
            free(buffer);
            return NULL;
        }

        free(buffer);
        buffer = resolvedPath;

        // Check existence if required
        if (mustExist && access(buffer, F_OK) == -1)
        {
            printf("Path does not exist: %s\n", buffer);
            free(buffer);
            return NULL;
        }

        // Verify it's a directory if needed
        if (isDirectory && access(buffer, F_OK) != -1)
        {
            struct stat pathStat;
            if (stat(buffer, &pathStat) == -1)
            {
                printf("Error: Failed to get file attributes\n");
                free(buffer);
                return NULL;
            }

            if (!S_ISDIR(pathStat.st_mode))
            {
                printf("Error: Path is not a directory: %s\n", buffer);
                free(buffer);
                return NULL;
            }
        }
    }
    else
    {
        // Non-existent path handling

        if (isDirectory)
        {
            // For directories, check if parent directory exists
            char *lastSlash = strrchr(buffer, '/');
            if (lastSlash != NULL && lastSlash != buffer) // Not root
            {
                char lastChar = *lastSlash;
                *lastSlash = '\0';

                // Empty directory means current directory
                if (strlen(buffer) == 0)
                    strcpy(buffer, ".");

                if (access(buffer, F_OK) == -1)
                {
                    printf("Parent directory does not exist: %s\n", buffer);
                    free(buffer);
                    return NULL;
                }

                *lastSlash = lastChar;
            }
        }
        else
        {
            // For files, check if parent directory exists
            char *lastSlash = strrchr(buffer, '/');
            if (lastSlash != NULL)
            {
                char lastChar = *lastSlash;
                *lastSlash = '\0';

                // Empty directory means current directory
                if (strlen(buffer) == 0)
                    strcpy(buffer, ".");

                if (access(buffer, F_OK) == -1)
                {
                    printf("Directory does not exist: %s\n", buffer);
                    free(buffer);
                    return NULL;
                }

                *lastSlash = lastChar;
            }
        }

        // Convert to absolute path if relative
        if (buffer[0] != '/')
        {
            char *cwd = getcwd(NULL, 0);
            if (cwd == NULL)
            {
                printf("Error: Failed to get current working directory\n");
                free(buffer);
                return NULL;
            }

            char *absolutePath = malloc(strlen(cwd) + strlen(buffer) + 2);
            if (absolutePath == NULL)
            {
                printf("Error: Memory allocation failed\n");
                free(buffer);
                free(cwd);
                return NULL;
            }

            sprintf(absolutePath, "%s/%s", cwd, buffer);
            free(buffer);
            free(cwd);
            buffer = absolutePath;
        }
    }
#endif

    return buffer;
}

bool fileExists(const char *filename)
{
    FILE *file = fopen(filename, "r");
    if (file)
    {
        fclose(file);
        return true;
    }
    return false;
}

/**
 * @brief Improved version of readFileContent that handles various text encodings.
 *
 * This function automatically detects file encoding from BOM markers and
 * converts content to standard UTF-8/ASCII for consistent handling.
 *
 * @param filename The path to the file to be read.
 * @param contentLength A pointer to a size_t variable where the length of the
 *                      file content will be stored.
 * @param isBinary A boolean flag indicating whether to treat as binary (true)
 *                 or detect and convert encoding (false).
 * @return A pointer to the dynamically allocated string containing the file
 *         content, or NULL if an error occurs.
 */
char *readFileContent(const char *filename, size_t *contentLength, bool isBinary)
{
    // Always open in binary mode first to check for BOM
    FILE *file = fopen(filename, "rb");
    if (file == NULL)
    {
        printf("Error: File not found or cannot be opened: %s\n", filename);
        printf("Error message: %s\n", strerror(errno));
        return NULL;
    }

    // Get file size
    if (fseek(file, 0, SEEK_END) != 0)
    {
        printf("Error: Could not seek in file: %s\n", filename);
        fclose(file);
        return NULL;
    }
    long fileSize = ftell(file);
    if (fileSize < 0)
    {
        printf("Error: Could not determine file size: %s\n", filename);
        fclose(file);
        return NULL;
    }
    rewind(file); // Back to beginning

    // Allocate memory for file content plus null terminator
    char *content = (char *)malloc(fileSize + 1);
    if (content == NULL)
    {
        printf("Error: Memory allocation failed for file: %s\n", filename);
        fclose(file);
        return NULL;
    }

    // Read entire file at once
    size_t bytesRead = fread(content, 1, fileSize, file);
    if (bytesRead != (size_t)fileSize)
    {
        printf("Error: Could not read entire file: %s\n", filename);
        printf("Expected %ld bytes, got %zu bytes\n", fileSize, bytesRead);
        if (ferror(file))
        {
            printf("Error message: %s\n", strerror(errno));
        }
        free(content);
        fclose(file);
        return NULL;
    }

    // Null-terminate the buffer
    content[bytesRead] = '\0';
    fclose(file);

    // If binary mode requested, return as-is
    if (isBinary)
    {
        *contentLength = bytesRead;
        return content;
    }

    // Otherwise, detect encoding and convert if needed
    enum Encoding
    {
        ENC_ASCII,
        ENC_UTF8,
        ENC_UTF16LE,
        ENC_UTF16BE,
        ENC_UTF32LE,
        ENC_UTF32BE
    } encoding = ENC_ASCII;

    size_t skipBytes = 0;

    // Detect encoding from BOM
    if (bytesRead >= 2)
    {
        if (bytesRead >= 4 &&
            (unsigned char)content[0] == 0xFF &&
            (unsigned char)content[1] == 0xFE &&
            (unsigned char)content[2] == 0x00 &&
            (unsigned char)content[3] == 0x00)
        {
            encoding = ENC_UTF32LE;
            skipBytes = 4;
        }
        else if (bytesRead >= 4 &&
                 (unsigned char)content[0] == 0x00 &&
                 (unsigned char)content[1] == 0x00 &&
                 (unsigned char)content[2] == 0xFE &&
                 (unsigned char)content[3] == 0xFF)
        {
            encoding = ENC_UTF32BE;
            skipBytes = 4;
        }
        else if ((unsigned char)content[0] == 0xFF &&
                 (unsigned char)content[1] == 0xFE)
        {
            encoding = ENC_UTF16LE;
            skipBytes = 2;
        }
        else if ((unsigned char)content[0] == 0xFE &&
                 (unsigned char)content[1] == 0xFF)
        {
            encoding = ENC_UTF16BE;
            skipBytes = 2;
        }
        else if (bytesRead >= 3 &&
                 (unsigned char)content[0] == 0xEF &&
                 (unsigned char)content[1] == 0xBB &&
                 (unsigned char)content[2] == 0xBF)
        {
            encoding = ENC_UTF8;
            skipBytes = 3;
        }
    }

    // Convert to ASCII/UTF-8 if necessary
    char *convertedContent = NULL;

    if (encoding == ENC_ASCII || encoding == ENC_UTF8)
    {
        // Just skip the BOM if present
        if (skipBytes > 0)
        {
            convertedContent = strdup(content + skipBytes);
            free(content);
            content = convertedContent;
            *contentLength = bytesRead - skipBytes;
        }
        else
        {
            *contentLength = bytesRead;
        }
    }
    else if (encoding == ENC_UTF16LE)
    {
        // Convert UTF-16LE to ASCII/UTF-8
        size_t utf16Length = (bytesRead - skipBytes) / 2;
        convertedContent = (char *)malloc(utf16Length + 1);
        if (convertedContent)
        {
            // Simple conversion - just take every other byte
            size_t j = 0;
            for (size_t i = skipBytes; i < bytesRead; i += 2)
            {
                convertedContent[j++] = content[i];
            }
            convertedContent[j] = '\0';
            free(content);
            content = convertedContent;
            *contentLength = j;
        }
    }
    else if (encoding == ENC_UTF16BE)
    {
        // Convert UTF-16BE to ASCII/UTF-8
        size_t utf16Length = (bytesRead - skipBytes) / 2;
        convertedContent = (char *)malloc(utf16Length + 1);
        if (convertedContent)
        {
            // Simple conversion - just take every other byte
            size_t j = 0;
            for (size_t i = skipBytes + 1; i < bytesRead; i += 2)
            {
                convertedContent[j++] = content[i];
            }
            convertedContent[j] = '\0';
            free(content);
            content = convertedContent;
            *contentLength = j;
        }
    }
    else
    {
        // UTF-32 is complex - provide a placeholder and warning
        printf("Warning: UTF-32 encoding detected in file %s. Only ASCII content will be displayed.\n", filename);
        free(content);
        content = strdup("[UTF-32 content not properly displayed]");
        *contentLength = strlen(content);
    }

    return content;
}

char *getCurrentWorkingDirectory()
{
#ifndef _WIN32 // In Linux, the maximum path length is 4096 I think
#define MAX_PATH 4096
#endif
    char *buffer = (char *)malloc(MAX_PATH);
    if (buffer == NULL)
    {
        return NULL;
    }
#ifdef _WIN32
    if (_getcwd(buffer, 256) == NULL)
    {
        free(buffer);
        return NULL;
    }
#else
    if (getcwd(buffer, 256) == NULL)
    {
        free(buffer);
        return NULL;
    }
#endif
    return buffer;
}

// Add this function implementation:
void infoHandler(void)
{
    printTitle();
    printf("Terminal Encryption App\n");
    printf("=======================\n\n");
    printf("Version: 1.0\n");
    printf("Author: Moriaan Michiels\n\n");
    printf("This application provides encryption, decryption, key generation,\n");
    printf("and hashing functionality through a simple terminal interface.\n\n");
    printf("Supported Encryption Methods:\n");
    printf("- Public-private key\n");
    printf("- Symmetric key\n\n");
    printf("Supported Hashing Methods:\n");
    printf("- SHA-256\n");
    printf("- MD5\n\n");

    // Display system information
    printf("System Information:\n");
#ifdef _WIN32
    printf("- Platform: Windows\n");
#else
    printf("- Platform: Unix/Linux\n");
#endif
    printf("- Compiled on: %s\n", __DATE__);

    printf("\n");

    // Ask the user what part they want information about
    const char *infoOptions[] = {
        "Cryptographic Methods",
        "Key Generation",
        "Hashing",
        "Back"};
    int selected = getMenuSelection("Choose an information category:", infoOptions, sizeof(infoOptions) / sizeof(infoOptions[0]), true);
    if (selected == 3)
    {
        return; // Back to main menu
    }

    // Display information based on selection
    switch (selected)
    {
    case 0:
        printf("Cryptographic Methods Information:\n\n");
        printf("Public-private key cryptography (RSA):\n");
        printf("- Uses RSA 2048-bit with OAEP padding for security\n");
        printf("- Encrypt with public key, decrypt with private key\n");
        printf("- Suitable for small data and key exchange\n");
        printf("- Implementation uses OpenSSL's EVP_PKEY interface\n");
        printf("- Key pairs can be generated in the Key Generation menu\n\n");

        printf("Symmetric key cryptography (AES):\n");
        printf("- Uses AES-256-CBC with a derived key and initialization vector (IV)\n");
        printf("- Same key for both encryption and decryption\n");
        printf("- Key is derived from your passphrase using SHA-256\n");
        printf("- IV is randomly generated and stored with encrypted data\n");
        printf("- Efficient for encrypting larger amounts of data\n\n");

        printf("Input/Output Options:\n");
        printf("- Input from file or direct text entry\n");
        printf("- Output to file or displayed as text\n");
        printf("- Keys can be loaded from PEM files or entered as text\n\n");

        printf("Data formats:\n");
        printf("- All encrypted data includes necessary parameters (IV, padding)\n");
        printf("- Binary output contains raw encrypted bytes\n");
        printf("- Base64 encoding provides text representation of binary data\n");
        printf("- During decryption, you can specify if input is Base64 or binary\n");
        break;
    case 1:
        printf("Key Generation Information:\n");
        printf("- At the moment, only RSA 2048-bit key pairs can be generated.\n");
        printf("- The public key is used for encryption, and the private key is used for decryption.\n");
        printf("- The keys are saved in PEM format.\n");
        printf("- The keys can be used with OpenSSL or other compatible libraries.\n");
        printf("- IMPORTANT: Keep your private key secure and never share it!\n");
        break;
    case 2:
        printf("Hashing Information:\n");
        printf("- SHA-256: A secure cryptographic hash function that produces a 256-bit (32-byte) hash value\n");
        printf("  Widely used in security applications and digital signatures\n");
        printf("- MD5: An older hash function that produces a 128-bit (16-byte) hash value\n");
        printf("  NOTE: MD5 is considered cryptographically broken and unsuitable for security purposes\n");
        printf("- Hashing is one-way (cannot be reversed) and used for data integrity verification\n");
        printf("- A good hash function will produce completely different outputs for similar inputs\n");
        break;
    default:
        printf("Invalid selection.\n");
        break;
    }
}

void testHandler(void)
{
    printf("Test handler\n");

    // Choose the test to run
    const char *testOptions[] = {
        "Test 1: File path processing",
        "Test 2: File existence check",
        "Test 3: File creation",
        "Back"};

    int selected = getMenuSelection("Choose a test:", testOptions, sizeof(testOptions) / sizeof(testOptions[0]), true);
    if (selected == 3)
    {
        return; // Back to main menu
    }

    // Run the selected test
    switch (selected)
    {
    case 0:
    {
        // Test file path processing
        char *testPath = getString("Enter a file path: ");
        if (testPath == NULL)
        {
            printf("Error: Failed to read path\n");
            return;
        }
        printf("Processing path (entering function): %s\n", testPath);
        char *processedPath = processPath(testPath, false, false);
        printf("Processed path, evaluating (after function): %s\n", processedPath);
        printf("Given path (input): %s\n", testPath);
        printf("Processed path (output): %s\n", processedPath);
        if (processedPath != NULL)
        {
            if (!fileExists(processedPath))
            {
                printf("File does not exist.\n");
            }

            free(processedPath);
        }
        else
        {
            printf("Test function failed.\n");
        }
    }
    break;
    case 1:
    {
        // Test file existence check
        char *testFile = getString("Enter a file name to check: ");
        if (testFile == NULL)
        {
            printf("Error: Failed to read file name\n");
            return;
        }
        // Check if the file exists
        if (fileExists(testFile))
        {
            printf("File exists: %s\n", testFile);
        }
        else
        {
            printf("File does not exist: %s\n", testFile);
        }
    }
    break;
    case 2:
    {
        // Test file creation
        char *testFile = getString("Enter a file name to create: ");
        if (testFile == NULL)
        {
            printf("Error: Failed to read file name\n");
            return;
        }
        // Create the file
        bool success = createFile(testFile);
        // Check if the file was created successfully
        if (fileExists(testFile))
        {
            printf("File created successfully: %s\n", testFile);
        }
        else
        {
            printf("Failed to create file: %s\n", testFile);
        }
    }
    break;
    default:
        printf("Invalid selection.\n");
        break;
    }

    // Repeat the test menu
    testHandler();
}

bool createFile(const char *filename)
{
    FILE *file = fopen(filename, "w");
    if (file == NULL)
    {
        printf("Error: Failed to create file: %s\n", filename);
        // Get error code
        int errorCode = errno;
        // Print error message
        printf("Error code: %d\n", errorCode);
        return false;
    }
    fclose(file);
    // Check if the file was created successfully
    if (!fileExists(filename))
    {
        printf("Error: File was not created successfully: %s\n", filename);
        return false;
    }
    /* printf("File created successfully: %s\n", filename); */
    return true;
}

// Add a function to change the working directory
bool changeWorkingDirectory(const char *newDir)
{
    int result;

#ifdef _WIN32
    result = _chdir(newDir);
#else
    result = chdir(newDir);
#endif

    if (result == 0)
    {
        printf("Changed directory to: %s\n", newDir);
        return true;
    }
    else
    {
        perror("Failed to change directory");
        return false;
    }
}

void changeDirHandler()
{
    char *newDir = getString("Enter the new directory: ");
    if (newDir == NULL)
    {
        printf("Error: Failed to read directory name\n");
        return;
    }

    // Process the new directory path
    newDir = processPath(newDir, false, true);
    if (newDir == NULL)
    {
        printf("Error: Failed to process directory path\n");
        free(newDir);
        return;
    }

    // Change the working directory
    if (!changeWorkingDirectory(newDir))
    {
        printf("Error: Failed to change directory\n");
    }

    free(newDir);
}

void configHandler(const char *configFile)
{
#define DEFAULT_CONFIG_FILE "config.conf"
// Use a single log entry for function start
#ifdef DEBUG
    printf("Config handler called with file: %s\n", configFile ? configFile : "NULL");
#endif

    // If no config file specified, use default
    if (configFile == NULL || strlen(configFile) == 0)
    {
        configFile = DEFAULT_CONFIG_FILE;
#ifdef DEBUG
        printf("Using default config file: %s\n", configFile);
#endif
    }

    // Check if file exists
    bool exists = fileExists(configFile);
    if (!exists)
    {
#ifdef DEBUG
        printf("Config file not found: %s\n", configFile);
#endif

        // Try default config file if not already trying it
        if (strcmp(configFile, DEFAULT_CONFIG_FILE) != 0)
        {
            configFile = DEFAULT_CONFIG_FILE;
#ifdef DEBUG
            printf("Trying default config file: %s\n", configFile);
#endif
            exists = fileExists(configFile);
        }
    }

    if (exists)
    {
#ifdef DEBUG
        printf("Config file exists: %s\n", configFile);
#endif

        // Process the path to get the absolute path
        char *configFilePath = processPath(configFile, true, false);
        if (configFilePath == NULL)
        {
            printf("Error: Failed to process config file path\n");
            return;
        }

#ifdef DEBUG
        printf("Processed config file path: %s\n", configFilePath);
#endif

        // Read the config file with automatic encoding detection (isBinary = false)
        size_t contentLength;
        char *content = readFileContent(configFilePath, &contentLength, false);

        if (content != NULL)
        {
            // Keep file size info as it might be useful in all builds
            printf("Config file loaded: %zu bytes\n", contentLength);

#ifdef DEBUG
            // Print the content (only in debug builds)
            printf("Config file content:\n%s\n", content);

            // Get additional info about the content string
            printf("Content length: %zu\n", contentLength);
            printf("Content (first 20 chars): ");

            // Print first 20 chars safely
            size_t safeLen = strlen(content);
            safeLen = (safeLen > 20) ? 20 : safeLen;

            for (size_t i = 0; i < safeLen; i++)
            {
                printf("%c", content[i]);
            }
            printf("...\n");
#endif

            // Parse the content
            if (!parseConfigFile(content))
            {
                printf("Error: Failed to parse config file\n");
            }
            else
            {
                printf("Config file parsed successfully\n");
            }

            free(content);
        }
        else
        {
            printf("Error: Failed to read config file\n");
        }

        free(configFilePath);
    }
    else
    {
        printf("Error: Config file not found\n");
    }
}

bool parseConfigFile(const char *content)
{
    if (content == NULL)
        return false;

    // Copy the content for safe tokenization
    char *copy = strdup(content);
    if (!copy)
        return false;

    // Change line endings to Unix-style (LF)
    for (size_t i = 0; i < strlen(copy); i++)
    {
        if (copy[i] == '\r')
        {
            if (copy[i + 1] != '\0' && copy[i + 1] == '\n')
            {
                copy[i] = '\n';
                memmove(copy + i + 1, copy + i + 2, strlen(copy) - i - 1);
                copy[strlen(copy) - 1] = '\0'; // Null-terminate
                i--;                           // Adjust index
            }
            else
            {
                copy[i] = '\n';
            }
        }
    }

    // DEBUG: Print the content to be parsed in hex
    printf("Parsing config file content after newline normalisation (hex): ");
    for (size_t i = 0; i < strlen(copy); i++)
    {
        printf("%02X ", (unsigned char)copy[i]);
    }
    printf("\n");

    char *line = strtok(copy, "\n");
    printf("Parsed line: %s\n", line);
    while (line)
    {
        // TODO: Implement parsing logic in detail
        line = strtok(NULL, "\n");
        printf("Parsed line: %s\n", line);
    }

    free(copy);
    return true;
}

void sigHandler(int signum)
{
/*
signal(SIGINT, sigHandler);  // Ctrl+C
signal(SIGTERM, sigHandler); // Termination request
signal(SIGSEGV, sigHandler); // Segmentation fault
signal(SIGABRT, sigHandler); // Abort signal
signal(SIGQUIT, sigHandler); // Quit signal
signal(SIGILL, sigHandler);  // Illegal instruction
*/
#ifdef _WIN32
#define SIGQUIT 3
#define SIGILL 4
#define SIGABRT 6
#define SIGSEGV 11
#define SIGTERM 15
#define SIGINT 2

    // Windows-specific signal handling
    if (signum == SIGINT)
    {
        printf("\nCtrl+C pressed. Exiting...\n");
    }
    else if (signum == SIGTERM)
    {
        printf("\nTermination request received. Exiting...\n");
    }
    else if (signum == SIGSEGV)
    {
        printf("\nSegmentation fault occurred. Exiting...\n");
    }
    else if (signum == SIGABRT)
    {
        printf("\nAbort signal received. Exiting...\n");
    }
    else if (signum == SIGQUIT)
    {
        printf("\nQuit signal received. Exiting...\n");
    }
    printf("\nSignal %d received. Exiting...\n", signum);
#else
    printf("\nSignal %d received (%s). Exiting...\n", signum, strsignal(signum));
#endif
    // Restore console
    /* restoreConsole(); */
    exit(signum);
}