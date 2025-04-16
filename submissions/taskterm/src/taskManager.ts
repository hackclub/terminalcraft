import * as blessed from "blessed";
import * as fs from "fs";
import * as os from "os";
import path from "path";
import { ITask } from "./type";

class TaskManager {
  private screen: blessed.Widgets.Screen;
  private taskList: blessed.Widgets.ListElement;
  private input: blessed.Widgets.TextboxElement;
  private statusBar: blessed.Widgets.TextElement;
  private instructionBar: blessed.Widgets.TextElement;
  private helpBox: blessed.Widgets.BoxElement;
  private editBox: blessed.Widgets.BoxElement;
  private editInput: blessed.Widgets.TextboxElement;
  private searchBox: blessed.Widgets.BoxElement;
  private searchInput: blessed.Widgets.TextboxElement;
  private tasks: ITask[] = [];
  private configDir: string = path.join(os.homedir(), ".taskterm");
  private filePath: string = path.join(this.configDir, "tasks.json");
  private filterMode: "all" | "completed" | "uncompleted" = "all";
  private filteredTaskIndices: number[] = []; // Track indices of filtered tasks
  private sortMode: "default" | "priority" | "dueDate" | "created" = "default";
  private searchTerm: string = "";

  constructor() {
    this.loadTasks();

    this.screen = blessed.screen({
      smartCSR: true,
      style: { bg: "black" },
    });
    this.screen.title = "TaskTerm";

    const taskListBox = blessed.box({
      top: 0,
      left: 0,
      width: "100%",
      height: "80%",
      border: { type: "line", fg: "green" as any },
      label: " Tasks ",
    });

    this.taskList = blessed.list({
      parent: taskListBox,
      top: 1,
      left: 0,
      width: "100%-2",
      height: "100%-2",
      keys: true,
      mouse: true,
      tags: true,
      style: {
        item: { fg: "white" },
        selected: { bg: "blue" as any, fg: "white" as any },
      },
    });

    const inputBox = blessed.box({
      bottom: 0,
      left: 0,
      width: "100%",
      height: 3,
      border: { type: "line", fg: "yellow" as any },
      label: " Add Task ",
    });

    this.input = blessed.textbox({
      parent: inputBox,
      top: 0,
      left: 1,
      width: "100%-2",
      height: 1,
      inputOnFocus: true,
    });

    this.statusBar = blessed.text({
      bottom: 3,
      left: 0,
      width: "100%",
      height: 1,
      content: "Tasks: 0 | Completed: 0 | Filter: all",
      style: { bg: "blue", fg: "white" },
    });

    this.instructionBar = blessed.text({
      bottom: 4,
      left: 0,
      width: "100%",
      height: 1,
      content:
        'Use arrow keys to select | "a" add | "e" edit | "c" complete | "d" delete | "f" filter | "s" sort | "/" search | "h" help',
      style: { fg: "white" },
    });

    this.helpBox = blessed.box({
      top: "center",
      left: "center",
      width: "60%",
      height: "60%",
      border: { type: "line", fg: "cyan" as any },
      label: " Help ",
      content:
        'Commands:\n"a" - Add task\n"e" - Edit selected task\n"c" - Toggle complete\n"d" - Delete task\n"f" - Toggle filter (all/completed/uncompleted)\n"s" - Change sort (default/priority/dueDate/created)\n"p" - Set priority (high/medium/low)\n"u" - Edit due date for task\n"t" - Add tags\n"/" - Search tasks\n"q" - Quit',
      style: { bg: "black", fg: "white" },
      hidden: true,
    });

    // Create edit dialog
    this.editBox = blessed.box({
      top: "center",
      left: "center",
      width: "70%",
      height: 5,
      border: { type: "line", fg: "yellow" as any },
      label: " Edit Task ",
      hidden: true,
    });

    this.editInput = blessed.textbox({
      parent: this.editBox,
      top: 1,
      left: 1,
      width: "100%-2",
      height: 1,
      inputOnFocus: true,
    });

    // Create search dialog
    this.searchBox = blessed.box({
      top: "center",
      left: "center",
      width: "70%",
      height: 5,
      border: { type: "line", fg: "magenta" as any },
      label: " Search Tasks ",
      hidden: true,
    });

    this.searchInput = blessed.textbox({
      parent: this.searchBox,
      top: 1,
      left: 1,
      width: "100%-2",
      height: 1,
      inputOnFocus: true,
    });

    this.screen.append(taskListBox);
    this.screen.append(inputBox);
    this.screen.append(this.statusBar);
    this.screen.append(this.instructionBar);
    this.screen.append(this.helpBox);
    this.screen.append(this.editBox);
    this.screen.append(this.searchBox);

    this.taskList.focus();

    this.screen.key(["escape", "q", "C-c"], () => process.exit(0));
    this.screen.key(["a"], () => this.input.focus());
    this.input.key(["enter"], () => this.addTask());
    this.taskList.key(["c"], () => this.toggleComplete());
    this.taskList.key(["d"], () => this.removeTask());
    this.screen.key(["f"], () => this.toggleFilterMode());
    this.screen.key(["s"], () => this.toggleSortMode());
    this.screen.key(["e"], () => this.showEditDialog());
    this.taskList.key(["p"], () => this.cyclePriority());
    this.taskList.key(["u"], () => this.promptForDueDate());
    this.taskList.key(["t"], () => this.promptForTags());
    this.taskList.key(["/"], () => this.showSearchDialog());
    this.screen.key(["h"], () => {
      this.helpBox.toggle();
      this.screen.render();
    });

    this.updateTaskList();
  }

