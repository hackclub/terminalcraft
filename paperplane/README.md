# Paperplane

Paperplane is a simple TUI todo app.

## Installation

This is published on the npm registry but works on bun. 

It is recommended to install it globally so you can use it from anywhere.

It is cross-platform and should work on Windows, macOS, and Linux.

```bash

`bash
$ bun add -g @atom06/paperplane
$ bun x paperplane
`

## Usage

The app has a few commands that you can use to interact with it:

### Commands

- `add <taskID>`: Add a new task with the given ID.
- `delete <taskID>`: Delete a task with the given ID.
- `list`: List all tasks.
- `edit <taskID>`: Edit a task with the given ID.
- `done <taskID>`: Mark a task with the given ID as done.

### Examples

- Add a task:
```bash
$ paperplane add milk
Enter task: Buy milk
Task added successfully.
```

- List all tasks:
```bash
$ paperplane list
    1. Buy milk
```

- Mark a task as done:
```bash
$ paperplane done 1
Task marked as done.
```

- Delete a task:
```bash
$ paperplane delete 1
Task deleted successfully.
```

- Edit a task:
```bash
$ paperplane edit 1
Enter new task: Buy milk and eggs
Task edited successfully.
```

## Report Issues

If you find any issues, please report them [here](https://github.com/theatom06/paperplane/issues).

## License

MIT

## Author

theatom06