#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>
#include <string.h>
#include <stdarg.h>
#include <time.h>
#include "log.h"   // Include the header for log functions
#include "logic.h" // Include the header for logic functions
#include "functions.h"

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
#include <sys/select.h>
#include <sys/stat.h> // For struct stat
#include <signal.h>   // For signal handling
#endif

#ifdef _WIN32
CHAR_INFO *consoleBuffer = NULL;
CONSOLE_SCREEN_BUFFER_INFO savedCsbi;
#endif

void init();
void loop(int argc, char *argv[]);
enum Action askForAction(bool invalid, int argc, char *argv[]);
void testHandler();
void restoreConsole();

enum Action
{
    Encrypt,
    Decrypt,
    GenerateKey,
    Hash,
    Info,
    ChangeDirectory,
    Test,
    Exit
};

int width;

int main(int argc, char *argv[])
{
    // Check if one of the command line arguments is "--config"
    if (argc > 1)
    {
        for (int i = 1; i < argc; i++)
        {
            if (strcmp(argv[i], "--config") == 0)
            {
                printf("Using config file\n");

                // Call the config function here
                if (i + 1 < argc)
                {
                    configHandler(argv[i + 1]);
                }
                else
                {
                    configHandler(NULL);
                }
                return 0;
            }
        }
    }

    /* Encryption tool */
    init();

    while (1)
    {
        // main loop
        loop(argc, argv);
    }

    return 0;
}

/*

    Encryption methods:
    - Public-private key
    - Symmetric key
    - Hashing

    Actions:
    - Encrypt
        - From file
        - From text
        - To file
        - To text
    - Decrypt
        - From file
        - From text
        - To file
        - To text
    - Generate key
        - Public-private key
        - Symmetric key
    - Hash
        - File
        - Text

    - Exit


The user will be able to choose an action from the list above.
The program will then ask for the necessary information to perform the action.
The program will then perform the action and display the result, or save it to a file.

*/

void loop(int argc, char *argv[])
{
    enum Action action = askForAction(false, argc, argv);
    printTitle();

    // Display current working directory
    char *cwd = getCurrentWorkingDirectory();
    if (cwd != NULL)
    {
        printf("Current working directory: %s\n", cwd);
        free(cwd);
    }
    else
    {
        printf("Error: Unable to get current working directory\n");
    }

    switch (action)
    {
    case Encrypt:
        encryptHandler();
        break;
    case Decrypt:
        decryptHandler();
        break;
    case GenerateKey:
        generateKeyHandler();
        break;
    case Hash:
        hashHandler();
        break;
    case Info:
        infoHandler();
        break;
    case ChangeDirectory:
        changeDirHandler();
        break;
    case Test:
        testHandler();
        break;
    case Exit:
        printf("Exiting...\n");
        // Restore the console before exiting
        restoreConsole();
        exit(0);
    default:
        printf("Invalid action (how did you get here?) probably a bug\n"); // Should never happen
#ifdef _WIN32
        Sleep(1000); // 1000 milliseconds
#else
        sleep(1); // 1 second
#endif
        break;
    }

#ifdef _WIN32
    system("pause");
#else
    printf("Press any key to continue...\n");
    getCharNoEcho();
#endif

    printTitle();
}

// Now refactor askForAction to use this new function
enum Action askForAction(bool invalid, int argc, char *argv[])
{
    if (invalid)
    {
        printf("Invalid action\n");
    }

    // Display current working directory
    char *cwd = getCurrentWorkingDirectory();
    if (cwd != NULL)
    {
        printf("Current working directory: %s\n", cwd);
        free(cwd);
    }
    else
    {
        printf("Error: Unable to get current working directory\n");
    }

    // Check if one of the command line arguments is "test"
    // If so, display the test option
    bool testOption = false;
    if (argc > 1)
    {
        for (int i = 1; i < argc; i++)
        {
            if (strcmp(argv[i], "--test") == 0)
            {
                printf("Test option selected\n");
                testOption = true;
                break;
            }
        }
    }

    // Define options based on whether testOption is enabled
    const char *options[7]; // Maximum 7 options
    int optionCount = 0;

    // Always include these options
    options[optionCount++] = "Encrypt";
    options[optionCount++] = "Decrypt";
    options[optionCount++] = "Generate key";
    options[optionCount++] = "Hash";
    options[optionCount++] = "Info";
    options[optionCount++] = "Change Directory";