  private saveTasks() {
    fs.writeFileSync(this.filePath, JSON.stringify(this.tasks, null, 2));
  }

  private loadTasks() {
    if (fs.existsSync(this.filePath)) {
      this.tasks = JSON.parse(fs.readFileSync(this.filePath, "utf8"));
    }
    if (!fs.existsSync(this.configDir)) {
      fs.mkdirSync(this.configDir, { recursive: true });
    }
  }

  private updateTaskList() {
    this.taskList.clearItems();
    this.filteredTaskIndices = [];

    // Apply sorting
    const sortedTasks = [...this.tasks];
    if (this.sortMode === "priority") {
      const priorityRank = { high: 0, medium: 1, low: 2, undefined: 3 };
      sortedTasks.sort(
        (a, b) =>
          priorityRank[a.priority || "undefined"] -
          priorityRank[b.priority || "undefined"]
      );
    } else if (this.sortMode === "dueDate") {
      sortedTasks.sort((a, b) => {
        if (!a.due_date) return 1;
        if (!b.due_date) return -1;
        return new Date(a.due_date).getTime() - new Date(b.due_date).getTime();
      });
    } else if (this.sortMode === "created") {
      sortedTasks.sort(
        (a, b) =>
          new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      );
    }

    sortedTasks.forEach((task) => {
      // Find original index in this.tasks
      const originalIndex = this.tasks.findIndex((t) => t.id === task.id);

      // Apply filters
      const matchesFilter =
        this.filterMode === "all" ||
        (this.filterMode === "completed" && task.completed) ||
        (this.filterMode === "uncompleted" && !task.completed);

      // Apply search
      const matchesSearch =
        !this.searchTerm ||
        task.description.toLowerCase().includes(this.searchTerm.toLowerCase());

      if (matchesFilter && matchesSearch) {
        let priorityMarker = "";
        // Add colorful priority indicators
        if (task.priority === "high")
          priorityMarker = "{red-fg}(HIGH){/red-fg}";
        else if (task.priority === "medium")
          priorityMarker = "{yellow-fg}(MED){/yellow-fg}";
        else if (task.priority === "low")
          priorityMarker = "{green-fg}(LOW){/green-fg}";

        let dueDateStr = task.due_date ? ` (due: ${task.due_date})` : "";
        let tagsStr = task.tags?.length ? ` #${task.tags.join(" #")}` : "";

        const text = task.completed
          ? `[✓] ${task.description} ${priorityMarker} ${dueDateStr}${tagsStr}`
          : `[ ] ${task.description} ${priorityMarker} ${dueDateStr}${tagsStr}`;

        this.taskList.addItem(text);
        this.filteredTaskIndices.push(originalIndex);
      }
    });

    this.updateStatusBar();
    this.screen.render();
  }

  private updateStatusBar() {
    const total = this.tasks.length;
    const completed = this.tasks.filter((t) => t.completed).length;
    this.statusBar.setContent(
      `Tasks: ${total} | Completed: ${completed} | Filter: ${this.filterMode} | Sort: ${this.sortMode}`
    );
  }

