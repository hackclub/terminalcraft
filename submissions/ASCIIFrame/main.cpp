#include "src/Manager.hpp"
#include "src/Window.hpp"

int main() {
    Manager manager;
    manager.menu();

    std::pair<int, int> dimensions = manager.start();
    Window window(dimensions.first, dimensions.second, manager);
    window.run();
}