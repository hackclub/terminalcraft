# taskterm

taskterm is a terminal-based manager app that allows you to manage yours tasks
directly from the command line. it provides a simple, efficient, and engiging
way to add, complete, delete and view task without leaving your terminal. With a
clean and intuitive interface, TaskTerm is perfect for developers, system
administrators, or anyone who preferes working in the terminal

## features

- **add tasks**: quickly add new tasks with a simple input field.
- **complete tasks**: mark tasks as completed or incomplete with single keypress
- **delete tasks**: remove tasks you have completed
- **filter tasks**: you can filter tasks: `all` | `completed` | `uncompleted`
- **persistent storage**: tasks are saved to a json file in your home directory,
  so they persist between sessions
- **cross-platform**: works on windows, macos, and linux.

## installation

You can install taskterm directly from npm:

```bash
# Install globally from npm
npm install -g taskterm
#or just run it without install it
npx taskterm
```

## usage

after installation, run taskterm by typing the following command in your
terminal:

```bash
taskterm
```

## commands

- **add a task**: press `a` to focus the input field,type your taks description,
  and press `enter`
- **complete a task**: use the arrow keys to select a task and press `c` to
  toggle it's completion status.
- **toggle filters**: press `f` to toggle between filters.
- **view tasks**: the task list is displayed in the main window. completed tasks
  are markded with `[✓]`, and incomplete tasks with `[ ]`
- **help**: press `h` to show/hide a help popup with detailed command
  instructions.
- **quit**: press `q`,`esc`, or `ctrl+c` to exit the application.

## requirements

node.js: version 14 or higher