    // Only include Test option if testOption is true
    if (testOption)
    {
        options[optionCount++] = "Test";
    }

    // Always include Exit as the last option
    options[optionCount++] = "Exit";

    const char *title = "Choose an action:";
    int selected = getMenuSelection(title, options, optionCount, true);

    // Convert selection to enum
    if (selected >= 0 && selected < optionCount)
    {
        // Map selection to enum value
        if (selected < 6)
        {
            // First 6 options (0-5) map directly
            return (enum Action)selected;
        }
        else if (selected == optionCount - 1)
        {
            // Last option is always Exit
            return Exit;
        }
        else if (testOption && selected == 6)
        {
            // If testOption is true and we selected position 6, it's Test
            return Test;
        }
    }
    else if (selected == -1)
    { // ESC key
        return Exit;
    }

    // This should never happen with our implementation
    printf("Invalid selection (how did you get here?) probably a bug\n");
    return askForAction(true, argc, argv);
}

void init()
{
// Save the current terminal content
#ifdef _WIN32
    HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
    CONSOLE_SCREEN_BUFFER_INFO csbi;
    GetConsoleScreenBufferInfo(hConsole, &csbi);

    // Save the csbi for later use in restoreConsole
    savedCsbi = csbi;

    // Get buffer size
    COORD bufferSize = csbi.dwSize;
    int cellCount = bufferSize.X * bufferSize.Y;

    // Allocate memory for buffer
    consoleBuffer = malloc(cellCount * sizeof(CHAR_INFO));
    if (consoleBuffer)
    {
        COORD bufferCoord = {0, 0};
        SMALL_RECT readRegion = {0, 0, bufferSize.X - 1, bufferSize.Y - 1};

        // Read the console buffer
        ReadConsoleOutput(hConsole, consoleBuffer, bufferSize, bufferCoord, &readRegion);

        // Register cleanup function
        atexit(restoreConsole);
    }
#else
    // For Unix-like systems, use terminal control sequences
    // Check if terminal supports alternate screen buffer
    char *term = getenv("TERM");
    if (term && (strstr(term, "xterm") || strstr(term, "screen") ||
                 strstr(term, "rxvt") || strstr(term, "vt100")))
    {
        // Save the screen state
        printf("\033[?1049h");
        fflush(stdout);
        atexit(restoreConsole);
    }
    else
    {
        printf("Warning: Terminal does not support alternate screen buffer\n");
    }

    // Register signal handlers
    signal(SIGINT, sigHandler);  // Ctrl+C
    signal(SIGTERM, sigHandler); // Termination request
    signal(SIGSEGV, sigHandler); // Segmentation fault
    signal(SIGABRT, sigHandler); // Abort signal
    signal(SIGQUIT, sigHandler); // Quit signal
    signal(SIGILL, sigHandler);  // Illegal instruction
#endif

    // Terminal support for UTF-8
#ifdef _WIN32
    printf("Enabling support for UTF-8\n");
    system("chcp 65001");
#endif

    // Determine terminal width
#ifdef _WIN32
    // Reuse the already initialized csbi instead of declaring a new one
    width = csbi.srWindow.Right - csbi.srWindow.Left + 1;
#else
    struct winsize w;
    ioctl(STDOUT_FILENO, TIOCGWINSZ, &w);
    width = w.ws_col;
#endif
    printf("Terminal width: %d\n", width);

    printTitle();

    if (width > 72)
    {
        printf("Encryption tool\n\n");
    }
}

void restoreConsole()
{
#ifdef _WIN32
    if (consoleBuffer)
    {
        HANDLE hConsole = GetStdHandle(STD_OUTPUT_HANDLE);
        COORD bufferSize = savedCsbi.dwSize;
        COORD bufferCoord = {0, 0};
        SMALL_RECT writeRegion = {0, 0, bufferSize.X - 1, bufferSize.Y - 1};

        // Write the saved buffer back to the console
        WriteConsoleOutput(hConsole, consoleBuffer, bufferSize, bufferCoord, &writeRegion);

        // Restore cursor position
        SetConsoleCursorPosition(hConsole, savedCsbi.dwCursorPosition);

        // Free the allocated memory
        free(consoleBuffer);
        consoleBuffer = NULL;
    }
#else
    // For Unix-like systems, restore the screen
    printf("\033[?1049l"); // Restore screen
    fflush(stdout);
#endif
}