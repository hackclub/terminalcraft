#include "xproj.h"
#include "utils.h"
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>

#ifdef _WIN32
#include <direct.h>  // for _mkdir, _getcwd, _chdir
#define MKDIR(dir) _mkdir(dir)
#define GETCWD(buf, size) _getcwd(buf, size)
#define CHDIR(dir) _chdir(dir)
#else
#include <unistd.h>  // for getcwd, chdir
#define MKDIR(dir) mkdir(dir, 0755)
#define GETCWD(buf, size) getcwd(buf, size)
#define CHDIR(dir) chdir(dir)
#endif

static int create_c_project(const char *project_name, const char *project_path);
static int create_py_project(const char *project_name, const char *project_path);
static int create_web_project(const char *project_name, const char *project_path);


int xsh_xproj(char **args) {
    if (args[1] == NULL || args[2] == NULL) {
        fprintf(stderr, "xsh: xproj: missing argument\n");
        fprintf(stderr, "Usage: xproj <project_type (c, py, web)> <project_name> [--git]\n");
        return 1;
    }

    const char *project_type = args[1]; 
    const char *project_name = args[2];
    int initialize_git = (args[3] && strcmp(args[3], "--git") == 0);

    // Create the project directory
    if (MKDIR(project_name) != 0) {
        fprintf(stderr, "xsh: xproj: cannot create project directory '%s': ", project_name);
        perror("");
        return 1;
    }
    printf("Created project directory '%s'\n", project_name);

    int result = 1;
    if (strcmp(project_type, "c") == 0) {
        result = create_c_project(project_name, project_name);
    } else if (strcmp(project_type, "py") == 0) {
        result = create_py_project(project_name, project_name);
    } else if (strcmp(project_type, "web") == 0) {
        result = create_web_project(project_name, project_name);
    } else {
        fprintf(stderr, "xsh: xproj: unknown project type '%s'. Supported types: c, py, web.\n", project_type);
        return 1;
    }

    if (result != 0) {
        fprintf(stderr, "xsh: xproj: failed to create project files for '%s'\n", project_name);
        return result;
    }

    printf("Project '%s' of type '%s' created successfully.\n", project_name, project_type);

    // Initialize Git if requested
    if (initialize_git) {
        char original_dir[XSH_MAXLINE];
        if (GETCWD(original_dir, sizeof(original_dir)) == NULL) {
            perror("xsh: xproj: getcwd failed");
            return 1;
        }

        if (CHDIR(project_name) != 0) {
            fprintf(stderr, "xsh: xproj: cannot change directory to '%s': ", project_name);
            perror("");
            return 1;
        }

        // Initialize Git repository
        printf("Initializing Git repository...\n");
        if (system("git init") != 0) {
            fprintf(stderr, "xsh: xproj: git initialization failed\n");
            CHDIR(original_dir); // Return to original directory before exiting
            return 1;
        }
        printf("Git repository initialized.\n");
        
        // Return to original directory
        if (CHDIR(original_dir) != 0) {
            perror("xsh: xproj: failed to return to original directory");
            return 1;
        }
    }
    
    printf("Project '%s' created successfully.\n", project_name);
    return 1;
}

static int create_c_project(const char *project_name, const char *project_path) {
        char file_path[XSH_MAXLINE];

    // Create main.c file
    snprintf(file_path, sizeof(file_path), "%s/main.c", project_name);
    const char *main_c_content = 
        "#include <stdio.h>\n\n"
        "int main() {\n"
        "    printf(\"Hello, World!\\n\");\n"
        "    return 0;\n"
        "}\n";
    if (create_file_with_content(file_path, main_c_content) != 0) {
        fprintf(stderr, "xsh: xproj: cannot create file '%s': ", file_path);
        perror("");
        return 1;
    }
    printf("Created file '%s'\n", file_path);

    // Create Makefile
    snprintf(file_path, sizeof(file_path), "%s/Makefile", project_name);
    char makefile_content[XSH_MAXLINE * 2];
    snprintf(makefile_content, sizeof(makefile_content),
        "CC = gcc\n"
        "CFLAGS = -Wall -Wextra -std=c17\n\n"
        "all: main\n\n"
        "main: main.o\n"
        "\t$(CC) $(CFLAGS) -o main main.o\n\n"
        "main.o: main.c\n"
        "\t$(CC) $(CFLAGS) -c main.c\n\n"
        "clean:\n"
        "\trm -f *.o main\n");

    if (create_file_with_content(file_path, makefile_content) != 0) {
        fprintf(stderr, "xsh: xproj: cannot create file '%s': ", file_path);
        perror("");
        return 1;
    }
    printf("Created file '%s'\n", file_path);

    // Create README.md
    snprintf(file_path, sizeof(file_path), "%s/README.md", project_name);
    char readme_content[XSH_MAXLINE];
    snprintf(readme_content, sizeof(readme_content),
        "# %s\n\n"
        "A brief description of your project.\n\n"
        "## Compilation\n\n"
        "Use `make` to compile the project.\n\n"
        "## Usage\n\n"
        "Run the compiled program with `./main`.\n", project_name);
    
    if (create_file_with_content(file_path, readme_content) != 0) {
        fprintf(stderr, "xsh: xproj: cannot create file '%s': ", file_path);
        perror("");
        return 1;
    }
    printf("Created file '%s'\n", file_path);

    return 0;
}

