# Veritaminal

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A terminal-based document verification game where players act as border control agents, verifying AI-generated documents to approve or deny travelers. Test your judgment, attention to detail, and critical thinking as you navigate through an immersive narrative experience.

## 🎮 Game Overview

In Veritaminal, you play as a border control agent stationed at various checkpoints around a fictional world. Your job is to review travel documents and decide whether to approve or deny entry based on the current rules and regulations.

### Key Features:

- **Immersive Narrative**: Experience a compelling story that evolves based on your decisions
- **AI-Powered Content**: Uses Google Gemini API to generate unique documents and storylines
- **Progressive Difficulty**: Face increasingly complex decisions as the game progresses
- **Multiple Border Settings**: Work at different border checkpoints, each with unique challenges
- **Save System**: Save your progress and continue your career later
- **Career Tracking**: See how your decisions impact your career stats over time

## 📋 Gameplay

### Core Mechanics:

1. **Document Verification**: Review traveler documents including names, permits, and backstories
2. **Decision Making**: Choose to approve or deny each traveler
3. **Narrative Consequences**: Your decisions affect trust, corruption, and the overall story
4. **Career Progression**: Advance through a 10-day career path at your assigned checkpoint

### Commands:

- `approve` - Approve the current traveler's entry
- `deny` - Deny the current traveler's entry
- `hint` - Request a hint from Veritas (the game's AI assistant)
- `rules` - Display current verification rules
- `save` - Save your current game progress
- `help` - Show help information
- `quit` - Exit the game

## 🔧 Installation

### Prerequisites

- Python 3.7 or higher
- Pip (Python package installer)
- Google Gemini API key (sign up at https://aistudio.google.com/apikey)

### Option 1: Direct Installation from PyPI

```bash
pip install veritaminal
```

Once installed, run the game with:

```bash
veritaminal
```

### Option 2: From Source

1. Clone this repository
   ```bash
   git clone https://github.com/maverickkamal/veritaminal.git
   cd veritaminal
   ```

2. Run the setup script
   ```bash
   # Windows
   python setup_veritaminal.py
   
   # Linux/Mac
   python3 setup_veritaminal.py
   ```

3. Set up your Google Gemini API key when prompted, or manually in a `.env` file:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## 🚀 Running the Game

### Windows
- Double-click on `veritaminal.bat`, or
- Run in command prompt: `veritaminal.bat`

### Linux/Mac
- Run the shell script: `./veritaminal.sh`

### Any Platform with Python
- Run with Python: `python run_game.py` (or `python3 run_game.py`)

### Command Line Arguments

The game supports several command line arguments:

- `--debug`: Enable debug logging
- `--load [SAVE_FILE]`: Load a specific save file
- `--skip-menu`: Skip the main menu and start a new game immediately

Example:
```bash
python run_game.py --debug --load saves/veritaminal_save_20250312_222841.json
```

## 📁 Project Structure

```
veritaminal/
├── __init__.py         # Package initialization
├── run_game.py         # Entry point script
├── setup_veritaminal.py  # Setup script for API keys
├── requirements.txt    # Python dependencies
├── game/               # Core game modules
│   ├── __init__.py     
│   ├── api.py          # API interactions for content generation
│   ├── gameplay.py     # Core gameplay mechanics
│   ├── main.py         # Main game loop
│   ├── main_menu.py    # Menu system
│   ├── memory.py       # Game state persistence
│   ├── narrative.py    # Story management
│   ├── settings.py     # Game settings and configuration
│   └── ui.py           # Terminal user interface
├── saves/              # Directory for saved games
└── utils/              # Utility scripts
```

## ⚙️ Game Mechanics Explained

### Document Verification

Each document contains:
- **Name**: The traveler's full name
- **Permit**: An identification code that must follow specific formats
- **Backstory**: The traveler's reason for crossing the border
- **Additional Fields**: May include seals, issuance dates, or other information depending on the border setting

### Rules System

Rules evolve as you progress through the game:
- New regulations are introduced on specific days
- Border settings have their own unique requirements
- Trust and corruption metrics affect game outcomes

### Narrative System

The game features a dynamic narrative that responds to:
- Your decision patterns (strict vs. lenient)
- Specific story events triggered by days or decisions
- Trust and corruption metrics

### Game Endings

Multiple endings are possible based on:
- **Trust Score**: How much the government trusts your decision-making
- **Corruption Level**: How often you've bent the rules
- **Days Completed**: Whether you completed your 10-day assignment

## 🛠️ Development

To install in development mode:

```bash
pip install -e .
```

This allows you to make changes to the code and have them immediately take effect when running `veritaminal`.

### Adding New Border Settings

Border settings are managed in `game/settings.py` and consist of:
- Name and description
- Document requirements
- Common issues
- Special rules

### Requirements

The following Python packages are used:
- prompt_toolkit: For interactive terminal UI
- colorama: For cross-platform terminal colors
- requests: For API calls
- python-dotenv: For managing API keys

## ❓ Troubleshooting

### Common Issues

1. **API Key Issues**:
   - Ensure your Gemini API key is correctly set in the `.env` file
   - Check that the key has proper permissions

2. **Display Problems**:
   - The game uses colorama for cross-platform terminal colors
   - If you see incorrect characters, ensure your terminal supports UTF-8

3. **Save File Issues**:
   - Save files are stored in the `saves/` directory as JSON files
   - If loading fails, check file permissions

### Debug Mode

Run with `--debug` to enable detailed logging:
```bash
python run_game.py --debug
```

The log file `veritaminal.log` will contain detailed information about game operations.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- This game was inspired by "Papers, Please" by Lucas Pope
- Uses the Google Gemini API for document and narrative generation
