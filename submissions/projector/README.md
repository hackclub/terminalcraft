# Projector

Original/official repository available at: https://github.com/ofluffydev/projector

A universal CLI tool that intelligently manages, builds, and runs projects of various types—Rust, Node.js, Python, etc. This utility automatically detects the type of project from the current directory, offers interactive suggestions, can install missing tooling, and optionally runs everything inside ephemeral Docker containers without requiring a Dockerfile. Additionally, it stores existing projects in a SQLite database for quick access later on.

I had the urge to build this years ago, but at the time I only used Java so SDKMAN was more than enough for what I needed. But now, being the terminal lover I am, I find myself juggling multiple languages and tools. This is my attempt to streamline that process

## Implemented Features

? indicates a feature that is not guranteed to be added.

- [ ] Project Detection
- [ ] More advanced options in gallery instead of just launching into editor
- [ ] Pre-commit hooks for git to show lines of codes/other stats
- [ ] Purge the repo of unholy Python code (replace with a better method for generating starter code)
- [ ] Visual Studio Code Plugin
- [ ] Docker setup for testing the tool (Possibly using the tools own docker feature)
- [ ] Quick gist/pastebin integration for sharing code snippets
- [ ] Github/Gitlab/Codeberg Integration via API's
- [ ] Track when project was last opened with Projector
- [ ] Installation method that doesn't require cargo or git. (Maybe a script?)
- [ ] Possible learning mode, maybe even within the REPL. (e.g. `projector learn rust` would open a REPL with the Rust docs)
  - [ ] Maybe even pull down docs from the internet instead of storing them here?
- [ ] Self updating
- [ ] Mini editor for quick edits?
- [ ] Github/Codeberg actions for CI/CD
- [ ] Projector website with documentation
- [ ] Projector blog
- [ ] Deployment options for sending your project to a server/remote machine
- [x] Automatic Tool Installation
- [ ] Instant Docker Integration
- [x] Configuration & Customization
  - [ ] Themes
  - [x] Pick an editor to open your project by default
    - [x] VSCode
    - [ ] All Jetbrains Editors
      - gonna make list of them here when I get to it
    - [ ] Vim
    - [ ] NeoVim
    - [ ] Nano
    - Let me know if you want more editors!
  - [ ] Interactive settings menu in CLI
  - [ ] REPL Mode
- [x] `new` Command
  - [ ] Type language to quickly select
  - [ ] Swap between framework/language mode?
  - [x] Rust
  - [x] Python
  - [ ] JavaScript
  - [ ] Java
  - [x] C
  - [ ] C#
  - [ ] C++
  - [ ] Go
  - [ ] Swift
  - [ ] Kotlin
- [x] Store existing projects in a SQLite database for quick access later on
  - [ ] Command for adding existing projects
  - [ ] Remote syncing for those 10x devs with hundreds of projects
- [ ] Project "vault" for encrypted storage of sensitive projects

## Table of Contents

- [Features](#features)
- [Why Use This?](#why-use-this)
- [Why Use Multiple Entry Points?](#why-use-multiple-entry-points)
- [Installation](#installation)
- [Contributing](#contributing)
- [License](#license)

## Features

1. **Project Detection**

   - Scans for marker files (e.g., `Cargo.toml`, `package.json`, `requirements.txt`, etc.).
   - Determines the project type automatically.
   - Supports optional overrides with `.projected/config.toml` for custom or multiple toolchains.

2. **Subcommand Abstraction**

   - Offers unified commands (`projected build`, `projected test`, `projected install`, etc.) based on the detected tool.
   - Internally calls cargo, npm, pip, etc., so you don’t need to remember each tool’s command.

3. **Automatic Tool Installation**

   - Automatically installs required tools if they aren’t on your system.
   - Integrates with apt, brew, or other package managers.
   - Prompts the user before installation or can auto-yes via config.

4. **Interactive REPL Mode**

   - Provides partial input parsing, real-time auto-completions, and command history.
   - Great for quickly exploring or chaining commands.

5. **Shell Completion**

   - Generates Bash, Zsh, and Fish completion scripts using Clap.
   - Enables tab-completion of subcommands, flags, and more.

6. **Docker Integration**

   - Optional `--docker` mode runs builds/tests in ephemeral containers.
   - Dynamically chooses a base image (e.g. `rust:latest`, `node:latest`) so no Dockerfile is needed.
   - Detects the project and picks a Docker image based on the project.
   - Mounts the project directory as a volume, cleans up containers automatically.

7. **Configuration & Customization**

   - Global config in `~/.projected/config.toml` or local config in `.projected/config.toml`.
   - Control default package managers, Docker usage, tool versions, etc.
   - Pick an editor to open your project by default
     - VSCode
     - Sublime Text
     - Atom
     - IntelliJ IDEA
   - Interactive settings menu in CLI

8. **Modular Architecture**

   - New project types can be plugged in easily.
   - Potential for a future plugin system.

9. **Cross-Platform**

   - Single binary for Windows, macOS, and Linux.
   - Attempts to abstract away platform-specific quirks.

10. **Store Existing Projects**

    - Stores existing projects in a SQLite database for quick access later on.
    - Remote syncing for those 10x devs with hundreds of projects.

11. **User Experience & Documentation**
    - Clear help messages with usage examples.
    - Offers guidance for beginners (e.g., detects Rust project and suggests `projected build`).
    - Comprehensive error handling (e.g., missing Docker or unrecognized project).

## Why Use This?

- Simplifies the dev workflow by centralizing commands for various projects.
- Eliminates friction when tools are missing, automatically installing them.
- Offers ephemeral container builds without needing Dockerfiles.
- Provides both a straightforward CLI and an interactive mode for quick iteration.

## Why Use Multiple Entry Points?

Due to the nature of the available commands, multiple entry points are necessary to provide stability and flexibility. This design allows users to enter any point of the application directly, bypassing intermediate steps. For example, specifying `project new rust` skips the interactive language chooser entirely, streamlining the workflow for experienced users who know exactly what they need.

## Installation

To install Projector, you can clone the repository and use `cargo install`:

```sh
git clone https://github.com/ofluffydev/projector.git
cd projector
cargo install --path .
```

## Contributing

We welcome contributions! If you encounter any issues, have feature requests, or want to contribute to the project, please follow these guidelines:

- **Opening Issues**: If you find a bug or have a suggestion, please open an issue on the [GitHub Issues](https://github.com/ofluffydev/projector/issues) page.
- **Pull Requests**: If you want to contribute code, fork the repository, create a new branch, and submit a pull request. Please ensure your code follows the project's coding standards and includes tests if applicable.
- **Reporting Bugs**: When reporting bugs, please include as much detail as possible, including steps to reproduce the issue, your operating system, and any relevant logs or error messages.

## License

This project is licensed under the [GNU AGPL](LICENSE). Feel free to contribute, suggest new features, or open issues!
