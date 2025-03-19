# alias-mngr
CLI utility for managing shell aliases. Cross-platform, experimental Windows support.

## Install
I am working on publishing this on NPM. In the meantime you can grab a bundled JS file named "alias-mngr.js" in this folder. If you wish to build it yourself, the code repository is [Exerra/alias-mngr](https://github.com/Exerra/alias-mngr). Substitute `alias-mngr` with `node alias-mngr.js`.

## Usage

You can view the help page by running `alias-mngr -h`.

Changes to the aliases (adding/removing/enabling/disabling) do not immediately get synced to the shell. They have to be linked/binded by running `alias-mngr link`.

When adding aliases that take inputs ($1, $2, etc) make sure to escape them, otherwise the shell will pass the input not as a string (`"$1"`), but prefill it.
Example: `alias-mngr add v "open \$1 -a \"Visual Studio Code\""`

### Windows

> [!CAUTION]
> The following command is aimed for power users ONLY. If you don't know what you're doing, DO NOT run this. This weakens security for your computer.

By default Windows does not let users execute PowerShell scripts. To use this utility on Windows you have to run the following command:
```sh
Set-ExecutionPolicy Bypass
```

## TODO
- [ ] Support for more shells

## Supported shells

| Shell                  | Supported? | Comment                                                                                                                                                               |
| ---------------------- | ---------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Bash                   | ✅          |                                                                                                                                                                       |
| Zsh                    | ✅          |                                                                                                                                                                       |
| Fish                   | ❌          | Different way of handling from what I can tell. Don't use it myself, will have to experiment.                                                                         |
| PowerShell             | Mostly     | If your PowerShell profile is configured to print something before a command is run, it won't work. Otherwise, should be fine if the Windows usage guide is followed. |
| Anything not mentioned | ❌          | If you have a shell you wish to be supported, you can create an issue or code it yourself & make a PR :)                                                              |
