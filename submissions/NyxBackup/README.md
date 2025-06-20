# NyxBackup

NyxBackup is a cross-platform terminal app that lets you create and manage compressed backups of directories.

---

## Features  
✅ Backup any folder as .zip or .tar.gz  
✅ Auto-names with timestamp  
✅ Keeps log of all backups  
✅ List backup history in table form  
✅ Clean up old backups by age  
✅ No external tools required  

---

## Installation  

### Requirements  
- Python 3.7+  

### Install dependencies  
```
pip install -r requirements.txt
```

---

## Usage  

### Create a backup  
```
python nyxbackup.py backup
```

### List backups  
```
python nyxbackup.py list
```

### Clean old backups (default: 30 days)  
```
python nyxbackup.py clean --days 30
```

---

## Packaging  

To create standalone executable:  
```
pip install pyinstaller
pyinstaller --onefile nyxbackup.py
```  
Binaries will be in `dist/`.  

---

## License  

MIT License
