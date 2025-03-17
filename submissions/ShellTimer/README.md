# ShellTimer

A simple speedcubing timer for the command line written in C# using .NET 9.

![timer.png](Assets/timer.png)
![stats.png](Assets/stats.png)

This project was written for the Hack Club 2025 Terminal Craft YSWS event, and this is my first ever standalone CLI application.

My primary motivation for creating this project was to create something actually useful that I could imagine myself using on a daily basis, as I am also a speedcuber ;)

## Features

- [x] Support for different cube sizes (2x2, 3x3, 4x4, etc.)
- [x] Configurable inspection time
- [x] Scramble generation
- [x] Support for penalties (+2, DNF)
- [x] Solve history
- [x] Solve statistics (PB, Ao5, Ao12, Ao100)

### Roadmap

- [ ] Add a multiplayer racing mode (using SignalR) - Already in the works!
- [ ] Add an option to export the solve history to a file
- [ ] Add support for multiple sessions
- [ ] Add an algorithm practice tool
- [ ] Add support for different puzzles (e.g. Skewb, Pyraminx)
- [ ] Add a scramble visualizer (using the Spectre.Console Canvas API)

## Building

1. Ensure you have [.NET 9 SDK](https://dotnet.microsoft.com/en-us/download/dotnet/9.0) installed:
   ```bash
   dotnet --version
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/Xeretis/ShellTimer.git
   cd ShellTimer
   ```

3. Build the project:
   ```bash
   dotnet build
   ```

4. Run the application (for development only):
   ```bash
   cd ShellTimer.Cli && dotnet run
   ```

## Usage

Run the application without any commands to see the help menu:

```
USAGE:
    ShellTimer.Cli.dll [OPTIONS] <COMMAND>

OPTIONS:
    -h, --help    Prints help information

COMMANDS:
    timer       Start timing solves
    scramble    Generate scrambles for a specific cube size
    solves      Manage solve records
    stats       Show statistics for a specific cube size
```

```
DESCRIPTION:
Manage solve records

USAGE:
    ShellTimer.Cli.dll solves [OPTIONS] <COMMAND>

OPTIONS:
    -h, --help    Prints help information

COMMANDS:
    list           List all solve records
    delete <id>    Delete a solve record by its ID
    clear          Clear all solve records from the database
```

If you want to know more about a specific command, pass the `help` flag to it.

For example: `./ShellTimer timer -h` (Please note that when running in development, you should only pass flags after `--` like so: `dotnet run timer -- -h`)

## Notable dependencies

- [Spectre.Console](https://spectreconsole.net/) - Terminal UI library
- [SQLite-net](https://github.com/praeclarum/sqlite-net) - SQLite ORM
