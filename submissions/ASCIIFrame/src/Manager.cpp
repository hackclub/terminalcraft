#ifdef _WIN32
#include <windows.h> // for Sleep()
#define USE_SLEEP
#else
#include <unistd.h> // for usleep
#define USE_USLEEP
#endif
#include "Manager.hpp"

#include <limits>

Manager::Manager() : fps(0) {

}
std::pair<int, int> Manager::start() {
#ifdef USE_SLEEP
    system("cls");
#endif
    std::cout << "Choose the dimensions of the window: " << '\n' << '\n';
    int x, y;
    std::cout << "X (min 5, recommended 30, max 250): "; std::cin >> x;
    std::cout << "Y (min 5, recommended 15, max 100): "; std::cin >> y;
    if (x < 5) {
        std::cout << "Changed x to 5 (minimum value)!" << '\n';
        x = 5;
    }
    if (y < 5) {
        std::cout << "Changed y to 5 (minimum value)!" << '\n';
        y = 5;
    }
    if (x > 250) {
        std::cout << "Changed x to 250 (maximum value)!" << '\n';
        x = 250;
    }
    if (y > 100) {
        std::cout << "Changed y to 100 (maximum value)!" << '\n';
        y = 100;
    }
    std::cout << '\n' << "This is how the cursor looks like: @" << '\n';
    std::cout << "Press any key to continue (recommended enter)" << '\n';
    std::cin.ignore();
    std::cin.get();

#ifdef USE_USLEEP
    system("clear");
#endif

    return { x, y };
}
void Manager::menu() {
    std::cout << "Welcome to ASCIIFrame!" << '\n' << '\n';
    while (true) {
        std::cout << "1. Start" << '\n';
        std::cout << "2. Exit" << '\n' << '\n';
        std::cout << "You can load and save after the frame loads!" << '\n';
        char choice;
        std::cin >> choice;

        if (choice == '1') {
            return;
        } else if (choice == '2') {
            exit(0);
        } else {
            std::cout << "Invalid choice!" << '\n' << '\n';
        }
    }
}
void Manager::menu(std::vector<std::vector<std::vector<char>>>& _a) {
    std::cout << "ASCIIFrame MENU!" << '\n' << '\n';
    while (true) {
        std::cout << "1. Resume" << '\n';
        std::cout << "2. Exit" << '\n';
        std::cout << "3. Save" << '\n';
        std::cout << "4. Load" << '\n';
        char choice;
        std::cin >> choice;

#ifdef USE_USLEEP
        system("clear");
#else
        system("cls");
#endif
        if (choice == '1') {
            return;
        } else if (choice == '2') {
            exit(0);
        } else if (choice == '3') {
            std::cout << "Name the file you would like to save: ";
            std::string name;
            std::cin >> name;
            save(name, _a);
        } else if (choice == '4') {
            std::cout << "Enter the name of the file you would like to load: ";
            std::string name;
            std::cin >> name;
            load(name, _a);
            break;
        } else {
            std::cout << "Invalid choice!" << '\n' << '\n';
        }
    }
}
void Manager::save(std::string filename, const std::vector<std::vector<std::vector<char>>>& a) {
    std::cout << "How many directories you need to go up to get to saved folder from build directory (usually one)?" << '\n';
    int up;
    std::cin >> up;
    std::string filePath;
    for (int i = 0; i < up; i++) {
        filePath += "../";
    }
    filePath += "saved/";
    filePath += filename;
    std::ofstream ofs(filePath);

    int height = a[0].size();
    int width = a[0][0].size();
    ofs << height << ' ' << width << '\n';

    for (const auto& frame : a) {
        for (const auto& row : frame) {
            for (char c : row) {
                ofs << c;
            }
            ofs << '\n';
        }
        ofs << "===FRAME===" << '\n';
    }
    ofs.close();
    std::cout << "Save succesful! Check saved directory!";
    exit(0);
}
void Manager::load(std::string fileName, std::vector<std::vector<std::vector<char>>>& a) {
    std::cout << "How many directories you need to go up to get to saved folder from build directory (usually one)?" << '\n';
    int up;
    std::cin >> up;
    std::string filePath;
    for (int i = 0; i < up; i++) {
        filePath += "../";
    }
    filePath += "saved/";
    filePath += fileName;
    std::ifstream ifs(filePath);

    if (!ifs) {
        throw std::runtime_error("File not found!");
    }

    int height = 0, width = 0;
    ifs >> height >> width;
    ifs.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    if (height != a[0].size() || width != a[0][0].size()) {
        std::cout << "The file youre trying to load is " << height << "x" << width << '\n';
        std::cout << "while your current window is " << a[0].size() << "x" << a[0][0].size() << '\n';
        std::cin.ignore();
        std::cin.get();
        return;
    }
    a.clear();

    std::string line;
    std::vector<std::vector<char>> current_frame;

    while (std::getline(ifs, line)) {
        if (line == "===FRAME===") {
            if (!current_frame.empty()) {
                a.push_back(current_frame);
                current_frame.clear();
            }
        } else {
            std::vector<char> row(line.begin(), line.end());
            current_frame.push_back(row);
        }
    }

    if (!current_frame.empty()) {
        a.push_back(current_frame);
    }
}
void Manager::playAnimation(const std::vector<std::vector<std::vector<char>>>& a) {
#ifdef USE_SLEEP
    system("cls");
#endif
    char option;
    if (fps != 0) {
        std::cout << "Would you like to change the frames per second value? (t/n): ";
        std::cin >> option;
    }
    if (fps == 0 || option == 't') {
        std::cout << "Please set frames per second: ";
        std::cin >> fps;
        if (fps < 1) {
            std::cout << "Set frames per second to 1 (minimum value)!" << '\n';
            fps = 1;
        } else if (fps > 60) {
            std::cout << "Set frames per second to 60 (maximum value)!" << '\n';
            fps = 60;
        }
    }
    int frameDelay = 1000000 / fps;
    int frameCount = a.size();
    int frameHeight = a[0].size();
    int frameWidth = a[0][0].size();

#ifdef USE_SLEEP
    system("cls");
#else
    system("clear");
#endif

    for (int i = 0; i < frameCount; i++) {
        // Top border
        std::cout << '+';
        for (int j = 0; j < frameWidth; j++) {
            std::cout << '-';
        }
        std::cout << '+' << '\n';

        // Frame content
        for (int j = 0; j < frameHeight; j++) {
            std::cout << '|';
            for (int k = 0; k < frameWidth; k++) {
                std::cout << a[i][j][k];
            }
            std::cout << '|' << '\n';
        }

        // Bottom border
        std::cout << '+';
        for (int j = 0; j < frameWidth; j++) {
            std::cout << '-';
        }
        std::cout << '+' << '\n';

#ifdef USE_SLEEP
        Sleep(frameDelay / 1000);
        system("cls");
#else
        usleep(frameDelay);
        system("clear");
#endif
    }
}