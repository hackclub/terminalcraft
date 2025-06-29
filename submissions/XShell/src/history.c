#include "history.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// Define history array and count here
char *history[XSH_HISTORY_SIZE];
int history_count = 0;

void add_to_history(const char *line) {
    if (line == NULL || *line == '\0') return; // Do not add empty lines

    // Avoid adding duplicate of the last command
    if (history_count > 0 && strcmp(history[history_count - 1], line) == 0) {
        return;
    }

    if (history_count < XSH_HISTORY_SIZE) {
        history[history_count] = strdup(line);
        if (history[history_count] == NULL) {
            fprintf(stderr, "xsh: strdup error in add_to_history\n");
            // Not exiting, as history is not critical enough to stop the shell
            return;
        }
        history_count++;
    } else {
        // History is full, shift everything up and add to the end
        free(history[0]); // Free the oldest command
        for (int i = 0; i < XSH_HISTORY_SIZE - 1; i++) {
            history[i] = history[i+1];
        }
        history[XSH_HISTORY_SIZE - 1] = strdup(line);
        if (history[XSH_HISTORY_SIZE - 1] == NULL) {
            fprintf(stderr, "xsh: strdup error in add_to_history (shifting)\n");
            // Attempt to recover by nullifying the last entry if strdup fails
            history[XSH_HISTORY_SIZE - 1] = NULL; 
            // And potentially decrementing history_count if it was wrongly assumed to be full
            // However, the logic implies it IS full, so this is tricky.
            // For now, just log and continue.
        }
    }
}

// This function is for the `history` built-in command's display part.
// The command itself (xsh_history) is in builtins.c
void display_history(void) {
    if (history_count == 0) {
        printf("No commands in history.\n");
        return;
    }
    for (int i = 0; i < history_count; i++) {
        // Check if history entry is not NULL, in case of strdup failure
        if (history[i] != NULL) {
            printf("%d: %s\n", i + 1, history[i]);
        } else {
            printf("%d: [error storing command]\n", i + 1);
        }
    }
}

// If xsh_history command logic were to be moved here entirely:
/*
int xsh_history_cmd(char **args) {
    display_history();
    return 1; // To continue shell loop
}
*/
