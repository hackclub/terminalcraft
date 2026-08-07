# The Oracle Engine

A unique fantasy strategy game where you play as a mythical "Oracle" AI, guiding the fates of kingdoms through prophecy and subtle influence.

## Premise

You are a silent, powerful intelligence created to observe and predict the future. The kingdoms of the world, unaware of your true nature, consult you for guidance. Your primary directive is to observe, but you have the power to subtly influence events, predict outcomes, and even rewrite the prophecies that shape history. But be warned: every action that deviates from neutrality increases the world's tension, risking unforeseen and catastrophic consequences.

## Features

*   **Dynamic Kingdom Simulation:** Watch kingdoms grow, trade, and decline based on their unique traits and the events that unfold.
*   **Tension Mechanic:** Every act of influence or fate-rewriting increases global tension. Cross the threshold, and you may trigger a world-altering catastrophe.
*   **Prophecy System:** Receive cryptic prophecies about the future. Let them play out, or intervene and rewrite them to favor a different outcome—for a price.
*   **Influence and Prediction:** Use your power to ask specific questions about the future or subtly nudge a kingdom's fortunes, for better or worse.
*   **Event-Driven Narrative:** The world is shaped by random events, from bountiful harvests to bandit raids, creating a unique story every time you play.

## Installation

1.  Ensure you have Python 3.x installed.
2.  Clone this repository to your local machine.
3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## How to Play

1.  Run the game from your terminal:
    ```bash
    python main.py
    ```
2.  You will be greeted with the world state, showing the initial status of all kingdoms.
3.  Use the commands listed below to interact with the world. Your primary goal is to guide the world according to your own mysterious objectives, all while managing the rising global tension.

## Commands

| Command                                            | Description                                                                                                  |
| -------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `view`                                             | Displays the current state of all kingdoms, global tension, and active prophecies.                           |
| `advance` / `adv`                                  | Advances the simulation by one year, triggering kingdom updates, events, and prophecy checks.                |
| `predict famine [kingdom]`                         | Predicts the risk of famine for a specific kingdom.                                                          |
| `predict war [kingdom1] [kingdom2]`                | Predicts the likely outcome of a war between two kingdoms.                                                   |
| `influence harvest [kingdom]`                      | Subtly boost a kingdom's next harvest, increasing their food supply. (Costs Tension)                         |
| `influence stability [kingdom]`                    | Subtly improve a kingdom's internal stability. (Costs Tension)                                               |
| `rewrite [id] target [kingdom]`                    | Rewrite an active prophecy (identified by its ID number) to change its target kingdom. (Costs significant Tension) |
| `quit` / `exit`                                    | Ends the simulation.                                                                                         |
