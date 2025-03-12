"use client"
import { useState, useEffect } from "react";
import Prompt from "./components/Prompt";
import Footer from "./components/Footer";
import { COMMIT_HASH } from './version';

type CommandEntry = {
  type: "input" | "output";
  content: string;
}

type EasterEggPasswords = Record<string, string>;

// Constants
const SUDO_PASSWORD = "orpheus";
const MAX_SUDO_ATTEMPTS = 3;
const VALID_FILES = ["about.md", "prizes.md", "faq.md"] as const;
type ValidFile = typeof VALID_FILES[number];

const EASTER_EGG_PASSWORDS: EasterEggPasswords = {
  '123': 'Are you kidding me? That\'s the first thing everyone tries!',
  'please': 'Being polite is good, but that\'s not the password!',
  'password': 'Really? That\'s the first thing everyone tries!',
  'root': 'Nice try, but I\'m not that simple!',
  'admin': 'Admin? This isn\'t Windows!',
  'sudo': 'Sudo is the command, not the password!',
  'hackclub': 'Close! But not quite... Think mascot!',
  '12345': 'That\'s amazing! I\'ve got the same combination on my luggage!',
  'letmein': 'Let you in? Not with that password!',
  'dinosaur': 'Rawr! But no, that\'s not it!',
  'terminalcraft': 'You\'re thinking about the right direction...',
};

