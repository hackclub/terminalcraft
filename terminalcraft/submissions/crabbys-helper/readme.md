# **Crabby's Helper CLI** 
A simple CLI tool to streamline Git workflow, track coding time with WakaTime, and manage tasks easily and ask ChatGPT questions!. 

## **Features**  
✅ Initialize Git and guide next steps  
✅ Add & commit files interactively (warns about `.env`)  
✅ Push changes to GitHub  
✅ Fetch today's WakaTime coding stats  
✅ Manage personal tasks  
✅ Ask AI stuff

---

## **Installation**  
Install globally from npm:  
```bash
npm install -g crabbys-helper
```

Verify installation:  
```bash
helper help
```

---

## **Usage**  
Run commands using:  
```bash
helper <command>
```

### **Git Commands**  
- `helper git here` → Initialize Git & guide next steps  

### **WakaTime Stats**  
- `helper get time` → Fetch coding stats  to date

### **Task Management**  
- `helper tasks` → View all tasks  
- `helper add-task` → Add a new task  
- `helper remove-task` → Remove a task

### **Ask AI**
- ` helper ask ai` → ask ChatGPT questions from the CLI

---

## **WakaTime Setup**  
Ensure you have a valid API key. Create or update your WakaTime config at:  
```bash
nano ~/.wakatime.cfg
```
Add the following:  
```
[settings]  
api_url = https://waka.hackclub.com/api  
api_key = your-api-key-here  
```

---


## **Contributing**  
Pull requests are welcome! Open an issue if you find a bug. 
Pls fix my git bug it driving me crazy now removed it for now you can ask me on slack for the details.

--- 
