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
 * @brief Processes a given file path and performs various checks and transformations based on the operating system.
 *
 * @param path The input file path to be processed. It can be a relative or absolute path.
 * @param mustExist A boolean flag indicating whether the path must exist. If true, the function will check if the path exists.
 *                  If false, the function will check if the parent directory exists, allowing for new file creation.
 *                  In general, input files should exist, while output files may not.
 *
 * @return A newly allocated string containing the processed path, or NULL if an error occurs. The caller is responsible for freeing the returned string.
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
 */
char *processPath(const char *path, bool mustExist)
{
    // If the path is NULL or empty, return NULL
    if (path == NULL || strlen(path) == 0)
    {
        printf("Error: Path is NULL or empty\n");
        return NULL;
    }

    // Allocate a buffer for the path
    char *buffer = (char *)malloc(strlen(path) + 1);
    if (buffer == NULL)
    {
        printf("Error: Memory allocation failed\n");
        return NULL;
    }

    // Copy the path to the buffer
    strcpy(buffer, path);

    // Check if the path is enclosed in quotes and remove them if present
    if (buffer[0] == '\"' && buffer[strlen(buffer) - 1] == '\"')
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
        {
            buffer[i] = '\\';
        }
    }

    // Convert to absolute path
    char *resolvedPath = _fullpath(NULL, buffer, 0);
    if (resolvedPath == NULL)
    {
        printf("Error: Failed to resolve path\n");
        free(buffer);
        return NULL;
    }

    // Free the original buffer and allocate a new one for the resolved path
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

    /* printf("Given path: %s\n", path);
    printf("Processed path: %s\n", buffer); */

    // Check if the path exists - only required if mustExist is true
    if (mustExist && _access(buffer, 0) == -1)
    {
        printf("Path does not exist: %s\n", buffer);
        free(buffer);
        return NULL;
    }

    // If creating a new file, check if the directory exists
    if (!mustExist)
    {
        char *lastSlash = strrchr(buffer, '\\');
        if (lastSlash != NULL)
        {
            // Temporarily cut the string at the last backslash
            char lastChar = *lastSlash;
            *lastSlash = '\0';

            // Check if the directory exists
            if (_access(buffer, 0) == -1)
            {
                printf("Directory does not exist: %s\n", buffer);
                free(buffer);
                return NULL;
            }

            // Restore the string
            *lastSlash = lastChar;
        }
    }

    // Check attributes only if the path exists
    if (_access(buffer, 0) != -1)
    {
        DWORD attributes = GetFileAttributesA(buffer);
        if (attributes == INVALID_FILE_ATTRIBUTES)
        {
            printf("Error: Failed to get file attributes\n");
            free(buffer);
            return NULL;
        }
    }

#elif __linux__
    // Linux path processing

    // For existing paths or when mustExist is true
    if (mustExist || access(buffer, F_OK) != -1)
    {
        char *resolvedPath = realpath(buffer, NULL);
        if (resolvedPath == NULL)
        {
            printf("Error: Failed to resolve path\n");
            free(buffer);
            return NULL;
        }

        // Free original buffer and use resolved path
        free(buffer);
        buffer = resolvedPath;

        // Check if the path exists (only matters if mustExist is true)
        if (mustExist && access(buffer, F_OK) == -1)
        {
            printf("Path does not exist: %s\n", buffer);
            free(buffer);
            return NULL;
        }

        // Check file attributes if the path exists
        if (access(buffer, F_OK) != -1)
        {
            struct stat pathStat;
            if (stat(buffer, &pathStat) == -1)
            {
                printf("Error: Failed to get file attributes\n");
                free(buffer);
                return NULL;
            }
        }
    }
    else
    {
        // Handle non-existent path (for file creation)

        // Extract directory path
        char *lastSlash = strrchr(buffer, '/');
        if (lastSlash != NULL)
        {
            // Temporarily cut string at the last slash
            char lastChar = *lastSlash;
            *lastSlash = '\0';

            // Empty directory means current directory
            if (strlen(buffer) == 0)
            {
                strcpy(buffer, ".");
            }

            // Check if directory exists
            if (access(buffer, F_OK) == -1)
            {
                printf("Directory does not exist: %s\n", buffer);
                free(buffer);
                return NULL;
            }

            // Restore the path
            *lastSlash = lastChar;
        }

        // Convert to absolute path if it's a relative path
        if (buffer[0] != '/')
        {
            // Get current working directory
            char *cwd = getcwd(NULL, 0);
            if (cwd == NULL)
            {
                printf("Error: Failed to get current working directory\n");
                free(buffer);
                return NULL;
            }

            // Create absolute path
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

    /* printf("Given path: %s\n", path);
    printf("Processed path: %s\n", buffer); */
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

char *readFileContent(const char *filename, size_t *contentLength)
{
    // Open the file
    FILE *file = fopen(filename, "r");
    if (file == NULL)
    {
        printf("Error: File not found or cannot be opened");
        system("pause");
        return NULL;
    }

    // Get file size
    fseek(file, 0, SEEK_END);
    long fileSize = ftell(file);
    fseek(file, 0, SEEK_SET);
    *contentLength = fileSize;

    // Allocate buffer
    char *content = (char *)malloc(fileSize + 1);
    if (content == NULL)
    {
        printf("Error: Memory allocation failed");
        fclose(file);
        return NULL;
    }

    // Read file into buffer
    size_t bytesRead = fread(content, 1, fileSize, file);
    if (bytesRead != fileSize)
    {
        printf("Error: Error reading file");
        if (sizeof(content) < 256)
        {
            printf("Buffer: %s\n", content);
        }
        else
        {
            printf("Buffer is too large to display (> 256 characters)\n");
        }
        printf("Bytes read: %zu\n", bytesRead);
        printf("File size: %ld\n", fileSize);
        fclose(file);
        free(content);
        return NULL;
    }

    // Close file
    fclose(file);

    // Null-terminate buffer
    content[fileSize] = '\0';

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
        char *processedPath = processPath(testPath, false);
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