export default function Home() {
  const [command, setCommand] = useState<string>('');
  const [history, setHistory] = useState<CommandEntry[]>([{
    type: "output",
    content: "type 'help' to get started"
  }]);
  const [sudoAttempts, setSudoAttempts] = useState<number>(0);
  const [awaitingSudoPassword, setAwaitingSudoPassword] = useState<boolean>(false);
  const [sudoCommand, setSudoCommand] = useState<string>('');

  // Helper functions
  const resetSudoState = () => {
    setSudoAttempts(0);
    setAwaitingSudoPassword(false);
    setSudoCommand('');
  };

  const exitApp = () => {
    resetSudoState();
    document.body.classList.add('crt-off');
    setTimeout(() => {
      window.close();
      // Fallback if window.close() is blocked
      window.location.href = "about:blank";
    }, 1000);
  };

  const addToHistory = (entries: CommandEntry[]) => {
    setHistory(prev => [...prev, ...entries]);
  };

  const handleSudoPassword = (password: string, newHistory: CommandEntry[]) => {
    setHistory(newHistory);
    
    if (password === SUDO_PASSWORD) {
      resetSudoState();
      const [cmd, ...params] = sudoCommand.trim().split(" ");
      addToHistory([
        { type: "output" as const, content: executeCommand(cmd, params) }
      ]);
    } else if (EASTER_EGG_PASSWORDS[password]) {
      setSudoAttempts(prev => prev + 1);
      addToHistory([
        { type: "output" as const, content: EASTER_EGG_PASSWORDS[password] }
      ]);
    } else if (sudoAttempts + 1 >= MAX_SUDO_ATTEMPTS) {
      resetSudoState();
      addToHistory([
        { type: "output" as const, content: "sudo: 3 incorrect password attempts" }
      ]);
    } else {
      setSudoAttempts(prev => prev + 1);
      addToHistory([
        { type: "output" as const, content: "Sorry, try again." }
      ]);
    }
  };

  function handleCommand(command: string) {
    const trimmedCommand = command.trim();

    if (command === "clear") {
      setHistory([]);
      setCommand("");
      resetSudoState();
      return;
    }

    const newHistory = [...history];
    
    if (!trimmedCommand) {
      setHistory(newHistory);
      setCommand("");
      return;
    }

    if (awaitingSudoPassword) {
      handleSudoPassword(command, newHistory);
      setCommand("");
      return;
    }

    const result = runCommand(command);
    addToHistory([
      { 
        type: "input" as const, 
        content: command 
      },
      { 
        type: "output" as const, 
        content: result 
      }
    ]);
    setCommand("");
  }

  function runCommand(fullCommand: string): string {
    const trimmedCommand = fullCommand.trim();
    if (!trimmedCommand) return "";
    
    const [command, ...params] = trimmedCommand.split(" ");
    
    if (command === "sudo") {
      const actualCommand = params[0];
      
      if (!actualCommand) {
        return "usage: sudo command";
      }

      setSudoCommand(`${actualCommand} ${params.slice(1).join(" ")}`);
      setAwaitingSudoPassword(true);
      return "[sudo] password for user:";
    }

    return executeCommand(command, params);
  }

  function executeCommand(command: string | undefined, params: string[]): string {
    switch (command) {
      case "cd":
        return params.length === 0 
          ? "cd: no directory specified" 
          : "cd: there are no directories to change to in this terminal";

      case "ls":
        if (params.length === 0) return listFiles();
        return params.map(param => 
          VALID_FILES.includes(param as ValidFile) 
            ? param 
            : `ls: ${param}: No such file or directory`
        ).join("\n");

      case "echo":
        return params.join(" ");

      case "whoami":
        return params.length > 0 
          ? `whoami: extra operand '${params[0]}'` 
          : whoami();

      case "cat":
        if (params.length === 0) return "usage: cat file ...";
        return params.map(filename => cat(filename)).join("\n");

      case "help":
        return params.length > 0 
          ? `help: too many arguments` 
          : help();

      case "rm":
        return handleRmCommand(params);

      case "hackclub":
        return params.length > 0 
          ? `hackclub: too many arguments` 
          : hackclubFlag();

      case "submit":
        if (params.length > 0) return `submit: too many arguments`;
        window.open('https://airtable.com/appzR6MIcj5G9A2Fa/pag8jn2axMXOB2lid/form', '_blank');
        return "Opening submission form in new tab...";

      case "slack":
        if (params.length > 0) return `slack: too many arguments`;
        window.open('https://hackclub.slack.com/archives/C08F58MT3GV', '_blank');
        return "Opening #terminal-craft channel on Slack...";

      case "exit":
        if (params.length > 0) return `exit: too many arguments`;
        exitApp();
        return "bash: Exiting...";

      case "clear":
        return params.length > 0 
          ? `clear: too many arguments` 
          : "";

      case undefined:
        return "";

      default:
        return `bash: command not found: ${command}`;
    }
  }

  function handleRmCommand(params: string[]): string {
    if (params.length === 0) {
      return "usage: rm [-f | -i] [-dIPRrvWx] file ...\n       unlink [--] file";
    }
    
    const isDangerous = params.join(" ").match(/(-rf|-fr|--recursive\s+--force)\s+(\/\*|--no-preserve-root\s*\/|\/)/) ||
                       params.join(" ").match(/-[rR][fF]\s+\/*/)

    if (isDangerous) {
      return [
        "               __",
        "              / _)   < You found me! But you also tried to do something dangerous. ",
        "     _.----._/ /",
        "    /         /",
        " __/ (  | (  |",
        "/__.-'|_|--|_|"
      ].join("\n");
    }
    
    return "rm: cannot remove files in this terminal";
  }

  // Content functions
  function listFiles() {
    return VALID_FILES.join(" ");
  }

  function whoami() {
    return `
    Lo, there walks among us a Hack Clubber most peculiar, one who scorns the frilly gewgaws of modern UI and finds solace in the cold, unfeeling embrace of the terminal. Where others prattle of their "drag-and-drop" and their "material design," this steadfast soul wields naught but a blinking cursor and the righteous fury of a well-placed grep. They craft tools not for the faint of heart, but for those brave enough to dance with stdin and stdout, their fingers moving with eldritch speed across the keys, summoning forth mighty applications that demand respect—or at the very least, a well-formatted man page. Speak to them of "mouse support," and they shall laugh, a grim and knowing laugh, before returning to their endless battle with sed and awk. And lo, though their ways be arcane and their scripts indecipherable to lesser mortals, those who walk the path of the terminal know: theirs is the true and noble craft, unsullied by the bloat of the modern age.
    `.trim();
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

**Q: How many projects can I submit?**
A: You can submit only one project. Make it count! Focus on quality and creativity.

**Q: I need help! Where can I get assistance?**
A: Join the <a href="https://hackclub.slack.com/archives/C08F58MT3GV" target="_blank" style="text-decoration: underline; color: #4AF626">#terminal-craft</a> channel on Slack! Our community is super friendly and always ready to help you out with coding, debugging, or brainstorming ideas.

**Q: What programming language should I use?**
A: You can use any programming language you're comfortable with! The only requirements are:
   - Include clear build/installation instructions
   - Provide either a runnable binary or detailed setup guide
   - Ensure it works across different platforms

**Q: How do I share my terminal program?**
A: You have several options:
   - GitHub Releases (recommended)
   - Package managers like brew.sh
   - Direct download links
   Make sure your distribution method is easily accessible!

**Q: When's the deadline?**
A: March 19th! Make sure to submit before 11:59 PM in your local timezone.

**Q: Can my project be a game?**
A: Absolutely! Games are welcome and encouraged. The terminal is your canvas - create anything from text adventures to multiplayer games. Go wild with your creativity!

**Q: Do I have to use a specific framework?**
A: Not at all! Use whatever tools and frameworks you're comfortable with. The focus is on building something useful or fun that runs in the terminal.

**Q: What makes a good terminal project?**
A: The best terminal projects are:
   - **Useful** or entertaining
   - **Easy** to install and use
   - **Well-documented**
   - **Creative** in their approach
   Remember: Simple but well-executed is better than complex but buggy!`;

      default:
        return `cat: ${filename}: No such file or directory`;
    }
  }

  function help() {
    return `Available commands:

  ls [file ...]
    Lists all available files or checks specific files
    Example: ls
    Example: ls about.md prizes.md

  cd [directory]
    Change directory (simulated - no actual directories available)
    Example: cd some_dir

  cat <file ...>
    Reads and displays the contents of files
    Example: cat about.md
    Example: cat faq.md prizes.md

  echo [text ...]
    Display a line of text
    Example: echo Hello, world!
    Example: echo The current date is $(date)

  whoami
    Displays information about the current user
    Example: whoami

  rm [options] <file ...>
    Simulates the remove command (doesn't actually remove files)
    Example: rm file.txt

  sudo <command>
    Execute command with superuser privileges (simulated)
    Example: sudo ls

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

Note: Commands are case-sensitive. Type them exactly as shown.`.trim();
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

  // Auto-scroll effect
  useEffect(() => {
    const terminalContent = document.querySelector('.terminal-content');
    if (terminalContent) {
      terminalContent.scrollTop = terminalContent.scrollHeight;
    }
  }, [history]);

  // Render
  return (
    <div className="min-h-screen bg-[#1E1E1E] flex flex-col">
      <div className="flex-1 flex items-center justify-center p-4">
        {/* macOS Terminal Window */}
        <div className="w-full max-w-4xl bg-black rounded-lg overflow-hidden shadow-2xl">
          {/* Terminal Title Bar */}
          <div className="bg-[#2D2D2D] px-4 py-2 flex items-center gap-2 border-b border-[#404040]">
            <div className="flex gap-2">
              <div 
                className="w-3 h-3 rounded-full bg-[#FF5F56] flex items-center justify-center cursor-pointer hover:opacity-80"
                onClick={exitApp}
              >
                <div className="w-2.5 h-2.5 rounded-full bg-[#FF5F56] shadow-inner"></div>
              </div>
              <div className="w-3 h-3 rounded-full bg-[#FFBD2E] flex items-center justify-center">
                <div className="w-2.5 h-2.5 rounded-full bg-[#FFBD2E] shadow-inner"></div>
              </div>
              <div className="w-3 h-3 rounded-full bg-[#27C93F] flex items-center justify-center">
                <div className="w-2.5 h-2.5 rounded-full bg-[#27C93F] shadow-inner"></div>
              </div>
            </div>
            <div className="flex-1 text-center text-sm text-[#808080] font-medium">
              user@user-mac — terminalcraft
            </div>
          </div>
          
          {/* Terminal Content */}
          <div
            className="terminal-content p-6 font-mono text-sm relative bg-black min-h-[400px] max-h-[70vh] overflow-y-auto"
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
                    <span className="text-gray-400 font-mono mr-2">you@hackclub ~ %</span>
                    <span className="text-white font-mono">{entry.content}</span>
                  </div>
                ) : (
                  !entry.content.includes("terminalcraft:") ? (
                    <pre 
                      key={idx} 
                      className="whitespace-pre-wrap break-words max-w-full text-[#4AF626] my-2"
                      dangerouslySetInnerHTML={{ 
                        __html: entry.content
                          // Parse headers (# Text)
                          .replace(/^(#{1,6})\s+(.+)$/gm, (_, hashes, text) => 
                            `<span class="text-yellow-400 font-bold">${text}</span>`)
                          // Parse bold text (**text**)
                          .replace(/\*\*(.+?)\*\*/g, '<span class="text-white font-bold">$1</span>')
                      }}
                      style={{ lineHeight: '1.5' }}
                    ></pre>
                  ) : (
                    <pre key={idx} className="whitespace-pre-wrap break-words max-w-full text-red-500 my-2">
                      {entry.content}
                    </pre>
                  )
                )
              ))}
            </div>

            <div className="flex items-start">
              <Prompt onCommand={handleCommand} isPassword={awaitingSudoPassword} />
            </div>
          </div>
        </div>
      </div>
      <Footer commitHash={COMMIT_HASH} />
    </div>
  );
}
