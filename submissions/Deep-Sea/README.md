# Deep-Sea Submarine Exploration Simulator

A complex and immersive deep-sea submarine exploration simulator with RPG and survival-horror elements. Inspired by games like *Barotrauma* and *Subnautica*.

## Features

- **Dynamic World**: Explore a procedurally generated abyss with unique zones, points of interest, and environmental hazards like currents and hydrothermal vents.
- **Narrative Quests**: Unravel the mysteries of the deep through multi-stage quests, faction side-missions, and a lore databank.
- **Advanced Crew Management**: Manage your crew's skills, morale, sanity, and relationships. Watch as their bonds and conflicts evolve based on your decisions.
- **Deep Submarine Systems**: Control a complex power grid, manage component-level damage, and install modular upgrades.
- **Crafting & Research**: Salvage materials from the abyss to craft essential components and conduct long-term research projects to unlock powerful new technologies.
- **Stealth & Combat**: Engage in tactical combat with terrifying monsters or use silent running to slip by undetected.
- **Trading & Factions**: Dock at outposts, trade resources, and build your reputation with the factions that inhabit the deep.
- **Psychological Horror**: The abyss is a terrifying place. Protect your crew from panic, hallucinations, and the crushing weight of the darkness.
- **Text-Based UI**: A fully interactive, terminal-based user interface powered by Textual.

## Installation

1.  **Clone the repository:**
    
2.  **Install dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

## How to Run

To start the game, run the following command in your terminal:

```sh
py tui.py
```

## How to Play

Welcome, Captain! Your mission is to explore the abyss, uncover its secrets, and keep your crew alive. Here’s a step-by-step guide to get you started:

### Step 1: Powering Up and Getting Moving

1.  **Check Your Systems:** Start by using the `system` command to see the status of your submarine's systems.
2.  **Activate Systems:** Your **Reactor** and **Life Support** start active. To begin your descent, you'll need to activate the **Engine**. Use the command: `system on engine`.
3.  **Monitor Power:** Keep an eye on your power grid. The `status` command will show you your power generation and consumption. If you consume more power than you generate, systems will start to shut down!

### Step 2: Managing Your Crew

Your crew is your most valuable asset. Keep them happy, sane, and productive.

1.  **Assign Tasks:** Use the `assign` command to give your crew orders.
    *   `assign Jonas repair`: Assign your Engineer, Jonas, to repair damaged systems.
    *   `assign "Dr. Aris" research`: Assign your Scientist, Dr. Aris, to a research station to generate research points.
    *   `assign Echo pilot`: Assign your Pilot, Echo, to the helm to improve navigation and evasion.
2.  **Monitor Crew Status:** Use the `status` command to check on your crew's morale, sanity, and fatigue. Low morale and sanity can lead to negative consequences.

### Step 3: Exploring the Deep

The abyss is a dangerous place. Be prepared for anything.

1.  **Go Deeper:** The submarine will automatically descend each turn.
2.  **Use Your Sonar:** Activate your sonar to find points of interest, resources, and potential threats. Use `system on sonar`. Be warned: the sonar generates noise and can attract unwanted attention.
3.  **Navigate with the Map:** Use the `map` command to see your location and any discovered points of interest.
4.  **Silent Running:** If you detect a threat, use the `silent` command to engage silent running. This reduces your noise signature but also reduces the effectiveness of some systems.

### Step 4: Dealing with Hazards and Encounters

The deep is not empty. You will encounter environmental hazards, strange creatures, and other factions.

1.  **Hazards:** You'll face hazards like high pressure, strong currents, and magnetic anomalies. These can damage your submarine and affect your crew. Keep an eye on your hull integrity and repair systems as needed.
2.  **Combat:** When you encounter a hostile creature, you can `fight`. The outcome of the fight depends on your crew's skills and your submarine's upgrades.
3.  **Trading:** You may encounter friendly outposts. Use the `trade` command to buy and sell resources.

## Leveling Up Your Crew

Your crew members will gain experience and level up as they perform tasks and overcome challenges.

1.  **Gaining Experience:** Crew members gain experience by:
    *   Successfully repairing systems.
    *   Conducting research.
    *   Piloting the submarine.
    *   Winning fights.
    *   Completing mission objectives.
2.  **Leveling Up:** When a crew member gains enough experience, they will level up. This will grant them a **skill point**.
3.  **Spending Skill Points:**
    *   Use the `skill [crew_name] view` command to see a crew member's skill tree.
    *   Use the `skill [crew_name] learn [skill_name]` command to spend a skill point and learn a new skill. Skills provide powerful bonuses and new abilities.

## Command Reference

### Core Commands
- `help`: Displays the list of available commands.
- `quit`: Exits the game.
- `status`: Shows a full report of the submarine's status, crew, and environment.
- `inventory`: Displays all scientific samples and raw materials in your cargo hold.

### Submarine Management
- `system [on/off/toggle] [system_name]`: Change the power state of a submarine system (e.g., `system on sonar`).
- `repair [system_name]`: Begin an interactive mini-game to repair a damaged system.
- `silent`: Toggle silent running mode to reduce noise and avoid detection.

### Crew Management
- `assign [crew_name] [task]`: Assign a crew member to a specific task (e.g., `assign Jonas repair`, `assign "Dr. Aris" research`).
- `skill [crew_name] [view/learn] [skill_name]`: View a crew member's skill tree or spend skill points to learn a new skill.
- `relationships`: View the current relationship statuses between all crew members.

### Exploration & Navigation
- `map`: Displays the procedural map of the current oceanic zone and known points of interest.
- `journal`: Shows your active quests and their current objectives.
- `lore [entry_number]`: Read an unlocked entry from your lore databank. If no number is provided, it lists all unlocked entries.

### Crafting & Research
- `craft [item_name] [quantity]`: Craft an item from raw materials. If no arguments are given, it lists all available crafting blueprints.
- `research [project_name]`: Start a new research project. If no project is specified, it lists all available and ongoing projects.
- `upgrades`: View all available and applied submarine upgrades.
- `upgrade [upgrade_name]`: Apply an unlocked upgrade, consuming the required samples.

### Interaction
- `fight`: Command the crew to attack a hostile creature during an encounter.
- `trade [buy/sell] [item] [quantity]`: Trade with a friendly outpost.
