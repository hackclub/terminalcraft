from sty import fg, ef, rs # For cross-platform color coding

RESET = fg.rs + ef.rs
RED = fg.red
BLUE = fg.blue
GREEN = fg.green
YELLOW = fg.yellow
BOLD = ef.bold

# Creat a list of tasks.
tasks = []


def addTask():
    task = input(f"{BLUE}Please enter a task: {RESET}")
    tasks.append(task)
    print(f"{BOLD}{GREEN}Task '{task}' added to the list.{RESET}")


def listTasks():
    if not tasks:
        print(f"{RED}{BOLD}There are no tasks currently{RESET}")
    else:
        print(f"{BOLD}{GREEN}Current Tasks:{RESET}")
        for index, task in enumerate(tasks):
            print(f"{BOLD}Task # {index + 1}. {task}\n{RESET}")


def deleteTask():
    listTasks()
    try:
        taskToDelete = int(input(f"{BLUE}Enter the # to delete:{RESET}")) - 1
        if taskToDelete <= 0 and taskToDelete < len(tasks):
            tasks.pop(taskToDelete)
            print(f"{BOLD}{GREEN}Task # {taskToDelete} has been removed {RESET}")
        else:
            print(f"{RED}{BOLD}Task # {taskToDelete} does not exist{RESET}")

    except:
        print(f"{RED}{BOLD}Invalid input.{RESET}")
        
def editTask():
    listTasks()
    if len(tasks) == 0:
        return
    try:
        taskToEdit = int(input(f"{BLUE}What task would you like to edit? {RESET}")) - 1
        if taskToEdit <= 0 and taskToEdit < len(tasks):
            edit = input(f"{BOLD}What would you want to edit the task to?{RESET}")
            tasks[taskToEdit] = edit
            print(f"{BOLD}{GREEN}Task # {taskToEdit} has been changed to {edit}{RESET}")
        else:
            print(f"{RED}{BOLD}Task # {taskToEdit} does not exist{RESET}")

    except:
        print(f"{RED}{BOLD}Invalid input.{RESET}")
            
if __name__ == "__main__":
    ### Create a loop  
    print(f"{GREEN}{BOLD}Welcome to the to-do list app:{RESET}")
    
    while True:
        ### Ask the user for a task
        print("\n")
        print(f"{BOLD}Please select one of the following options:{RESET}") 
        print("-------------------------------------------") 
        print(f"{BOLD}{RED}1. Add a new task{RESET}")
        print(f"{BOLD}{YELLOW}2. Delete a task{RESET}")
        print(f"{BOLD}{BLUE}3. List tasks{RESET}")
        print(f"{BOLD}{GREEN}4. Edit task{RESET}")
        print(f"{BOLD}{RED}5. Quit{RESET}")
        
        choice = input(f"\n{BLUE}Enter your choice: {RESET}")
        if(choice == "1"):
            addTask()        
        elif(choice == "2"):
            deleteTask()
        elif(choice == "3"):
            listTasks()
        elif(choice == "4"):
            editTask()
        elif(choice == "5"):
            break
        else:
            print(f"{RED}{BOLD}Invalid input. Please try again.{RESET}")
            
    print(f"{BOLD}{GREEN}\nGoodbye👋👋{RESET}")
