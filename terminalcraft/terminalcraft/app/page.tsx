"use client"
import { useState, useEffect } from "react";
import Prompt from "@/components/Prompt";


type CommandEntry = {
  type: "input" | "output",
  content: string
}

export default function Home() {
  const [command, setCommand] = useState<string>('');
  const [history, setHistory] = useState<CommandEntry[]>([{
    type: "output",
    content: "type 'help' to get started"
  }]);

  function handleCommand(command: string) {
    if (command == "clear") {
      setHistory([]);
      setCommand("");
      return
    }

    // push the command the user typed
    const newHistory = [ ...history, {
      type: "input" ,
      content: command
    }] as CommandEntry[];

    // add the output of running the command to the history
    setHistory([ ...newHistory, {
      type: "output",
      content: runCommand(command)
    }]);

    setCommand("");
  }

  function runCommand(fullCommand: string): string {
    const commandAndParams = fullCommand.split(" ");
    const command = commandAndParams.shift();
    switch (command) {
      case "ls": {
        return listFiles();
      }
      case "whoami": {
        return whoami();
      }
      case "cat": {
        return cat(commandAndParams[0]);
      }
      case "help": {
        return help();
      }
      case "hackclub": {
        return hackclubFlag();
      }
      case "submit": {
        window.open('https://airtable.com/appzR6MIcj5G9A2Fa/pag8jn2axMXOB2lid/form', '_blank');
        return "Opening submission form in new tab...";
      }
      case "slack": {
        window.open('https://hackclub.slack.com/archives/C08F58MT3GV', '_blank');
        return "Opening #terminal-craft channel on Slack...";
      }
      case "exit": {
        document.body.classList.add('crt-off');
        setTimeout(() => {
          window.close();
          // Fallback if window.close() is blocked
          window.location.href = "about:blank";
        }, 1000);
        return "Goodbye! 👋";
      }
      case "clear":
        return ""
      default:
        return `terminalcraft: could not find command: ${command}`
    }
  }

  function listFiles() {
    return "about.md prizes.md faq.md";
  }

  function whoami() {
    return `
    Lo, there walks among us a Hack Clubber most peculiar, one who scorns the frilly gewgaws of modern UI and finds solace in the cold, unfeeling embrace of the terminal. Where others prattle of their "drag-and-drop" and their "material design," this steadfast soul wields naught but a blinking cursor and the righteous fury of a well-placed grep. They craft tools not for the faint of heart, but for those brave enough to dance with stdin and stdout, their fingers moving with eldritch speed across the keys, summoning forth mighty applications that demand respect—or at the very least, a well-formatted man page. Speak to them of "mouse support," and they shall laugh, a grim and knowing laugh, before returning to their endless battle with sed and awk. And lo, though their ways be arcane and their scripts indecipherable to lesser mortals, those who walk the path of the terminal know: theirs is the true and noble craft, unsullied by the bloat of the modern age.
    `
  }

  function cat(filename: string) {
    switch (filename) {
      case "about.md":
        return `# TerminalCraft YSWS

Get ready to build and publish your own terminal program and earn a **Raspberry Pi 4**! 🎉 This is your chance to create something useful, learn new skills, and get a cool prize.

## What You Need to Do:
1. **Build a Terminal App** that solves a problem or improves your workflow.
2. **Get 10 Users** to use your program.
3. **Make It Open-Source** so others can learn from it.
4. **Support Both Unix (MacOS, Linux) and Windows** platforms.
5. **Provide Clear Instructions** on how to build and run your app.

### Tools You Can Use:
- **Textualize** (Recommended for web sharing)
- **Ncurses** (or any other framework)

## How to Get Involved:
1. Join the #terminal-craft channel on Slack to ask questions, share progress, or just vibe
2. Build something sick & ship it!
3. Submit your project via **Airtable** for review!
4. Claim your Raspberry Pi 4

### Prize:
- **Raspberry Pi 4** 🖥️ 

Let's build some awesome terminal apps and hack the world together! 🌟`;
      case "prizes.md":
        return "You will get a Raspberry Pi 4 and bragging rights ;)";
      case "faq.md":
        return `# Frequently Asked Questions

Q: How many projects can I submit?
A: You can submit only one project. Make it count! Focus on quality and creativity.

Q: I need help! Where can I get assistance?
A: Join the <a href="https://hackclub.slack.com/archives/C08F58MT3GV" target="_blank" style="text-decoration: underline">#terminal-craft</a> channel on Slack! Our community is super friendly and always ready to help you out with coding, debugging, or brainstorming ideas.

Q: What programming language should I use?
A: You can use any programming language you're comfortable with! The only requirements are:
   - Include clear build/installation instructions
   - Provide either a runnable binary or detailed setup guide
   - Ensure it works across different platforms

Q: How do I share my terminal program?
A: You have several options:
   - GitHub Releases (recommended)
   - Package managers like brew.sh
   - Direct download links
   Make sure your distribution method is easily accessible!

Q: When's the deadline?
A: March 19th! Make sure to submit before 11:59 PM in your local timezone.

Q: Can my project be a game?
A: Absolutely! Games are welcome and encouraged. The terminal is your canvas - create anything from text adventures to multiplayer games. Go wild with your creativity!

Q: Do I have to use a specific framework?
A: Not at all! Use whatever tools and frameworks you're comfortable with. The focus is on building something useful or fun that runs in the terminal.

Q: What makes a good terminal project?
A: The best terminal projects are:
   - Useful or entertaining
   - Easy to install and use
   - Well-documented
   - Creative in their approach
   Remember: Simple but well-executed is better than complex but buggy!`;
      default:
        return `cat: ${filename}: No such file or directory`;
    }
  }

  function help() {
    return `
Available commands:

  ls
    Lists all available files
    Example: ls

  cat <filename>
    Reads and displays the contents of a file
    Example: cat about.md
    Example: cat faq.md

  whoami
    Displays information about the current user
    Example: whoami

  clear
    Clears the terminal screen
    Example: clear

  help
    Shows this help message with command descriptions and examples
    Example: help

  submit
    Opens the project submission form in a new tab
    Example: submit

  slack
    Open the #terminal-craft channel on Slack
    Example: slack

Note: Commands are case-sensitive. Type them exactly as shown.
    `.trim();
  }

  function hackclubFlag() {
    return `
<div class="flex flex-col items-start">
  <img src="/hackclub.svg" alt="Hack Club Flag" style="width: 300px; height: auto;" />

  <p class="mt-4">You found the secret Hack Club flag!
Keep hacking and building awesome things! 🚀</p>
</div>
    `.trim();
  }

  useEffect(() => {
    // Scroll to bottom whenever history changes
    window.scrollTo({
      top: document.documentElement.scrollHeight,
      behavior: 'smooth'
    });
  }, [history]);

  return (
    <div className="p-8 sm:p-20 min-h-screen bg-[#1E1E1E] flex items-center justify-center">
      {/* macOS Terminal Window */}
      <div className="w-full max-w-4xl bg-black rounded-lg overflow-hidden shadow-2xl">
        {/* Terminal Title Bar */}
        <div className="bg-[#2D2D2D] px-4 py-2 flex items-center gap-2 border-b border-[#404040]">
          <div className="flex gap-2">
            <div className="w-3 h-3 rounded-full bg-[#FF5F56] flex items-center justify-center">
              <div className="w-2.5 h-2.5 rounded-full bg-[#FF5F56] shadow-inner"></div>
            </div>
            <div className="w-3 h-3 rounded-full bg-[#FFBD2E] flex items-center justify-center">
              <div className="w-2.5 h-2.5 rounded-full bg-[#FFBD2E] shadow-inner"></div>
            </div>
            <div className="w-3 h-3 rounded-full bg-[#27C93F] flex items-center justify-center">
              <div className="w-2.5 h-2.5 rounded-full bg-[#27C93F] shadow-inner"></div>
            </div>
          </div>
          <div className="flex-1 text-center text-sm text-[#808080] font-medium">user@user-mac — terminalcraft</div>
        </div>
        
        {/* Terminal Content */}
        <div
          className="p-6 font-mono text-sm relative bg-black"
          onClick={() => {
            const activePrompts = Array.from(document.getElementsByTagName('input'))
              .filter(input => !input.readOnly);
            if (activePrompts.length > 0) {
              activePrompts[activePrompts.length - 1].focus();
            }
          }}
        >
          <div>
            {history.map((entry, idx) => (
              entry.type === "input" ? (
                <div key={idx} className="flex items-start">
                  <Prompt command={entry.content} readonly={true} />
                </div>
              ) : (
                !entry.content.includes("terminalcraft:") ? (
                  <pre 
                    key={idx} 
                    className="whitespace-pre-wrap break-words max-w-full text-[#4AF626] my-2"
                    dangerouslySetInnerHTML={{ __html: entry.content }}
                    style={{ lineHeight: '1.5' }}
                  ></pre>
                ) : (
                  <pre key={idx} className="whitespace-pre-wrap break-words max-w-full text-red-500 my-2">{entry.content}</pre>
                )
              )
            ))}
          </div>

          <div className="flex items-start">
            <Prompt
              command={command}
              setCommand={setCommand}
              handleCommand={handleCommand}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
