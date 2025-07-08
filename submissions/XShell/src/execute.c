#include "execute.h"
#include "xsh.h" // For platform checks and system headers

// Implementation of command execution
int xsh_launch(char **args) {
#ifndef _WIN32
    // POSIX-specific implementation
    pid_t pid;
    int status;

    pid = fork();
    if (pid == 0) { // Child process
        if (execvp(args[0], args) == -1) {
            perror("xsh: execvp failed");
        }
        exit(EXIT_FAILURE); // Child process must exit if execvp fails
    } else if (pid < 0) { // Error forking
        perror("xsh: fork failed");
    } else { // Parent process
        do {
            if (waitpid(pid, &status, WUNTRACED) == -1) {
                perror("xsh: waitpid failed");
                return 1; // Error in waiting
            }
        } while (!WIFEXITED(status) && !WIFSIGNALED(status));
    }
#else
    // Windows-specific implementation
    if (args[0] == NULL) {
        return 1; // No command to execute.
    }

    // For Windows, system() is simpler for basic commands but less flexible.
    // CreateProcess offers more control but is more complex to use correctly with args.
    // Sticking with system() for now as in the original code.
    
    // Concatenate arguments into a single command string for system()
    size_t cmd_len = 0;
    for (int i = 0; args[i] != NULL; i++) {
        cmd_len += strlen(args[i]) + 1; // +1 for space or null terminator
    }

    if (cmd_len == 0) return 1;

    char *command = malloc(cmd_len);
    if (!command) {
        fprintf(stderr, "xsh: allocation error for command string (Windows)\n");
        return 1; 
    }
    command[0] = '\0'; 

    for (int i = 0; args[i] != NULL; i++) {
        strcat(command, args[i]);
        if (args[i+1] != NULL) {
            strcat(command, " ");
        }
    }

    int ret_val = system(command);
    if (ret_val == -1) {
        // system() returning -1 usually means command processor couldn't be started.
        fprintf(stderr, "xsh: system() call failed for command: %s\n", command);
    } else if (ret_val != 0) {
        // Non-zero return usually indicates the command itself failed.
        // No standard way to get specific error from system(), so just note it.
        // fprintf(stderr, "xsh: command '%s' exited with status %d\n", command, ret_val);
    }

    free(command);
#endif
    return 1; // Indicate to the shell loop to continue.
}
