#!/usr/bin/env bun

import { Command } from "commander";
import chalk from "chalk";
import { join } from "path";
import readline from "readline";
import fs from "fs/promises";

const program = new Command();

program
  .name(chalk.bold("paperplane"))
  .version(chalk.gray("1.0.0"))
  .description("A simple TUI To-Do app");

const dbPath = join(__dirname, "db.json");

if (await fs.exists(dbPath) == false) {
  await fs.writeFile(dbPath, "{}");
}

program
  .command("add <taskID>")
  .description("Add a new task with the given ID")
  .action(async (taskID) => {

    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    try {
      rl.question("Enter task: ", async (task) => {
        const db = JSON.parse(await fs.readFile(dbPath, "utf-8"));
        db[taskID] = {
          task,
          done: false
        };
        await fs.writeFile(dbPath, JSON.stringify(db, null, 2));
        console.log(chalk.green("Task added successfully!"));
        rl.close();
      });
    } catch (error) {
      console.log(chalk.red("Error adding task!"));
      console.log(error);
    }
  });

program
  .command("delete <taskID>")
  .description("Delete a task with the given ID")
  .action(async (taskID) => {
    try {
      const db = JSON.parse(await fs.readFile(dbPath, "utf-8"));
      delete db[taskID];
      await fs.writeFile(dbPath, JSON.stringify(db, null, 2));
      console.log(chalk.green("Task deleted successfully!"));
    } catch (error) {
      console.log(chalk.red("Error deleting task!"));
    }
  });

program
  .command("list")
  .description("List all tasks")
  .action(async () => {
    try {
      const db = JSON.parse(await fs.readFile(dbPath, "utf-8"));
      console.log(chalk.green("Tasks:"));

      if(Object.keys(db).length === 0)
        console.log(chalk.yellow("  No tasks found!"));

      for (const taskID in db) {
        if (db[taskID].done)
          console.log(chalk.strikethrough(` ${chalk.magenta(taskID)}: ${db[taskID].task} (done)`));
        else
          console.log(`${chalk.magenta(taskID)}: ${db[taskID].task}`);
      }
    } catch (error) {
      console.log(chalk.red("Error listing tasks!"));
    }
  });

program
  .command("edit <taskID>")
  .description("Edit a task with the given ID")
  .action(async (taskID) => {

    const rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout,
    });

    try {
      const db = JSON.parse(await fs.readFile(dbPath, "utf-8"));
      rl.question("Enter new task: ", async (task) => {
        db[taskID].task = task;
        await fs.writeFile(dbPath, JSON.stringify(db, null, 2));
        console.log(chalk.green("Task edited successfully!"));
        rl.close();
      });
    } catch (error) {
      console.log(chalk.red("Error editing task!"));
    }
  });

program
  .command("done <taskID>")
  .description("Mark a task with the given ID as done")
  .action(async (taskID) => {
    try {
      const db = JSON.parse(await fs.readFile(dbPath, "utf-8"));
      db[taskID].done = true;
      await fs.writeFile(dbPath, JSON.stringify(db, null, 2));

      console.log(chalk.green("Task marked as done successfully!"));
    } catch (error) {
      console.log(chalk.red("Error marking task as done!"));
    }
  });

program.parse(process.argv);