# Advanced CLI Task Manager 🎉🚀

A feature-rich command-line interface (CLI) task management tool built in Python. This application allows users to create, edit, delete, and manage tasks with priorities, due dates, categories, progress tracking, and more. It includes a user authentication system, task persistence, and an engaging loading animation. 🌟📋

## Table of Contents 📑
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

## Features ✨
- **Task Management**: Add, edit, delete, and toggle task completion. ✅✏️🗑️
- **Task Details**: Set titles, descriptions, priorities (low/medium/high), due dates, categories, progress (0-100%), effort hours, dependencies, and recurrence (none/daily/weekly). 📝📅🔧
- **Sorting and Filtering**: Sort by priority, due date, or creation time; filter by category. 🔄🔍
- **Search**: Search tasks by keyword with date range filters. 🔎📅
- **Export/Import**: Export tasks to JSON or CSV, and import from the same formats. 📤📥
- **Dashboard**: View task statistics (total, completed, overdue). 📊📈
- **Categories**: Manage custom task categories. 🗂️
- **Undo**: Undo the last task deletion. 🔙
- **Animations**: Loading screen with progress bar and idle wave pattern animation. 🎬🌊
- **Persistence**: Tasks are saved to a JSON file with automatic backups. 💾🔧
- **Notifications**: In-app alerts for tasks due within 1 hour. 🔔⏰

## Installation 🛠️
1. **Clone the Repository**  
   ```bash
   git clone https://github.com/kaustubhkharvi/task-manager.git
   cd task-manager
   ```
2. **Install Dependencies**  
   Ensure you have Python 3.6+ installed. No additional libraries are required as the script uses the standard library. 🐍
3. **Run the Script**  
   ```bash
   python3 main.py
   ```

## Usage 🎮
1. Log in with the default credentials (`username: default`, `password: default123`) or create a new user by editing `users.json`. 🔐
2. Use the numbered menu to select options (e.g., `1` for Add Task, `14` to Exit). 🔢
3. Follow the prompts to manage tasks. Press `Enter` to continue after each action. ⏎
4. Navigate task lists with `p` (previous), `n` (next), `d` (details), or `q` (quit). 🗺️

### Example Commands
- Add a task: Select `1`, enter title, description, etc. ✅
- View tasks: Select `13`, navigate with `n` or `p`. 👀
- Export tasks: Select `9`, choose format (json/csv), and enter a filename. 📤

## Screenshots 📸

![image](images/image.png) 📷
![image](images/image(1).png) 📷
![image](images/image(2).png) 📷

## Contributing 🤝
1. Fork the repository. 🍴
2. Create a feature branch (`git checkout -b feature-name`). 🌿
3. Commit your changes (`git commit -m "Add feature-name"`). 💾
4. Push to the branch (`git push origin feature-name`). 🚀
5. Open a Pull Request with a description of your changes. 📩

## License 📜
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details. ⚖️
