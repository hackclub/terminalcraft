#ifndef MENU_HPP
#define MENU_HPP

#include <cstdlib>
#include <iostream>
#include <fstream>
#include <utility>
#include <vector>

class Manager {
private:
    int fps;
public:
    Manager();
    ~Manager() = default;
    std::pair<int, int> start();
    void menu();
    void menu(std::vector<std::vector<std::vector<char>>> &_a);
    void save(std::string fileName, const std::vector<std::vector<std::vector<char>>> &a);
    void load(std::string fileName, std::vector<std::vector<std::vector<char>>> &a);
    void playAnimation(const std::vector<std::vector<std::vector<char>>>& a);
};

#endif //MENU_HPP
