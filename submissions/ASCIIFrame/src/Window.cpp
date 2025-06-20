#include <limits>
#include <iostream>
#include "Window.hpp"
#ifdef _WIN32
    #define USE_STDOUT_DISPLAY
#else
    #define USE_NCURSES_DISPLAY
#endif

Window::Window(int x, int y, Manager& mgr) :
m_x(x),
m_y(y),
currentFrame(0),
framesCount(1),
animation(1, std::vector<std::vector<char>>(m_y, std::vector<char>(m_x, ' '))),
m_mgr(mgr) {

}
void Window::run() {
#ifdef USE_STDOUT_DISPLAY
    runConioh();
#else
    runNcurses();
#endif
}
#if defined(__linux__) || defined(__APPLE__)
void Window::runNcurses() {
    initscr();
    noecho();
    cbreak();
    keypad(stdscr, TRUE);
    nodelay(stdscr, FALSE);

    refresh();

    int current_x = 0;
    int current_y = 0;

    // Will store the character placed at the position of the cursor cause
    // the cursor will replace it
    char storedCharacter = animation[currentFrame][current_y][current_x];
    animation[currentFrame][current_y][current_x] = '@';

    // The character that will be written upon pressing enter
    char selectedChar = ' ';

    // flag to know when to place character
    bool place = false;
    // flag to know when to go to next frame
    bool nextf = false;
    // flag to know when to go to next frame
    bool prevf = false;
    // flag to delete character
    bool del = false;

    int tempX = 0;
    int tempY = 0;

    while(true) {
        display(currentFrame);
        mvprintw(m_y + 2, 0, "Current frame: %d", currentFrame+1);
        mvprintw(m_y + 3, 0, "Total frames: %d", framesCount);
        mvprintw(m_y + 4, 0, "Current selected character: %c", selectedChar);
        mvprintw(m_y + 5, 0, "CONTROLS:");
        mvprintw(m_y + 6, 0, " - Move: wsad or arrow keys");
        mvprintw(m_y + 7, 0, " - Change Character: tab");
        mvprintw(m_y + 8, 0, " - Place Character: enter");
        mvprintw(m_y + 9, 0, " - Delete Character: backspace");
        mvprintw(m_y + 10, 0, " - New Frame: n");
        mvprintw(m_y + 11, 0, " - Previous Frame: p");
        mvprintw(m_y + 12, 0, " - Play animation: e");

        int ch = getch();

        switch (ch) {
            case KEY_UP:
                if (current_y != 0) {
                    current_y--;
                }
                break;
            case KEY_DOWN:
                if (current_y != m_y - 1) {
                    current_y++;
                }
                break;
            case KEY_LEFT:
                if (current_x != 0) {
                    current_x--;
                }
                break;
            case KEY_RIGHT:
                if (current_x != m_x - 1) {
                    current_x++;
                }
                break;
            case 'w':
                if (current_y != 0) {
                    current_y--;
                }
                break;
            case 's':
                if (current_y != m_y - 1) {
                    current_y++;
                }
                break;
            case 'a':
                if (current_x != 0) {
                    current_x--;
                }
                break;
            case 'd':
                if (current_x != m_x - 1) {
                    current_x++;
                }
                break;
            case 9: // tab pressed
                selectedChar = changeCharacter();
                break;
            case '\n':
            case '\r':
            case KEY_ENTER:
                place = true;
                break;
            case 'e':
                animation[currentFrame][current_y][current_x] = storedCharacter;
                endwin();
                m_mgr.playAnimation(animation);
                initscr();
                noecho();
                cbreak();
                keypad(stdscr, TRUE);
                nodelay(stdscr, FALSE);
                refresh();
                animation[currentFrame][current_y][current_x] = '@';
                break;
            case 'q':
                endwin();
                animation[currentFrame][current_y][current_x] = storedCharacter;
                m_mgr.menu(animation);
                initscr();
                noecho();
                cbreak();
                keypad(stdscr, TRUE);
                nodelay(stdscr, FALSE);
                refresh();
                animation[currentFrame][current_y][current_x] = '@';
                break;
            case 'n':
                if (currentFrame == animation.size() - 1) {
                    animation[currentFrame][tempY][tempX] = storedCharacter;

                    framesCount++;
                    animation.push_back(animation[currentFrame]);

                    storedCharacter = animation[currentFrame+1][tempY][tempX];
                }
                nextf = true;

                break;
            case 'p':
                if (currentFrame != 0) {
                    prevf = true;
                }
                break;
            case KEY_BACKSPACE:
                del = true;
                break;
            default:
                break;
        }
        if (del) {
            animation[currentFrame][current_y][current_x] = ' ';
            storedCharacter = ' ';
            del = false;
        }

        animation[currentFrame][tempY][tempX] = storedCharacter;

        if (place) {
            animation[currentFrame][tempY][tempX] = selectedChar;
            place = false;
        }

        tempX = current_x;
        tempY = current_y;

        storedCharacter = animation[currentFrame][current_y][current_x];

        if (nextf) {
            nextf = false;
            currentFrame++;
            storedCharacter = animation[currentFrame][current_y][current_x];
        } else if (prevf) {
            currentFrame--;
            prevf = false;
        }
        if (currentFrame < animation.size()) {
            animation[currentFrame][current_y][current_x] = '@';
        }
    }
}
#endif
#ifdef _WIN32
void Window::runConioh() {
    int current_x = 0;
    int current_y = 0;

    // Will store the character placed at the position of the cursor cause
    // the cursor will replace it
    char storedCharacter = animation[currentFrame][current_y][current_x];
    animation[currentFrame][current_y][current_x] = '@';

    // The character that will be written upon pressing enter
    char selectedChar = ' ';

    // flag to know when to place character
    bool place = false;
    // flag to know when to go to next frame
    bool nextf = false;
    // flag to know when to go to next frame
    bool prevf = false;
    // flag to delete character
    bool del = false;

    int tempX = 0;
    int tempY = 0;

    while (true) {
        display(currentFrame);
        std::cout << "Current frame: " << currentFrame+1 << '\n';
        std::cout << "Total frames: " << framesCount << '\n';
        std::cout << "Current selected character:" << selectedCharacter << '\n';
        std::cout << "CONTROLS: \n - Move: wsad or arrow keys\n - Change Character: tab\n - Place Character: enter" << '\n';
        std::cout << " - Delete Character: backspace\n - Next frame: n\n - Previous Frame: p\n - Play animation: e" << '\n';
        std::cout << " - Menu: q" << '\n';
        int ch = _getch();

        // Arrow keys input
        if (ch == 224) {
            int arrow = _getch();
            switch (arrow) {
                case 72:
                    if (current_y != 0) {
                        current_y--;
                    }
                    break;
                case 80:
                    if (current_y != m_y - 1) {
                        current_y++;
                    }
                    break;
                case 75:
                    if (current_x != 0) {
                        current_x--;
                    }
                    break;
                case 77:
                    if (current_x != m_x - 1) {
                        current_x++;
                    }
                    break;
            }
        } else {
            switch (ch) {
                case 'w':
                    if (current_y != 0) {
                        current_y--;
                    }
                    break;
                case 's':
                    if (current_y != m_y - 1) {
                        current_y++;
                    }
                    break;
                case 'a':
                    if (current_x != 0) {
                        current_x--;
                    }
                    break;
                case 'd':
                    if (current_x != m_x - 1) {
                        current_x++;
                    }
                    break;
                case 9:
                    selectedChar = changeCharacter();
                    break;
                case 13:
                    place = true;
                    break;
                case 'e':
                    animation[currentFrame][current_y][current_x] = storedCharacter;
                    m_mgr.playAnimation(animation);
                    animation[currentFrame][current_y][current_x] = '@';
                    break;
                case 'q':
                    animation[currentFrame][current_y][current_x] = storedCharacter;
                    m_mgr.menu(animation);
                    animation[currentFrame][current_y][current_x] = '@';
                    break;
                case 'n':
                    if (currentFrame == animation.size() - 1) {
                        animation[currentFrame][tempY][tempX] = storedCharacter;

                        framesCount++;
                        animation.push_back(animation[currentFrame]);

                        storedCharacter = animation[currentFrame + 1][tempY][tempX];
                    }
                    nextf = true;

                    break;
                case 'p':
                    if (currentFrame != 0) {
                        prevf = true;
                    }
                    break;
                case 8:
                    del = true;
                    break;
            }
        }
        if (del) {
            animation[currentFrame][current_y][current_x] = ' ';
            storedCharacter = ' ';
            del = false;
        }
        animation[currentFrame][tempY][tempX] = storedCharacter;

        if (place) {
            animation[currentFrame][tempY][tempX] = selectedChar;
            place = false;
        }

        tempX = current_x;
        tempY = current_y;

        storedCharacter = animation[currentFrame][current_y][current_x];

        if (nextf) {
            nextf = false;
            currentFrame++;
            storedCharacter = animation[currentFrame][current_y][current_x];
        }
        else if (prevf) {
            currentFrame--;
            prevf = false;
        }
        if (currentFrame < animation.size()) {
            animation[currentFrame][current_y][current_x] = '@';
        }
    }
}
#endif
void Window::display(int currf) {
#ifdef USE_NCURSES_DISPLAY
    clear();

    // Border for the frame
    for (int i = 0; i <= m_y + 1; i++) {
        for (int j = 0; j <= m_x + 1; j++) {
            if (i == 0 || i == m_y + 1) {
                move(i, j);
                addch('-');
            } else if (j == 0 || j == m_x + 1) {
                move(i, j);
                addch('|');
            }
        }
    }
    mvaddch(0, 0, '+');
    mvaddch(0, m_x + 1, '+');
    mvaddch(m_y + 1, 0, '+');
    mvaddch(m_y + 1, m_x + 1, '+');

    // The actual content
    for (int i = 0; i < m_y; i++) {
        move(i + 1, 1);
        for (int j = 0; j < m_x; j++) {
            addch(animation[currf][i][j]);
        }
    }
    refresh();
#else
    system("cls");

    std::cout << '+';
    for (int j = 0; j < m_x; j++) {
        std::cout << '-';
    }
    std::cout << '+' << '\n';

    for (int i = 0; i < m_y; i++) {
        std::cout << '|';
        for (int j = 0; j < m_x; j++) {
            std::cout << animation[currf][i][j];
        }
        std::cout << '|' << '\n';
    }
    std::cout << '+';
    for (int j = 0; j < m_x; j++) {
        std::cout << '-';
    }
    std::cout << '+' << '\n';
#endif
}
char Window::changeCharacter() {
#ifdef USE_NCURSES_DISPLAY
    // End ncurses mode
    endwin();
#endif

    char selected = ' ';

    while (true) {
        std::cout << '\n' << "Enter the character you would like to select" << '\n';
        char option;
        std::cout << "Would you like to enter an ASCII code (type a) or a character (type c): ";
        std::cin >> option;
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

        if (option == 'a') {
            int ascii;
            std::cout << "Enter the ASCII code (33-126): ";
            std::cin >> ascii;

            if (std::cin.fail() || ascii < 33 || ascii > 126) {
                std::cout << "Invalid ASCII code! Enter a value between 33 and 126!" << '\n';
                std::cin.clear();
                std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
                continue;
            }
            selected = static_cast<char>(ascii);
            break;
        } else if (option == 'c') {
            char input;
            std::cout << "Enter a printable character: ";
            std::cin >> input;

            if (input < 33 || input > 126) {
                std::cout << "Invalid character! Enter a printable character!" << '\n';
                continue;
            }
            selected = input;
            break;
        } else {
            std::cout << "Invalid option. Please type 'a' or 'c'!" << '\n';
        }
    }
#ifdef USE_NCURSES_DISPLAY
    // Restart ncurses mode
    initscr();
    noecho();
    cbreak();
    keypad(stdscr, TRUE);
    nodelay(stdscr, FALSE);
    refresh();
#endif

    return selected;
}
