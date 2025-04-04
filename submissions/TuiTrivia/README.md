# TuiTrivia

TuiTrivia is a trivia game for the terminal, allowing users to play trivia games, manage scores, and interact with a leaderboard. This project was made as part of a YSWS event by HackClub called TerminalCraft, the API and Database used in leaderboard management where created as part of this project and used knowledge I aquired from the RaspAPI YSWS event.

## Features

- Single-player and multiplayer modes
- Custom trivia questions
- Leaderboard management
- User authentication and registration
- API integration for leaderboard

## Requirements

- Python 3.10 or higher
- `requests`
- `pwinput`
- `termcolor`

## Setup Instructions

1. Clone the repository:
    ```sh
    git clone https://github.com/yousseftechdev/TuiTrivia
    cd TuiTrivia
    ```

2. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Run the trivia game:
    ```sh
    python main.py
    ```

## Command Usage

### Main Commands

- `exit`: Exit the game
- `help`: Show help message
- `clear`: Clear the screen
- `scores <local|global>`: Show high scores
- `clearscore <username>`: Clear your score
- `clearall`: Clear all scores
- `cleardb`: Clear the leaderboard database (ADMIN ONLY)
- `editdb <old_username> <new_username> <new_score> <new_date>`: Edit a user entry in the leaderboard database (ADMIN ONLY)
- `trivia`: Get a random trivia question
- `custom`: Get a random custom trivia question
- `addcustom`: Add a custom trivia question
- `multiplayer`: Start a multiplayer game
- `debug`: Show debug information
- `debug color <color>`: Test colored output
- `debug colors`: Show available colors
- `devmode`: Enable/Disable developer mode
- `difficulty <level>`: Set difficulty level (easy, medium, hard)
- `category <name>`: Set question category
- `debug api <url>`: Set API URL

### API and Database

- Flask: Used for the API
- Supabase: Used for storing leaderboard in a postgresql database
- Leapcell: Hosting the API and Database

## License

This project is licensed under the MIT License.

## Acknowledgements

- Open Trivia Database (https://opentdb.com/)
- Flask (https://flask.palletsprojects.com/)
- Supabase (https://supabase.com/)
- Leapcell (https://leapcell.io/)