  private toggleSortMode() {
    if (this.sortMode === "default") this.sortMode = "priority";
    else if (this.sortMode === "priority") this.sortMode = "dueDate";
    else if (this.sortMode === "dueDate") this.sortMode = "created";
    else this.sortMode = "default";

    this.updateTaskList();
    this.setStatusMessage(`Sort: ${this.sortMode}`);
  }

  private toggleFilterMode() {
    if (this.filterMode === "all") this.filterMode = "completed";
    else if (this.filterMode === "completed") this.filterMode = "uncompleted";
    else this.filterMode = "all";

    this.updateTaskList();
    this.setStatusMessage(`Filter: ${this.filterMode}`);
  }

  private showSearchDialog() {
    this.searchBox.show();
    this.searchInput.focus();
    this.screen.render();

    this.searchInput.setValue(this.searchTerm);

    const onCancel = () => {
      this.searchBox.hide();
      this.taskList.focus();
      this.screen.render();
    };

    const onSubmit = () => {
      this.searchTerm = this.searchInput.getValue().trim();
      this.searchBox.hide();
      this.updateTaskList();
      this.taskList.focus();
    };

    this.searchInput.key(["escape"], onCancel);
    this.searchInput.key(["enter"], onSubmit);
  }

  private showEditDialog() {
    const selectedIndex = (this.taskList as any).selected;
    if (selectedIndex < 0 || selectedIndex >= this.filteredTaskIndices.length)
      return;

    const taskIndex = this.filteredTaskIndices[selectedIndex];
    const task = this.tasks[taskIndex];
    const taskId = task.id; // Store task ID to ensure we update the correct task

    // Remove any existing key handlers first
    this.editInput.unkey("escape", () => {});
    this.editInput.unkey("enter", () => {});

    // Clear input first to avoid showing previous values
    this.editInput.setValue("");
    this.editBox.show();
    this.editInput.focus();
    this.screen.render();

    // Use a short timeout to ensure the UI is ready before setting the value
    setTimeout(() => {
      this.editInput.setValue(task.description);
      this.screen.render();
    }, 80);

    const onCancel = () => {
      this.editBox.hide();
      this.taskList.focus();
      this.screen.render();
    };

    const onSubmit = () => {
      const newDescription = this.editInput.getValue().trim();
      if (newDescription) {
        // Find the current index of the task in case it changed
        const currentTaskIndex = this.tasks.findIndex((t) => t.id === taskId);
        if (currentTaskIndex >= 0) {
          this.tasks[currentTaskIndex].description = newDescription;
          this.saveTasks();
          this.updateTaskList();
          this.setStatusMessage("Task updated!");
        }
      }
      this.editBox.hide();
      this.taskList.focus();
    };

    this.editInput.key(["escape"], onCancel);
    this.editInput.key(["enter"], onSubmit);
  }

  private cyclePriority() {
    const selectedIndex = (this.taskList as any).selected;
    if (selectedIndex < 0 || selectedIndex >= this.filteredTaskIndices.length)
      return;

    const taskIndex = this.filteredTaskIndices[selectedIndex];
    const task = this.tasks[taskIndex];

    // Ensure proper cycling of priority values
    if (!task.priority || task.priority === "high") {
      task.priority = "low";
    } else if (task.priority === "low") {
      task.priority = "medium";
    } else if (task.priority === "medium") {
      task.priority = "high";
    }

    this.saveTasks();
    this.updateTaskList();
    this.setStatusMessage(`Priority set to: ${task.priority}`);
  }

