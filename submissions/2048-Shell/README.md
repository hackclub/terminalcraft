# 2048-Shell
A simple implementation of the classic 2048 game, playable directly in your terminal using a Bash shell script.

## Features
- Play 2048 in your terminal with simple keyboard commands.
- No dependencies-just Bash!
- Keeps track of your score.
- New [multiplier](#multipliers) feature.
- 3 Difficulty levels:
  - Easy: 6x6 grid, classic normal game.
  - Hard: 4x4 grid, 20% chance each for a "x2" or "/2".
  - Expert: 4x4 grid, 60% chance for "/2", 20% chance for "x2".
- This version adds the forbidden 1 (you get it by passing 2 through a "/2" multiplier).
- Easy to use and lightweight (literally no dependencies).

## Multipliers
This is a new feature that adds a twist to the classic game. In addition to the standard 2s and 4s, you can now encounter:
- `x2` - Doubles the value of the tile.
- '/2' - Halves the value of the tile.

These multipliers can appear randomly on the board anytime.

- **Hard Difficulty**: Only 1 multiplier per at a time, and it goes away after the current turn.
- **Expert Difficulty**: More than 1 multipliers can be on the board at the same time, and they stay until they are used.

Note: Multipliers don't change their position on the board, they just modify the tile going through them.

## Requirements
- Bash shell (Linux, macOS, or Windows with WSL/Git Bash)

## Installation
- Clone the repository:
   ```sh
   git clone
  ```
- Done, that's it! No additional setup required.

## How to Play
1. Open your terminal.
2. Navigate to the project directory.
3. Run the game with:
   ```sh
   bash game2048.sh
   ```
4. Choose the difficulty level:
   - `1` for Easy
   - `2` for Hard
   - `3` for Expert
5. Use the following commands to play:
   - `W` - Swipe Up
   - `A` - Swipe Down
   - `S` - Swipe Left
   - `D` - Swipe Right
   - `Q` - Quit the game
   - `H` - Show help

## Screenshots
<div align="center">
<img src="https://hc-cdn.hel1.your-objectstorage.com/s/v3/4f2c2e82bd3a6940fd71ea980771829d22cdbb32_image.png" alt="Header">

<b>Header</b>

<img src="https://hc-cdn.hel1.your-objectstorage.com/s/v3/18d2f51f2e0054c71242b1f8d306cae759173671_image.png" alt="Normal Difficulty">

<b>Normal Difficulty</b>

<img src="https://hc-cdn.hel1.your-objectstorage.com/s/v3/246c8bbe962852f46d35e77415ed4271e25ecb47_image.png" alt="/2 multiplier">

<b>/2 Multiplier</b>

<img src="https://hc-cdn.hel1.your-objectstorage.com/s/v3/71b61fe6441aabf98b7e3f8f3c8cf6c51e1a528e_image.png" alt="x2 multiplier">

<b>x2 Multiplier</b>

<img src="https://hc-cdn.hel1.your-objectstorage.com/s/v3/30de0a74411f173cbd7761b2ff96ca6542e0de13_image.png" alt="Expert Difficulty">

<b>Expert Difficulty</b>

<img src="https://hc-cdn.hel1.your-objectstorage.com/s/v3/12a55db45e5658da0fd0a0a21267491eeeae7d59_image.png" alt="The Forbidden 1">

<b>The Forbidden 1</b>
</div>

## License
This project is open source and available under the Apache 2.0 License.
Feel free to modify and distribute it as you wish.