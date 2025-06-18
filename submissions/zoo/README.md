# Terminal Zoo Tycoon

A terminal-based zoo management simulation game. Build and manage your own zoo: construct habitats, buy animals, hire staff, conduct research, and handle random events—all from your terminal!

---

## Features

- **Build and Expand**: Construct habitats (Savannah, Arctic, Jungle) and expand your zoo.
- **Animal Management**: Buy, name, and care for animals (Lions, Penguins, Monkeys, Giraffes, and unlockable Tigers & Pandas).
- **Staff System**: Hire and train Zookeepers and Veterinarians, each with skills and fatigue.
- **Visitor Simulation**: Attract different visitor types (Families, Students, Animal Enthusiasts, Regulars) with unique interests and donation behaviors.
- **Research & Development**: Unlock upgrades and new animals through research projects.
- **Random Events**: Handle disease outbreaks, PR scandals, philanthropist visits, surprise births, and more.
- **Financial Management**: Track income, expenses, and net profit with daily financial reports.
- **Save/Load System**: Save your progress and continue your zoo at any time.
- **Colorful Terminal UI**: Enhanced with colorama for a more engaging experience.

---

## Installation

1. **Clone the repository:**
   
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## How to Play

1. **Start the game:**
   ```bash
   python main.py
   ```
2. **Choose an option:**
   - New Game: Start a new zoo and enter its name.
   - Load Game: Continue from your last save (stored in `saves/savegame.json`).
3. **Main Menu Options:**
   - View Detailed Reports: See animal, habitat, staff, and visitor stats.
   - Build Habitat: Construct new habitats for animals.
   - Buy Animal: Purchase and name animals for your zoo.
   - Hire Staff: Recruit zookeepers and veterinarians.
   - Manage Habitats: Upgrade habitat security.
   - Manage Staff: Train staff to improve their skills.
   - Research & Development: Unlock upgrades and new animals.
   - Next Day: Progress to the next day, triggering events and visitor simulation.
   - Save Game: Save your current progress.
   - Exit: Quit the game.

---

## Animals
- **Available from start:** Lion, Penguin, Monkey, Giraffe
- **Unlockable via research:** Tiger, Panda

## Habitats
- Savannah
- Arctic
- Jungle

## Staff Roles
- Zookeeper: Feeds animals, cleans habitats
- Veterinarian: Heals sick/injured animals

## Research Projects
- Advanced Nutrition: Improves animal health/happiness
- Efficient Staff Training: Reduces training cost, increases skill gain
- Exotic Animal Acquisition: Unlocks Tiger and Panda

## Random Events
- Disease outbreak, PR scandal, philanthropist visit, surprise birth, positive press, habitat malfunction, food spoilage, and more.

---

## Saving & Loading
- The game auto-saves to `saves/savegame.json` when you choose "Save Game".
- Load your zoo from the main menu.

---

## Requirements
- Python 3.7+
- colorama==0.4.6

---