static int create_py_project(const char *project_name, const char *project_path) {
        char file_path[XSH_MAXLINE];

    // Create main.py file
    snprintf(file_path, sizeof(file_path), "%s/main.py", project_name);
    const char *main_py_content = 
        "def main():\n"
        "    print(\"Hello, World!\")\n\n"
        "if __name__ == \"__main__\":\n"
        "    main()\n";
    if (create_file_with_content(file_path, main_py_content) != 0) {
        fprintf(stderr, "xsh: xproj: cannot create file '%s': ", file_path);
        perror("");
        return 1;
    }
    printf("Created file '%s'\n", file_path);


    // Create README.md
    snprintf(file_path, sizeof(file_path), "%s/README.md", project_name);
    char readme_content[XSH_MAXLINE];
    snprintf(readme_content, sizeof(readme_content),
        "# %s\n\n"
        "A brief description of your project.\n\n"
        "## Usage\n\n", project_name);
    
    if (create_file_with_content(file_path, readme_content) != 0) {
        fprintf(stderr, "xsh: xproj: cannot create file '%s': ", file_path);
        perror("");
        return 1;
    }
    printf("Created file '%s'\n", file_path);

    return 0;
}

static int create_web_project(const char *project_name, const char *project_path) {
    char file_path[XSH_MAXLINE];

    // Create index.html file
    snprintf(file_path, sizeof(file_path), "%s/index.html", project_name);
    char index_html_content[XSH_MAXLINE * 2];
    snprintf(index_html_content, sizeof(index_html_content),
        "<!DOCTYPE html>\n"
        "<html lang=\"en\">\n"
        "<head>\n"
        "    <meta charset=\"UTF-8\">\n"
        "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n"
        "    <title>%s</title>\n"
        "    <link rel=\"stylesheet\" href=\"styles.css\">\n"
        "</head>\n"
        "<body>\n"
        "    <h1>Hello, World!</h1>\n"
        "    <p>Welcome to your new web project</p>\n"
        "    <div id=\"content\"></div>\n"
        "    <script src=\"script.js\"></script>\n"
        "</body>\n"
        "</html>\n", project_name);
    
    if (create_file_with_content(file_path, index_html_content) != 0) {
        fprintf(stderr, "xsh: xproj: cannot create file '%s': ", file_path);
        perror("");
        return 1;
    }
    printf("Created file '%s'\n", file_path);

    // Create styles.css file
    snprintf(file_path, sizeof(file_path), "%s/styles.css", project_name);
    const char *style_css_content =
        "body {\n"
        "    font-family: Arial, sans-serif;\n"
        "    line-height: 1.6;\n"
        "    margin: 0;\n"
        "    padding: 20px;\n"
        "    color: #333;\n"
        "}\n\n"
        "h1 {\n"
        "    color: #2c3e50;\n"
        "    text-align: center;\n"
        "}\n\n"
        "#content {\n"
        "    margin-top: 20px;\n"
        "    padding: 15px;\n"
        "    border: 1px solid #ddd;\n"
        "    border-radius: 5px;\n"
        "}\n";
    
    if (create_file_with_content(file_path, style_css_content) != 0) {
        fprintf(stderr, "xsh: xproj: cannot create file '%s': ", file_path);
        perror("");
        return 1;
    }
    printf("Created file '%s'\n", file_path);
    
    // Create script.js file
    snprintf(file_path, sizeof(file_path), "%s/script.js", project_name);
    const char *script_js_content =
        "document.addEventListener('DOMContentLoaded', function() {\n"
        "    const content = document.getElementById('content');\n"
        "    content.innerHTML = '<p>This content was added with JavaScript!</p>';\n"
        "    \n"
        "    // Example of adding an event\n"
        "    content.addEventListener('click', function() {\n"
        "        alert('You clicked the content!');\n"
        "    });\n"
        "});\n";
    
    if (create_file_with_content(file_path, script_js_content) != 0) {
        fprintf(stderr, "xsh: xproj: cannot create file '%s': ", file_path);
        perror("");
        return 1;
    }
    printf("Created file '%s'\n", file_path);

    // Create README.md
    snprintf(file_path, sizeof(file_path), "%s/README.md", project_name);
    char readme_content[XSH_MAXLINE];
    snprintf(readme_content, sizeof(readme_content),
        "# %s\n\n"
        "A brief description of your web project.\n\n", project_name);
    
    if (create_file_with_content(file_path, readme_content) != 0) {
        fprintf(stderr, "xsh: xproj: cannot create file '%s': ", file_path);
        perror("");
        return 1;
    }
    printf("Created file '%s'\n", file_path);

    return 0;
}