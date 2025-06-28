# Terminal Zoo Tycoon

A deep and engaging terminal-based zoo management simulation. Build your dream zoo, manage finances, care for animals, and navigate a world of dynamic events, challenges, and mysteries.

---

## Features

- **Zoo Simulation**: Manage everything from animal welfare and staff duties to visitor happiness and zoo finances.
- **Reputation System**: Your zoo's reputation (0-100) is a core mechanic, influenced by animal care, visitor satisfaction, and special events. A high reputation attracts more visitors and unlocks opportunities.
- **Multiple Game Modes**: 
  - **Sandbox Mode**: The classic experience. Build your zoo from the ground up with full freedom.
  - **Challenge Mode**: Test your management skills in unique scenarios like the "Rescue Zoo," where you must turn a failing park around.
- **Engaging Quests & Events**:
  - **The Mysterious Fossil**: Unearth a strange fossil and embark on a multi-stage quest involving research and construction to unlock a prehistoric secret.
  - **VIP Visitors**: Host special guests with unique objectives. Fulfill their requests for big rewards!
  - **Animal Escapes**: Keep your habitats secure! Escaped animals damage your reputation and can be costly to recover.
  - **Random Events**: Over a dozen random events keep gameplay unpredictable, from surprise births to PR scandals.
- **Deep Management Systems**: 
  - **Animals & Habitats**: Care for a variety of animals, each with unique needs. Build and maintain their habitats.
  - **Staffing**: Hire, train, and manage Zookeepers and Veterinarians.
  - **Research**: Unlock new animals, habitat improvements, and staff efficiencies.
- **Persistent Saves**: Save your progress and load your zoo at any time in Sandbox Mode.
- **Colorful UI**: A clean, color-coded terminal interface for an intuitive experience.

---

## How to Play

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Run the Game**:
   ```bash
   python main.py
   ```
3. **Select a Game Mode**:
   - **New Game**: Start a new zoo in Sandbox Mode.
   - **Load Game**: Continue a saved Sandbox game.
   - **Challenge Mode**: Select a pre-defined challenge scenario.

---

## New Gameplay Mechanics

### Reputation
Your reputation is the measure of your zoo's success. It is affected by:
- **Positive**: High animal happiness, clean habitats, high visitor satisfaction, new animal births.
- **Negative**: Low animal happiness, dirty habitats, animal deaths, and animal escapes.

### The Mysterious Fossil Quest
This quest begins randomly. Once you find the fossil, you must:
1.  **Analyze the Fossil**: A research project that takes several in-game days.
2.  **Build the Paddock**: Construct a special "Prehistoric Paddock."
3.  **Unlock the Dinosaur**: Complete the quest to welcome a dinosaur to your zoo!

### VIP Visitors
Occasionally, a VIP will visit with a specific goal (e.g., "see a Lion with 90+ happiness"). Success brings large cash and reputation bonuses, while failure leads to a small reputation penalty.

---

## Requirements

- Python 3.7+
- `colorama`

---
