import { bold } from "./colors.ts"
import ora from "ora"

// Learn more at https://docs.deno.com/runtime/manual/examples/module_metadata#concepts
interface ChatLog {
  role: string
  content: string
}
const cmd = Deno.args[0]

if (!cmd) {
  console.error('No command provided, possible commands are: help, hey, stats, chat')
  Deno.exit(1)
}
const validCmds = ['help', 'hey', 'stats', 'chat']
if (!validCmds.includes(cmd.toLowerCase())) {
  console.error('Invalid command, possible commands are: help, hey, stats, chat')
  Deno.exit(1)
}

if (cmd == "help") {
  console.table([
    {
      Command: "help",
      Description: "Prints this help message"
    },
    {
      Command: "hey",
      Description: "Prints a greeting message"
    },
    {
      Command: "stats",
      Description: "Prints the stats of ai.hackclub.com"
    },
    {
      Command: "chat",
      Description: "Starts a chat session"
    }
  ])
}

if (cmd == "hey") {
  console.log("Hey there! 👋")
}
if (cmd == "stats") {
  fetch("https://ai.hackclub.com/", {
    headers: {
      "User-Agent": `HackclubAICli v0.0.1 (Deno ${Deno.version.deno})`
    }
  }).then(r => r.text()).then(text => {
    const usageCount = text.split("<b>")[1].split("</b>")[0]
    const model = text.split("<code>")[2].split("</code>")[0]
    console.log(`The model has been used ${bold(usageCount)} times and is ${bold(model)}`)
  })
}
if (cmd == "chat") {
  
  const chatLogs: ChatLog[] = [{
    role: "ai", 
    content: "Hi"
  }]
  console.log(`Enter your message below: `)
  Deno.stdout.write(new TextEncoder().encode("> "))
  for await (const line of Deno.stdin.readable
    .pipeThrough(new TextDecoderStream())) {
    // console.log(`> ` + line.trim())
    const spinner = ora("Thinking...").start()
    spinner.color = "yellow"
    spinner.spinner = "dots"
    fetch("https://ai.hackclub.com/chat/completions", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      "User-Agent": `HackclubAICli v0.0.1 (Deno ${Deno.version.deno})`
      }, 
      body: JSON.stringify({
        messages: [{ role: "user", content: `Previous messages: ${chatLogs.map(e => `${e.content} said by ${e.role}`).join('\n')}\ncurrent message: ${line.trim()}` }]
      })
    }).then(r => r.json()).then(d => {
      // console.log(d)
      chatLogs.push({ role: "user", content: line.trim() })
      chatLogs.push({ role: "ai", content: d.choices[0].message })
      spinner.succeed(d.choices[0].message.content)
    Deno.stdout.write(new TextEncoder().encode("> "))
    }).catch(e => {
      spinner.fail(e.message || "Um idk what happened i died")
     Deno.stdout.write(new TextEncoder().encode("> "))
    })
  }
}