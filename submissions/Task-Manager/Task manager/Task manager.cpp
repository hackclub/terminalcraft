#include <iostream>
#include <string>
#include <vector>
#include <cctype>
#include <cmath>
#include <fstream>
#include <limits>
#include <sstream>
#include <algorithm>
#include <sys/stat.h>
#include <dirent.h>

using namespace std;


// Clear command line
void clearScreen() {
#ifdef _WIN32
    system("CLS");
#else
    system("clear");
#endif
}


void createDirectory(const string& path) {
    #ifdef _WIN32
        mkdir(path.c_str());
    #else
        mkdir(path.c_str(), 0777);
    #endif
}


bool directoryExists(const string& path) {
    DIR* dir = opendir(path.c_str());
    if (dir) {
        closedir(dir);
        return true;
    }
    return false;
}


string currentBusiness;
vector<string> businesses;

void loadBusinesses() {
    ifstream inFile("businesses.txt");
    if (!inFile) return;

    string business;
    while (getline(inFile, business)) {
        businesses.push_back(business);
    }
    inFile.close();
}

void saveBusinesses() {
    ofstream outFile("businesses.txt", ios::trunc);
    if (!outFile) {
        cerr << "Error saving businesses!" << endl;
        return;
    }

    for (const auto& business : businesses) {
        outFile << business << endl;
    }
    outFile.close();
}

void ensureBusinessDirectory() {
    if (currentBusiness.empty()) return;

    string dirPath = "businesses/" + currentBusiness;
    if (!directoryExists(dirPath)) {
        createDirectory(dirPath);
    }
}

bool selectBusiness() {
    clearScreen();
    cout << "Available Businesses:\n";
    for (size_t i = 0; i < businesses.size(); i++) {
        cout << i + 1 << ". " << businesses[i] << endl;
    }
    cout << businesses.size() + 1 << ". Create new business\n";
    cout << "0. Exit\n";
    cout << "Select an option: ";

    int choice;
    cin >> choice;
    cin.ignore();

    if (choice == 0) return false;

    if (choice == static_cast<int>(businesses.size()) + 1) {
        cout << "Enter new business name: ";
        string newBusiness;
        getline(cin, newBusiness);

        if (find(businesses.begin(), businesses.end(), newBusiness) != businesses.end()) {
            cout << "Business already exists!" << endl;
            return selectBusiness();
        }

        businesses.push_back(newBusiness);
        saveBusinesses();
        currentBusiness = newBusiness;
        ensureBusinessDirectory();
    } else if (choice > 0 && choice <= static_cast<int>(businesses.size())) {
        currentBusiness = businesses[choice - 1];
    } else {
        cout << "Invalid choice!" << endl;
        return selectBusiness();
    }

    return true;
}

// Inventory
struct Item {
    string name;
    int count;
    string description;
};

vector<Item> inventory;

void loadInventory() {
    if (currentBusiness.empty()) return;

    string filename = "businesses/" + currentBusiness + "/inventory.txt";
    ifstream inFile(filename);
    if (!inFile) return;

    inventory.clear();
    Item item;
    while (getline(inFile, item.name)) {
        inFile >> item.count;
        inFile.ignore(numeric_limits<streamsize>::max(), '\n');
        getline(inFile, item.description);
        inventory.push_back(item);
    }
    inFile.close();
}

void saveInventory(bool forceSave = false) {
    if (currentBusiness.empty()) return;

    static bool saved = true;
    if (saved && !forceSave) return;

    ensureBusinessDirectory();
    string filename = "businesses/" + currentBusiness + "/inventory.txt";
    ofstream outFile(filename, ios::trunc);
    if (!outFile) {
        cerr << "Error saving inventory!" << endl;
        return;
    }

    for (const auto& item : inventory) {
        outFile << item.name << endl;
        outFile << item.count << endl;
        outFile << item.description << endl;
    }
    outFile.close();
    saved = true;
}

// Tasks
vector<string> taskKeeper;
vector<bool> taskStatus;

void loadTasks() {
    if (currentBusiness.empty()) return;

    taskKeeper.clear();
    taskStatus.clear();

    string filename = "businesses/" + currentBusiness + "/tasks.txt";
    ifstream inFile(filename);
    if (!inFile) {

        return;
    }

    string task;
    bool status;
    while (getline(inFile, task)) {
        if (task.empty()) continue;
        inFile >> status;
        inFile.ignore(numeric_limits<streamsize>::max(), '\n');
        taskKeeper.push_back(task);
        taskStatus.push_back(status);
    }
    inFile.close();
}

void saveTasks() {
    if (currentBusiness.empty()) return;

    ensureBusinessDirectory();
    string filename = "businesses/" + currentBusiness + "/tasks.txt";
    ofstream outFile(filename, ios::trunc);
    if (!outFile) {
        cerr << "Error saving tasks to: " << filename << endl;
        return;
    }

    for (size_t i = 0; i < taskKeeper.size(); i++) {
        outFile << taskKeeper[i] << endl;
        outFile << taskStatus[i] << endl;
    }
    outFile.close();
}

// Calculator
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

        if ((!isdigit(c) && c != ' ' && c != '.') || i == operation.length() - 1) {
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
            isDecimal = false;
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
            cout << i + 1 << ". " << taskKeeper[i] << " [Status: "
                 << (taskStatus[i] ? "Completed" : "In Progress") << "]" << endl;
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
        taskStatus.push_back(false);
        saveTasks();
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

        if (taskNumber > 0 && taskNumber <= static_cast<int>(taskKeeper.size())) {
            taskKeeper.erase(taskKeeper.begin() + taskNumber - 1);
            taskStatus.erase(taskStatus.begin() + taskNumber - 1);
            saveTasks();
            cout << "Task removed!" << endl;
        } else {
            cout << "Invalid task number!" << endl;
        }
    }
}