  private promptForTags() {
    const selectedIndex = (this.taskList as any).selected;
    if (selectedIndex < 0 || selectedIndex >= this.filteredTaskIndices.length)
      return;

    const taskIndex = this.filteredTaskIndices[selectedIndex];
    const task = this.tasks[taskIndex];

    // Create a temporary dialog for tags
    const tagsBox = blessed.box({
      top: "center",
      left: "center",
      width: "70%",
      height: 5,
      border: { type: "line", fg: "blue" as any },
      label: " Add Tags (comma-separated) ",
    });

    const tagsInput = blessed.textbox({
      parent: tagsBox,
      top: 1,
      left: 1,
      width: "100%-2",
      height: 1,
      inputOnFocus: true,
    });

    this.screen.append(tagsBox);
    tagsInput.focus();

    if (task.tags) {
      tagsInput.setValue(task.tags.join(","));
    }

    this.screen.render();

    tagsInput.key(["escape"], () => {
      this.screen.remove(tagsBox);
      this.taskList.focus();
      this.screen.render();
    });

    tagsInput.key(["enter"], () => {
      const tagsValue = tagsInput.getValue().trim();
      if (tagsValue) {
        task.tags = tagsValue
          .split(",")
          .map((t) => t.trim())
          .filter((t) => t);
      } else {
        task.tags = [];
      }
      this.saveTasks();
      this.updateTaskList();
      this.screen.remove(tagsBox);
      this.taskList.focus();
      this.setStatusMessage("Tags updated!");
    });
  }

  private setStatusMessage(message: string, timeout: number = 2000) {
    const originalContent = this.statusBar.content;
    this.statusBar.setContent(message);
    this.screen.render();
    setTimeout(() => {
      this.statusBar.setContent(originalContent);
      this.screen.render();
    }, timeout);
  }

  private addTask() {
    const description = this.input.getValue().trim();
    if (description) {
      this.tasks.push({
        id: Date.now(),
        description,
        completed: false,
        created_at: new Date().toISOString(),
        priority: "medium", // Default priority
      });
      this.saveTasks();
      this.updateTaskList();
      this.input.clearValue();
      this.setStatusMessage("Task added!");
      this.taskList.focus();
    }
  }

  private toggleComplete() {
    const selectedIndex = (this.taskList as any).selected;
    if (selectedIndex >= 0 && selectedIndex < this.filteredTaskIndices.length) {
      const taskIndex = this.filteredTaskIndices[selectedIndex];
      this.tasks[taskIndex].completed = !this.tasks[taskIndex].completed;
      this.saveTasks();
      this.updateTaskList();
      this.setStatusMessage(
        this.tasks[taskIndex].completed
          ? "Task completed!"
          : "Task marked incomplete"
      );
    }
  }

  private removeTask() {
    const selectedIndex = (this.taskList as any).selected;
    if (selectedIndex >= 0 && selectedIndex < this.filteredTaskIndices.length) {
      const taskIndex = this.filteredTaskIndices[selectedIndex];
      this.tasks.splice(taskIndex, 1);
      this.saveTasks();
      this.updateTaskList();
      this.setStatusMessage("Task deleted!");
    }
  }

  private promptForDueDate() {
    const selectedIndex = (this.taskList as any).selected;
    if (selectedIndex < 0 || selectedIndex >= this.filteredTaskIndices.length)
      return;

    const taskIndex = this.filteredTaskIndices[selectedIndex];
    const task = this.tasks[taskIndex];

    // Create a temporary dialog for due date
    const dueDateBox = blessed.box({
      top: "center",
      left: "center",
      width: "70%",
      height: 5,
      border: { type: "line", fg: "cyan" as any },
      label: " Set Due Date (YYYY-MM-DD) ",
    });

    const dueDateInput = blessed.textbox({
      parent: dueDateBox,
      top: 1,
      left: 1,
      width: "100%-2",
      height: 1,
      inputOnFocus: true,
    });

    this.screen.append(dueDateBox);
    dueDateInput.focus();

    if (task.due_date) {
      dueDateInput.setValue(task.due_date);
    }

    this.screen.render();

    dueDateInput.key(["escape"], () => {
      this.screen.remove(dueDateBox);
      this.taskList.focus();
      this.screen.render();
    });

    dueDateInput.key(["enter"], () => {
      const dueDateValue = dueDateInput.getValue().trim();
      if (dueDateValue) {
        // Simple validation for YYYY-MM-DD format
        const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
        if (dateRegex.test(dueDateValue)) {
          task.due_date = dueDateValue;
          this.saveTasks();
          this.updateTaskList();
          this.setStatusMessage("Due date updated!");
        } else {
          this.setStatusMessage("Invalid date format! Use YYYY-MM-DD");
        }
      } else {
        // Clear due date if empty
        task.due_date = undefined;
        this.saveTasks();
        this.updateTaskList();
        this.setStatusMessage("Due date cleared!");
      }
      this.screen.remove(dueDateBox);
      this.taskList.focus();
    });
  }
}
const app = new TaskManager();
export default app;
