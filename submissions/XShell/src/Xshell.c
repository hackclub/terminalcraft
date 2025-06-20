// Hi,today we will be looking at how to implement a simple shell in C.
// Yes, we will be implementing a simple shell in C.
// How? I do not know yet, but we will figure it out together.

// let the journey begin...

#include "xsh.h"
#include "input.h"
#include "builtins.h"
#include "execute.h"
#include "history.h"
#include "utils.h" // For print_slow, build_prompt

void xsh_banner(void) {
    // Get terminal width (default to 80 if we can't determine it)
    int term_width = 80;
    
    // ASCII Art Logo with proper centering
    const char *logo[] = {
        " __  ______  _          _ _ ",
        " \\ \\/ / ___|| |__   ___| | |",
        "  \\  /\\___ \\| '_ \\ / _ \\ | |",
        "  /  \\ ___) | | | |  __/ | |",
        " /_/\\_\\____/|_| |_|\\___|_|_|"
    };
    
    printf("\n");
    
    // Center and print the logo
    for (int i = 0; i < 5; i++) {
        int padding = (term_width - strlen(logo[i])) / 2;
        printf("%*s%s\n", padding, "", logo[i]);
    }
    
    printf("\n");
    
    // Center the header line
    const char *header = "====================================================================";
    int header_padding = (term_width - strlen(header)) / 2;
    printf("%*s%s\n", header_padding, "", header);
    
    // Center the title
    const char *title = "XShell - A Powerful Shell Implementation in C";
    int title_padding = (term_width - strlen(title)) / 2;
    printf("%*s%s\n", title_padding, "", title);
    
    // Center the footer line
    printf("%*s%s\n\n", header_padding, "", header);
    
    // Center each feature line
    const char *features[] = {
        "FEATURES:",
        "- Command history tracking and recall",
        "- Built-in commands (help, cd, exit, history)",
        "- External command execution",
        "- Dynamic prompt with system information",
        "",
        "Type 'help' to see all available commands"
    };
    
    for (int i = 0; i < 7; i++) {
        int feat_padding = (term_width - strlen(features[i])) / 2;
        printf("%*s%s\n", feat_padding, "", features[i]);
    }
    
    // Center the closing line
    printf("\n%*s%s\n\n", header_padding, "", header);
}


// Main shell loop
void xsh_loop(void) {
    char *line;
    char **args;
    int status;

    do {
        char *prompt = build_prompt(); // Get dynamic prompt
        printf("%s", prompt);
        line = xsh_read_line();
        add_to_history(line); // Add command to history
        args = xsh_split_line(line);
        status = xsh_execute(args); // xsh_execute will handle builtins or launch

        free(line);
        free(args);
    } while (status);
}

// Execute command: checks for built-ins first, then launches external command
int xsh_execute(char **args) {
    if (args[0] == NULL) {
        // An empty command was entered.
        return 1; // Continue shell loop
    }

    for (int i = 0; i < xsh_num_builtins(); i++) {
        if (strcmp(args[0], builtin_str[i]) == 0) {
            return (*builtin_func[i])(args);
        }
    }

    return xsh_launch(args);
}

int main(int argc, char **argv) {
    // Load config files, if any.
    xsh_banner();

    // Run command loop.
    xsh_loop();

    // Perform any shutdown/cleanup.
    // Free history
    for (int i = 0; i < history_count; i++) {
        free(history[i]);
    }

    return EXIT_SUCCESS;
}

