# PetVerse: Virtual Pet Simulator

Welcome to PetVerse, a terminal-based virtual pet game where you can adopt, raise, and interact with your own digital companions. This project simulates a persistent world where your pets have unique needs, behaviors, and talents.

## Features

- **Pet Management**: Create, select, and manage multiple virtual pets.
- **Needs Simulation**: Pets have dynamic needs such as hunger, happiness, and energy that you must manage.
- **Behavior System**: Pets exhibit different behaviors based on their current needs and mood.
- **Interactive Mini-Games**: Engage with your pets through various mini-games, including feeding, training, grooming, and adventuring.
- **Customization**: Personalize your pets with different colors, hats, and accessories.
- **Marketplace**: Buy and sell items, food, and customization options in the in-game marketplace.
- **Housing System**: Decorate your pet's living space with furniture.
- **Dynamic World**: An in-game world with a persistent time and weather system that influences gameplay.
- **Save/Load**: Your game progress is automatically saved and can be loaded later.


## How to Run the Game

To start the game, run the `main.py` script from your terminal:

```bash
python main.py
```

Or, on Windows systems:

```bash
py main.py
```

## Project Structure

The project is organized into several modules to separate concerns:

-   `main.py`: The main entry point for the application. It contains the primary game loop and orchestrates the different game systems.
-   `test_runner.py`: A script for running automated tests for the project.

-   **`pets/`**: This package contains all logic related to the pets themselves.
    -   `pet_base.py`: Defines the fundamental `Pet` class with its core attributes and methods.
    -   `species.py`: Manages the different available pet species and their creation.
    -   `customization.py`: Handles the logic for customizing a pet's appearance.
    -   `talents.py`: Manages the talent and skill system for pets.

-   **`simulation/`**: This package handles the background simulation engines that create a dynamic world.
    -   `needs.py`: The engine for simulating and updating pet needs over time.
    -   `behavior.py`: The engine that determines a pet's current behavior based on its state.
    -   `weather.py`: Simulates weather patterns that can affect the game.
    -   `time_system.py`: Manages the in-game clock and calendar.

-   **`mini_games/`**: This package contains the implementation of the various interactive mini-games.
    -   `adventure_game.py`: A game where pets can go on adventures to find items.
    -   `feeding_game.py`: The mini-game for feeding your pet.
    -   `grooming_game.py`: The mini-game for grooming and maintaining your pet's hygiene.
    -   `healing_game.py`: The mini-game for healing your pet when it's sick.
    -   `social_game.py`: The mini-game for social interactions with other pets.
    -   `training_game.py`: The mini-game for training your pet and improving its skills.

-   **`systems/`**: This package contains other major game systems.
    -   `housing.py`: Manages the pet's housing, rooms, and furniture.
    -   `marketplace.py`: Implements the in-game economy and shop.
