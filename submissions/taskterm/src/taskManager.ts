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
  private tasks: ITask[] = [];
  private configDir: string = path.join(os.homedir(), ".taskterm");
  private filePath: string = path.join(this.configDir, "tasks.json");

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
      style: {
        item: { fg: "white" },
        selected: { bg: "blue", fg: "white" },
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
      content: "Tasks: 0 | Completed: 0",
      style: { bg: "blue", fg: "white" },
    });

    this.instructionBar = blessed.text({
      bottom: 4,
      left: 0,
      width: "100%",
      height: 1,
      content:
        'Use arrow keys to select | "a" to add | "c" to complete | "d" to delete | "h" for help',
      style: { fg: "white" },
    });

    this.helpBox = blessed.box({
      top: "center",
      left: "center",
      width: "50%",
      height: "50%",
      border: { type: "line", fg: "cyan" as any },
      label: " Help ",
      content:
        'Commands:\n"a" - Add task\n"c" - Toggle complete\n"d" - Delete task\n"q" - Quit',
      style: { bg: "black", fg: "white" },
      hidden: true,
    });

    this.screen.append(taskListBox);
    this.screen.append(inputBox);
    this.screen.append(this.statusBar);
    this.screen.append(this.instructionBar);
    this.screen.append(this.helpBox);

    this.taskList.focus();

    this.screen.key(["escape", "q", "C-c"], () => process.exit(0));
    this.screen.key(["a"], () => this.input.focus());
    this.input.key(["enter"], () => this.addTask());
    this.taskList.key(["c"], () => this.toggleComplete());
    this.taskList.key(["d"], () => this.removeTask());
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
    this.tasks.forEach((task) => {
      const text = task.completed
        ? `[✓] ${task.description}`
        : `[ ] ${task.description}`;
      this.taskList.addItem(text);
    });
    this.updateStatusBar();
    this.screen.render();
  }

  private updateStatusBar() {
    const total = this.tasks.length;
    const completed = this.tasks.filter((t) => t.completed).length;
    this.statusBar.setContent(`Tasks: ${total} | Completed: ${completed}`);
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
      });
      this.saveTasks();
      this.updateTaskList();
      this.input.clearValue();
      this.setStatusMessage("Task added!");
      this.taskList.focus();
    }
  }

  private toggleComplete() {
    const index = (this.taskList as any).selected;
    if (index >= 0 && index < this.tasks.length) {
      this.tasks[index].completed = !this.tasks[index].completed;
      this.saveTasks();
      this.updateTaskList();
      this.setStatusMessage(
        this.tasks[index].completed
          ? "Task completed!"
          : "Task marked incomplete"
      );
    }
  }

  private removeTask() {
    const index = (this.taskList as any).selected;
    if (index >= 0 && index < this.tasks.length) {
      this.tasks.splice(index, 1);
      this.saveTasks();
      this.updateTaskList();
      this.setStatusMessage("Task deleted!");
    }
  }
}

const app = new TaskManager();
