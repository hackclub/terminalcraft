#ifndef WINDOW_HPP
#define WINDOW_HPP

#include "Manager.hpp"
#ifdef _WIN32
#include <conio.h>
#else
#include <ncurses.h>
#endif

class Window {
private:
    int m_x;
    int m_y;

    int currentFrame;
    int framesCount;
    std::vector<std::vector<std::vector<char>>> animation;

    void runNcurses();
    void runConioh();
    void display(int currf);
    char changeCharacter();

    Manager& m_mgr;
public:
    Window(int x, int y, Manager& mgr);
    ~Window() = default;
    void run();
};

#endif //WINDOW_HPP
