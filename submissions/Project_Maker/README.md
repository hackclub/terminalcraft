# ProjectMaker

ProjectMaker is a command-line tool that automates project setup, creates necessary folders, initializes repositories (TBD), and generates an Obsidian template with note files (TBD). It supports various project types, including web, Godot, Unity, and Node.js.

## Note
This was tested on Windows and WSL (Windows Subsystem for Linux) only.

## Features
- Automates project creation for multiple frameworks and technologies
- Initializes Git repositories automatically
- Generates project-specific templates
- Creates an Obsidian structure for project documentation
- Cross-platform support

## Installation

To install ProjectMaker locally, use the following command:
```sh
pip install projectmaker
```

If you want to install it from a local build:
```sh
pip install dist/projectmaker-<version>-py3-none-any.whl
```

## Usage

### Creating a New Project
To create a new project, run:
```sh
projectmaker create <project_name> <project_type>
```
Example:
```sh
projectmaker create MyWebsite web
```

To precise the directory you want the project to be, run:
```sh
projectmaker create <project_name> <project_type> -d (or --directory) <directory_path>
```
Example:
```sh
projectmaker create MyGodotGame godot -d "C:\Users\[Username]\Projects\New Folder" (On Windoes)
projectmaker create MyGodotGame godot -d "/home/[Username]/Projects/New Folder" (On MacOS)
projectmaker create MyGodotGame godot -d "/Users/[Username]/Projects/New Folder" (On Linux)
```


### Supported Project Types
- `web` - Initializes an HTML/CSS/JS project
- `godot` - Sets up a new Godot project
- `unity` - Creates a Unity project structure
- `nodejs` - Initializes a Node.js project with `npm init`

## Configuration
ProjectMaker includes a `config.yaml` file that allows customization of default settings.

## Troubleshooting
If you encounter issues with `npm` or `node` not being recognized, ensure they are properly installed and accessible in your system's PATH.

For WSL users:
```sh
pip install --user projectmaker
```
If you get a permission error, try creating a virtual environment:
```sh
python3 -m venv venv
source venv/bin/activate
pip install projectmaker
```

## Contributing
Contributions are welcome! Feel free to submit a pull request or open an issue.

## License
This project is licensed under the MIT License.

