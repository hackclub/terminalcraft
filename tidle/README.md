# Tidle
> an open-source, small idle game in the terminal.

## Installation
```bash
pip install tilde
```
ps: ensure that your python executables are on your PATH, or it won't work.

## Usage
```bash
tilde
```

## Guide
### How to play
on booting the game, you will be presented with a screen like this:
```
Welcome to tidle!
ticks: 0 | cycles: 0 | processes: 0 | loops: 0 | optimization rate: 1
RPS (Resources Per Second):
ticks: 0 | cycles: 0 | processes: 0 | loops: 0
||> 
```

This is the *Command Line Interface* (CLI) of the game. You can interact with the game by typing commands into the CLI. You will have to type the command and press `Enter` to execute it.

### Commands
- `help`: shows the help menu.
- `generate`: generates a tick.
- `exchange <resource1> <resource2> <amount>`: exchanges the necessary amount of `resource1` to create 'amount' of `resource2`. (ex: `exchange ticks cycles 10` will convert 1000 ticks to 10 cycles)
- `exit`: saves exits the game.
- `save`: saves the game.
- `medals`: lists all achievements and if they are unlocked or not.
- `stats`: shows the stats of the game.
- `clear`: clears the screen.
- `store`: opens the store for buying upgrades.
- `delete`: deletes the save file. ***Permanently.***

### Currencies
- `ticks`: the main currency of the game. Used to purchase most of the upgrades.
- `cycles`: used to create the next currency, `processes`.
- `processes`: used to create the next currency, `loops`.
- `loops`: used to purchase refactorizations.

Each tier of currency can be created by exchanging 100x of the previous currency. 100 ticks = 1 cycle, 100 cycles = 1 process, 100 processes = 1 loop and so on.

### Upgrades
Upgrades can be purchased from the store. They can provide a variety of benefits. As you get more of an upgrade, the cost of the next one increases. The upgrades are as follows:
- `Generator Efficiency`: increases the amount of ticks generated per `generate` command by 1.
- `Auto Generator`: automatically generates 1 extra tick per second.
- `Cycle Booster`: automatically generates 1 extra cycle per second.
- `Process Enhancer`: automatically generates 1 extra process per second.
- `Loop Accelerator`: automatically generates 1 extra loop per second.
- `Refactor`: increases the optimization rate by 1, but ***resets everything***.

### Achievements
Achievements can be unlocked by reaching certain milestones in the game. They do not provide any benefits, but they are fun to collect. You can view all the achievements by typing `medals`. (the word 'Achievements' proved to be too hard to spell when you are tired)

### Refactorizations
Refactorizations are basically the rebirth mechanic. They reset everything, but they increase the optimization rate by 1. This means that you will generate more resources per second. You can purchase refactorizations in the shop.

### Optimization Rate
The optimization rate is a multiplier that increases the amount of resources generated per second and resources per manual generation. It starts at 1 and increases by 1 for each refactorization.
