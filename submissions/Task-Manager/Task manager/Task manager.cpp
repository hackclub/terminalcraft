#include <iostream>
#include <string>
#include <vector>
#include <cctype>
#include <cmath>
#include <fstream>
#include <limits> // Add this to include numeric_limits

using namespace std;

// Load inventory
struct Item {
    string name;
    int count;
    string description;
};

vector<Item> inventory;

void loadInventory() {
    ifstream inFile("inventory.txt");
    if (!inFile) {
        cerr << "Error opening inventory file!" << endl;
        return;
    }

    Item item;
    while (getline(inFile, item.name)) {
        inFile >> item.count;
        inFile.ignore(numeric_limits<streamsize>::max(), '\n');
        getline(inFile, item.description);
        inventory.push_back(item);
    }
    inFile.close();
}

// Save inventory
void saveInventory() {
    ofstream outFile("inventory.txt", ios::trunc);
    if (!outFile) {
        cerr << "Error opening inventory file for saving!" << endl;
        return;
    }

    for (const auto& item : inventory) {
        outFile << item.name << endl;
        outFile << item.count << endl;
        outFile << item.description << endl;
    }
    outFile.close();
}

// Load tasks
vector<string> taskKeeper;

void loadTasks() {
    ifstream inFile("tasks.txt");
    if (!inFile) {
        cerr << "Error opening tasks file!" << endl;
        return;
    }

    string task;
    while (getline(inFile, task)) {
        taskKeeper.push_back(task);
    }
    inFile.close();
}

// Save tasks
void saveTasks() {
    ofstream outFile("tasks.txt");
    if (!outFile) {
        cerr << "Error opening tasks file for saving!" << endl;
        return;
    }

    for (const auto& task : taskKeeper) {
        outFile << task << endl;
    }
    outFile.close();
}

// Clear command line
void clearScreen() {
    #ifdef _WIN32
        system("CLS");
    #else
        system("clear");
    #endif
}

// Main Menu Function
void mainMenu() {
    clearScreen();
    cout << "Hello, welcome to the task manager, please type a number for the action you want to execute:" << endl;
    cout << "0. Main Menu\n1. To Do List\n2. Calculator\n3. Inventory\n4. Exit" << endl;
}

// Expression function
double Expression(const string& operation) {
    double result = 0;
    double num = 0;
    double prevNum = 0;
    char op = '+';
    size_t i = 0;
    bool isDecimal = false;
    double decimalPlace = 0.1;

    while (i < operation.length()) {
        char c = operation[i];

        if (isdigit(c)) {
            if (!isDecimal) {
                num = num * 10 + (c - '0');
            } else {
                num += (c - '0') * decimalPlace;
                decimalPlace /= 10;
            }
        } else if (c == '.') {
            isDecimal = true;
        }

        if ((!isdigit(c) && c != ' ' && c != '.' || i == operation.length() - 1)) {
            if (op == '*') {
                prevNum *= num;
            } else if (op == '/') {
                if (num != 0) prevNum /= num;
                else {
                    cerr << "Error: Division by zero!" << endl;
                    return 0;
                }
            } else if (op == '+') {
                result += prevNum;
                prevNum = num;
            } else if (op == '-') {
                result += prevNum;
                prevNum = -num;
            }

            op = c;
            num = 0;
            isDecimal = false;  // Reset decimal flag
            decimalPlace = 0.1;
        }

        i++;
    }

    result += prevNum;
    return result;
}

// Task functions
void displayTasks() {
    cout << "\nYour To-Do List:" << endl;
    if (taskKeeper.empty()) {
        cout << "No tasks to display!" << endl;
    } else {
        for (size_t i = 0; i < taskKeeper.size(); i++) {
            cout << i + 1 << ". " << taskKeeper[i] << endl;
        }
    }
}

void addTask() {
    string Task;
    cout << "Enter a task (or type 'L' to finish): ";

    while (true) {
        getline(cin, Task);

        if (Task.empty()) {
            cout << "Task cannot be empty. Please enter a valid task." << endl;
            continue;
        }

        if (Task == "L") {
            cout << "Exiting task addition." << endl;
            break;
        }

        taskKeeper.push_back(Task);
        cout << "Task added. Enter another task (or type 'L' to finish): ";
    }
}

void removeTask() {
    int taskNumber;
    displayTasks();

    if (!taskKeeper.empty()) {
        cout << "Enter the task number you want to remove: ";
        cin >> taskNumber;
        cin.ignore(numeric_limits<streamsize>::max(), '\n');

        if (taskNumber > 0 && taskNumber <= taskKeeper.size()) {
            taskKeeper.erase(taskKeeper.begin() + taskNumber - 1);
            cout << "Task removed!" << endl;
        } else {
            cout << "Invalid task number!" << endl;
        }
    }
}

// Main function
int main() {
    loadTasks();
    int options = 0;

    do {
        mainMenu();
        cin >> options;
        cin.ignore();

        if (options < 0 || options > 4) {
            while (options < 0 || options > 4) {
                cout << "Invalid option. Please enter a valid number (0-4): ";
                cin >> options;
                cin.ignore();
            }
        }

        if (options == 0) {
            clearScreen();
            cout << "You are in the main menu." << endl;
        }

        // Option 1 - To Do List
        if (options == 1) {
            clearScreen();
            int option;
            while (true) {
                cout << "\nTask Menu:" << endl;
                cout << "1. Add a task" << endl;
                cout << "2. Remove a task" << endl;
                cout << "3. Display tasks" << endl;
                cout << "4. Exit" << endl;
                cout << "Choose an option: ";
                cin >> option;
                cin.ignore();

                switch (option) {
                    case 1: addTask(); break;
                    case 2: removeTask(); break;
                    case 3: displayTasks(); break;
                    case 4: cout << "Exiting task menu..." << endl; break;
                    default: cout << "Invalid option, please try again!" << endl;
                }

                if (option == 4) break;
            }
        }

        // Option 2 - Calculator
        if (options == 2) {
            clearScreen();
            string operation;
            cout << "Enter equations or type 'exit' to leave: ";
            while (true) {
                getline(cin, operation);
                if (operation == "exit") break;

                if (operation.empty()) {
                    cout << "No input entered!" << endl;
                    continue;
                }

                double result = Expression(operation);
                cout << "Result: " << result << endl;
                cout << "Enter another equation or type 'exit' to leave: ";
            }
        }

        // Option 3 - Item tracking
        if (options == 3) {
            loadInventory();
            clearScreen();
            string userChoice1;

            do {
                cout << "Inventory Menu:\n1. Add Item\n2. View Inventory\n3. Return to Main Menu\n";
                int choice;
                cin >> choice;
                cin.ignore();

                if (choice == 1) {
                    Item newItem;

                    cout << "Please enter item name:" << endl;
                    getline(cin, newItem.name);

                    cout << "Please enter item count:" << endl;
                    cin >> newItem.count;
                    cin.ignore();

                    cout << "Please enter item description:" << endl;
                    getline(cin, newItem.description);

                    inventory.push_back(newItem);
                    saveInventory();
                } else if (choice == 2) {
                    cout << "\nCurrent Inventory:\n";
                    for (size_t i = 0; i < inventory.size(); i++) {
                        cout << i + 1 << ". Name: " << inventory[i].name
                             << ", Count: " << inventory[i].count
                             << ", Description: " << inventory[i].description << endl;
                        cout << endl;
                    }
                } else {
                    saveInventory();
                    break;
                }

            } while (true);
        }

        // Option 4 - Exit program
        if (options == 4) {
            cout << "Exiting program..." << endl;
            break;
        }

    } while (options != 4);

    return 0;
}
