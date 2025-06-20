# **txt-to-cli**  

## 🚀 What’s This?  
Ever forget a terminal command and have to Google it? **Not anymore.**  
This script takes normal text and turns it into **real terminal commands** using Gemini AI. Just type what you want, and boom—you get the exact command for your system.  

---

## 🎯 How to Use  

### 🔧 Installation (If You Wanna Use It Properly)  
You **need** to install or add this script to your system to call it like a real command.  

---

### **🐧 Linux / 🍏 macOS Setup**  
1️⃣ **Make it executable:**  
   ```sh
   chmod +x a
   ```  
2️⃣ **Move it to a system path:**  
   ```sh
   sudo mv a /usr/local/bin/
   ```  
3️⃣ **Done!** Now just type:  
   ```sh
   a create a new folder
   ```  
   It’ll return the correct command for your OS & terminal.  

---

### **🖥️ Windows (PowerShell) Setup**  
Follow these steps to make it work on Windows like a real command.  

#### **1️⃣ Open PowerShell as Admin**  
- Search **PowerShell** in the Start Menu.  
- Right-click → **Run as administrator**.  

#### **2️⃣ Add the Script to Your Profile (Permanent Setup)**  
1️⃣ Open the PowerShell profile file:  
   ```powershell
   notepad $PROFILE
   ```  
   *(If it doesn’t exist, Notepad will ask you to create one.)*  

2️⃣ Add this to the file:  
   ```powershell
   function t { 
    python "C:\Users\Public\Documents\txt_to_cli\main.py" "$args"
}

   ```  
3️⃣ Save & close Notepad.  

4️⃣ Reload the profile:  
   ```powershell
   . $PROFILE
   ```  

---

#### **3️⃣ Create an Alias (Temporary Method, Works Only Until You Close PowerShell)**  
If you don’t wanna mess with the profile, just do this:  
   ```powershell
   New-Alias -Name t -Value "python C:\Users\Public\Documents\txt_to_cli\main.py"
   ```  
This works, but you’ll have to redo it every time you open PowerShell.  

---

#### **4️⃣ Test It!**  
Try this command:  
   ```powershell
   t list all files
   ```  
If it spits out the correct command, congrats—it’s working! 🎉  

---

#### **5️⃣ Making It Permanent (So You Don’t Have to Set It Up Again)**  
Add this to `$PROFILE` too:  
   ```powershell
   Set-Alias -Name t -Value "python C:\Users\Public\Documents\txt_to_cli\main.py"
   ```  
Now, every time you open PowerShell, `t` will work like a real command!  

---

## 🔥 Why Use This?  
✅ **Saves time**—no more Googling commands  
✅ **Works on Linux, macOS, and Windows**  
✅ **Stupidly simple to set up & use**  

---

## ⚠️ Notes  
- This script **needs an API key** for Gemini AI. Get yours [here](#).  
- It saves your OS, terminal type, and API key in `config.json`, so you only set it up once.  