void markTaskAsCompleted() {
    int taskNumber;
    displayTasks();

    if (!taskKeeper.empty()) {
        cout << "Enter the task number you want to mark as completed: ";
        cin >> taskNumber;
        cin.ignore(numeric_limits<streamsize>::max(), '\n');

        if (taskNumber > 0 && taskNumber <= static_cast<int>(taskKeeper.size())) {
            taskStatus[taskNumber - 1] = true;
            saveTasks();
            cout << "Task marked as completed!" << endl;
        } else {
            cout << "Invalid task number!" << endl;
        }
    }
}

// Inventory functions
void editItem() {
    int itemNumber;
    cout << "Enter the number of the item you want to edit: ";
    cin >> itemNumber;
    cin.ignore();

    if (itemNumber <= 0 || itemNumber > static_cast<int>(inventory.size())) {
        cout << "Invalid item number!" << endl;
        return;
    }

    Item& item = inventory[itemNumber - 1];
    cout << "Editing item: " << item.name << endl;

    cout << "Enter new name (or press Enter to keep unchanged): ";
    string newName;
    getline(cin, newName);
    if (!newName.empty()) {
        item.name = newName;
    }

    cout << "Enter new count (or press Enter to keep unchanged): ";
    string newCount;
    getline(cin, newCount);
    if (!newCount.empty() && isdigit(newCount[0])) {
        item.count = stoi(newCount);
    }

    cout << "Enter new description (or press Enter to keep unchanged): ";
    string newDescription;
    getline(cin, newDescription);
    if (!newDescription.empty()) {
        item.description = newDescription;
    }

    saveInventory(true);
}

void removeItem() {
    int itemNumber;
    cout << "Enter the number of the item you want to remove: ";
    cin >> itemNumber;
    cin.ignore();

    if (itemNumber <= 0 || itemNumber > static_cast<int>(inventory.size())) {
        cout << "Invalid item number!" << endl;
        return;
    }

    inventory.erase(inventory.begin() + itemNumber - 1);
    saveInventory(true);
    cout << "Item removed!" << endl;
}

// Main Menu Function
void mainMenu() {
    clearScreen();
    cout << "Current business: " << currentBusiness << endl;
    cout << "Main Menu:\n0. Main Menu\n1. To Do List\n2. Calculator\n3. Inventory\n4. Switch Business\n5. Exit" << endl;
}

// Main function
int main() {

    loadBusinesses();

    if (!selectBusiness()) {
        return 0;
    }

    loadInventory();
    loadTasks();

    int options = 0;
    do {
        mainMenu();
        cin >> options;
        cin.ignore();

        if (options < 0 || options > 5) {
            while (options < 0 || options > 5) {
                cout << "Invalid option. Please enter a valid number (0-5): ";
                cin >> options;
                cin.ignore();
            }
        }

        if (options == 0) {
            clearScreen();
            cout << "Current business: " << currentBusiness << endl;
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
                cout << "4. Mark task as completed" << endl;
                cout << "5. Exit" << endl;
                cout << "Choose an option: ";
                cin >> option;
                cin.ignore();

                switch (option) {
                    case 1: addTask(); break;
                    case 2: removeTask(); break;
                    case 3: displayTasks(); break;
                    case 4: markTaskAsCompleted(); break;
                    case 5: cout << "Exiting task menu..." << endl; break;
                    default: cout << "Invalid option, please try again!" << endl;
                }

                if (option == 5) break;
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
            clearScreen();
            string userChoice1;

            do {
                cout << "Inventory Menu:\n1. Add Item\n2. Edit Item\n3. Remove Item\n4. View Inventory\n5. Return to Main Menu\n";
                int choice;
                cin >> choice;
                cin.ignore();

                if (choice == 1) {
                    Item newItem;

                    cout << "Please enter item name:" << endl;
                    getline(cin, newItem.name);

                    cout << "Please enter item count:" << endl;
                    while (true) {
                        string countStr;
                        getline(cin, countStr);
                        if (isdigit(countStr[0])) {
                            newItem.count = stoi(countStr);
                            break;
                        }
                        cout << "Please enter a valid number for count: ";
                    }

                    cout << "Please enter item description:" << endl;
                    getline(cin, newItem.description);

                    inventory.push_back(newItem);
                    saveInventory(true);
                    cout << "Item added successfully!" << endl;
                } else if (choice == 2) {
                    editItem();
                } else if (choice == 3) {
                    removeItem();
                } else if (choice == 4) {
                    cout << "\nCurrent Inventory:\n";
                    for (size_t i = 0; i < inventory.size(); i++) {
                        cout << i + 1 << ". Name: " << inventory[i].name
                             << ", Count: " << inventory[i].count
                             << ", Description: " << inventory[i].description << endl;
                    }
                } else {
                    saveInventory(true);
                    break;
                }

            } while (true);
        }


        if (options == 4) {
            saveInventory(true);
            saveTasks();
            if (!selectBusiness()) {
                options = 5;
            } else {
                loadInventory();
                loadTasks();
            }
        }

    } while (options != 5);

    saveInventory(true);
    saveTasks();
    return 0;
}
