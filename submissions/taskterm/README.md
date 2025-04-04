# taskterm

taskterm is a terminal-based manager app that allows you to manage your tasks
directly from the command line. it provides a simple, efficient, and engaging
way to add, complete, delete and view tasks without leaving your terminal. with
a clean and intuitive interface, taskterm is perfect for developers, system
administrators, or anyone who prefers working in the terminal.

## features

- **add tasks**: quickly add new tasks with a simple input field.
- **complete tasks**: mark tasks as completed or incomplete with a single
  keypress.
- **delete tasks**: remove tasks you no longer need.
- **edit tasks**: modify existing task descriptions.
- **priority levels**: assign high, medium, or low priority to tasks.
- **due dates**: set and manage due dates for your tasks.
- **tags**: categorize tasks with customizable tags.
- **filter tasks**: filter tasks by status: `all` | `completed` | `uncompleted`.
- **sort tasks**: sort by priority, due date, or creation date.
- **search**: search through tasks to find what you need.
- **persistent storage**: tasks are saved to a json file in your home directory,
  so they persist between sessions.
- **cross-platform**: works on windows, macos, and linux.

## installation

you can install taskterm directly from npm:

```bash
# install globally from npm
npm install -g taskterm
# or just run it without install it
npx taskterm
```

## usage

after installation, run taskterm by typing the following command in your
terminal:

```bash
taskterm
```

## commands

- **add a task**: press `a` to focus the input field, type your task
  description, and press `enter`.
- **edit a task**: select a task and press `e` to edit its description.
- **complete a task**: use the arrow keys to select a task and press `c` to
  toggle its completion status.
- **delete a task**: select a task and press `d` to remove it.
- **set priority**: select a task and press `p` to cycle through priority levels
  (high/medium/low).
- **set due date**: select a task and press `u` to add or edit a due date.
- **add tags**: select a task and press `t` to add tags for categorization.
- **toggle filters**: press `f` to cycle between filter modes
  (all/completed/uncompleted).
- **change sort order**: press `s` to cycle through sort options
  (default/priority/duedate/created).
- **search tasks**: press `/` to search through your tasks.
- **view tasks**: the task list is displayed in the main window. completed tasks
  are marked with `[✓]`, and incomplete tasks with `[ ]`.
- **help**: press `h` to show/hide a help popup with detailed command
  instructions.
- **quit**: press `q`, `esc`, or `ctrl+c` to exit the application.

## requirements

node.js: version 14 or higher
