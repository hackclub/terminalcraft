#!/usr/bin/env node

import enquirer from "enquirer"
import * as fs from "fs/promises"
import {homedir} from "os"
import figlet from "figlet"
import {promisify} from "util"
const fig = promisify(figlet)
import ora from "ora"
import { Resend } from "resend"
import routes from "./routes.js"
import readline from "readline"

if (process.platform === "win32") {
    var rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  
    rl.on("SIGINT", function () {
      process.emit("SIGINT");
    });
  }
  
  process.on("SIGINT", function () {
    //graceful shutdown
    console.log("\nExiting...");
    process.exit();
  });

const text = await fig("resend-cli")
console.log(text)
const configPath = `${homedir()}/.resend_config.json`
const fileExists = await fs.access(configPath).then(() => true).catch(() => false);
if (fileExists) {
    let config, instance
    try {
        let fileContents = await fs.readFile(configPath)
        fileContents = fileContents + ''
        config = JSON.parse(fileContents)
        //console.log(config.apiKey)
        instance = new Resend(config.apiKey)
    } catch (e) {
        console.error("Error reading config file")
        console.error(e)
        process.exit(1)
    }

    try {
        await routes({resend: instance, apiKey: config.apiKey, config})
    } catch {} // this is needed so that Ctrl+C doesn't throw an exception
} else {
    const apiKeyResponse = await enquirer.password({
        message: "Enter an API key with full access: "
    })
    const spinner = ora({text: "Authenticating...", spinner: "toggle9"}).start()
    const resend = new Resend(apiKeyResponse)
    const apiKeys = await resend.apiKeys.list()
    spinner.stop()
    if (apiKeys?.error?.statusCode === 400) {
        console.error("Invalid API key")
        process.exit(1)
    } else {
        const config = {
            apiKey: apiKeyResponse
        }
        await fs.writeFile(configPath, JSON.stringify(config))
        console.log("API key saved in plain text to ~/.resend_config.json.")
        console.log("Run `resend-cli` again to use the CLI.")
        process.exit(0)
    }
}