# 🛰️ The Signal Cartographer: Echoes from the Void

A sci-fi signal analysis game built with Python and Textual TUI. Explore the void of space, detect mysterious signals, and uncover their secrets using the AetherTap terminal interface.

## 🎮 Game Overview

You are a Signal Cartographer exploring space sectors to detect and analyze mysterious signals from unknown sources. Use advanced tools to scan different sectors, focus on interesting signals, and analyze them to reveal hidden information. Progress through increasingly challenging sectors while upgrading your equipment and unlocking achievements.

## ✨ Complete Feature Set

### 🖥️ Interface & User Experience
- **Professional TUI Interface** - Built with Textual for a modern terminal experience
- **6-Panel AetherTap Interface** - Spectrum analyzer, signal focus, cartography, decoder, captain's log, and command input
- **Enhanced Command System** - TAB autocompletion with live preview and multi-word support
- **Real-time Visual Feedback** - Immediate feedback with success/error icons and suggestions
- **Context-Sensitive Help** - Smart help system that adapts to your current progress
- **Modern Visual Indicators** - Progress bars, status icons, and enhanced UI elements
- **Full Hotkey Support** - F1-F5 for panel switching, Ctrl+H for help, Ctrl+C to quit

### 🌌 Exploration & Content
- **5-Tier Difficulty Progression** - ALPHA-1 (Beginner) through EPSILON-5 (Expert)
- **9 Unique Signal Types** - From basic Pulsed-Echo to advanced Singularity-Resonance
- **Advanced Signal Properties** - Frequency, strength, modulation, stability, and signatures
- **Progressive Complexity** - Signals become more challenging and rewarding in higher sectors
- **Dynamic Signal Generation** - Procedurally generated signals with unique characteristics

### 📈 Progression & Achievements
- **Equipment Upgrade System** - 4 tier upgrades: Scanner Sensitivity, Signal Amplifier, Frequency Filter, Deep Space Antenna
- **Analysis Points Currency** - Earned through signal analysis and spent on upgrades
- **10 Achievement System** - From "First Contact" to "Deep Space Pioneer" with progress tracking
- **Performance Statistics** - Track your scans, analyses, discoveries, and efficiency
- **Progression Commands** - UPGRADES, ACHIEVEMENTS, PROGRESS for detailed tracking

### 💾 Save System & Persistence
- **Complete Save/Load System** - JSON-based with metadata and error handling
- **Multiple Save Slots** - Named saves with SAVE filename and LOAD filename commands
- **Auto-save Functionality** - Automatic saves on sector changes and major progress
- **Progress Preservation** - All upgrades, achievements, and discoveries saved
- **Save File Management** - File size tracking, timestamps, and corruption protection

### ⚡ Performance & Optimization
- **Memory Management** - Advanced garbage collection and object tracking
- **Render Caching** - LRU cache for expensive ASCII rendering operations
- **Command Throttling** - Prevents spam and improves responsiveness
- **Performance Monitoring** - PERFORMANCE command to monitor system efficiency
- **Error Handling** - Graceful degradation and fallback functions
- **Data Cleanup** - Automatic cleanup of old/stale data

### 🎯 Enhanced Commands & Tools
- **Core Commands** - SCAN, FOCUS, ANALYZE, STATUS, HELP with enhanced feedback
- **Progression Commands** - UPGRADES, ACHIEVEMENTS, PROGRESS, PERFORMANCE
- **Save Commands** - SAVE, LOAD with flexible filename support
- **System Commands** - CLEAR (logs), QUIT with proper cleanup
- **Analysis Tools** - 6 specialized tools: pattern_recognition, cryptographic, spectral, ascii_manipulation, constellation_mapping, temporal_sequencing
- **Command Aliases** - Short forms like S for SCAN, F for FOCUS, A for ANALYZE

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Windows, macOS, or Linux

### Installation & Running

1. **Clone the repository:**
   ```bash
   git clone https://github.com/maverickkamal/signal-cartographer.git
   cd signal-cartographer
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate virtual environment:**
   - **Windows:** `.venv\Scripts\activate`
   - **macOS/Linux:** `source .venv/bin/activate`

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the game:**
   ```bash
   python main.py
   ```

   Or use the provided scripts:
   - **Windows:** `.\start_game.ps1` or `.\run.bat`
   - **Unix:** `./run.sh`

## 🎯 How to Play

### Getting Started
1. **Launch the game** and enjoy the enhanced startup sequence with progress indicators
2. **Type commands** in the purple-bordered command input box (with TAB completion!)
3. **Type `HELP`** or press **Ctrl+H** for the comprehensive gameplay guide
4. **Start with `SCAN`** to detect signals in the current sector
5. **Use `FOCUS SIG_1`** to lock onto the first detected signal
6. **Run `ANALYZE`** to reveal hidden information and earn Analysis Points

### Essential Commands
- `SCAN` / `S` - Scan current sector for signals
- `SCAN BETA-2` - Scan specific sector (ALPHA-1 through EPSILON-5)
- `FOCUS SIG_1` / `F SIG_1` - Focus on a detected signal
- `ANALYZE` / `A` - Analyze the currently focused signal  
- `ANALYZE spectral` - Use specific analysis tool
- `UPGRADES` - View and purchase equipment upgrades
- `ACHIEVEMENTS` - View achievement progress
- `STATUS` - Show comprehensive system status
- `SAVE` / `SAVE mysave` - Save game progress
- `LOAD` / `LOAD mysave` - Load saved game
- `PERFORMANCE` - View system performance statistics

### Progressive Gameplay
- **ALPHA-1** (🟢 Beginner): 3 basic signals, learn the fundamentals
- **BETA-2** (🟡 Easy): 2 stronger signals, practice analysis skills
- **GAMMA-3** (🟠 Medium): Complex signals with deeper secrets
- **DELTA-4** (🔴 Hard): Bio-Neural and Quantum-Echo signals
- **EPSILON-5** (🟣 Expert): Singularity-Resonance - the ultimate challenge

### Interface Panels (F1-F5)
- **F1 - Spectrum Analyzer** - Shows detected signals as frequency spikes
- **F2 - Signal Focus & Data** - Detailed information about focused signals  
- **F3 - Cartography & Navigation** - Current sector and signal map
- **F4 - Decoder & Analysis Toolkit** - Analysis results and specialized tools
- **F5 - Captain's Log & Database** - Command history, achievements, and system messages

## 🌟 Advanced Features

### Equipment Upgrades
- **Scanner Sensitivity** (+1 signal detection range)
- **Signal Amplifier** (+20% signal strength reading)
- **Frequency Filter** (reduce noise, clearer signals)
- **Deep Space Antenna** (detect distant sectors)

### Achievement System
- **First Contact** - Analyze your first signal
- **Explorer** - Discover all 5 sectors
- **Signal Hunter** - Find 10 different signals
- **Master Analyst** - Complete 50 analyses
- **Deep Space Pioneer** - Reach EPSILON-5
- **Speed Scanner**, **Perfectionist**, **Code Breaker** and more!

### Signal Types by Complexity
1. **Pulsed-Echo** (Beginner) - Basic radar-like signals
2. **Bio-Resonant** (Easy) - Life-sign indicators
3. **Quantum-Drift** (Easy) - Quantum interference patterns
4. **Phase-Locked** (Medium) - Synchronized transmissions
5. **Null-State** (Medium) - Inverted signal patterns
6. **Bio-Neural** (Hard) - Neural collective consciousness patterns
7. **Quantum-Echo** (Hard) - Dimensional interference signatures
8. **Omni-Band** (Very Hard) - Multi-frequency spectrum signals
9. **Singularity-Resonance** (Expert) - Gravitational singularity signals

## 🛠️ Technical Details

### Built With
- **Python 3.8+**
- **Textual** - Modern Python TUI framework
- **Rich** - Terminal text formatting and styling
- **JSON** - Save system and data persistence

### Architecture
- **Modular Design** - Separate UI, game logic, signal systems, and progression
- **Enhanced Command Parser** - Flexible parsing with autocompletion and error handling
- **Performance Optimization** - Memory management, caching, and monitoring
- **Save System** - Robust JSON-based persistence with error recovery
- **Progression System** - Comprehensive tracking of player advancement

## 📁 Project Structure

```
signal-cartographer/
├── src/
│   ├── ui/                    # User interface components
│   │   ├── layout.py         # Main interface layout
│   │   ├── panes.py          # Individual panel widgets
│   │   └── input_handler.py  # Command input with autocompletion
│   ├── utils/                # Utility functions
│   │   └── save_system.py    # Save/load functionality
│   ├── content/              # Game content and data
│   ├── game_controller.py    # Core game logic
│   ├── command_parser.py     # Enhanced command parsing
│   ├── progression_system.py # Upgrades and achievements
│   ├── enhanced_ux.py        # UX improvements and autocompletion
│   ├── performance_optimizations.py # Performance monitoring
│   └── aethertap_textual.py  # Main TUI interface
├── data/                     # Game data files
├── saves/                    # Save game files
├── instruction/              # Documentation
├── main.py                   # Game entry point
├── requirements.txt          # Python dependencies
├── GAME_GUIDE.md            # Comprehensive gameplay guide
└── README.md                # This file
```

## 💡 Pro Tips

### Efficiency & Strategy
- **Use TAB completion** for faster command entry
- **Focus on progression** - analyze signals to earn Analysis Points
- **Upgrade strategically** - Scanner Sensitivity first for more signals
- **Save frequently** with named saves for different playthroughs
- **Monitor performance** with the PERFORMANCE command
- **Explore systematically** - master each sector before advancing

### Advanced Techniques
- **Sector progression** - Complete lower sectors before attempting DELTA-4 or EPSILON-5
- **Achievement hunting** - Use ACHIEVEMENTS command to track progress
- **Equipment synergy** - Combine upgrades for maximum effectiveness
- **Pattern recognition** - Look for relationships between signals in different sectors

## 🐛 Troubleshooting

### Common Issues
- **Can't see signals?** → Run `SCAN` first to detect signals in current sector
- **FOCUS not working?** → Ensure signals exist after scanning; try `SCAN` again
- **ANALYZE gives no results?** → Focus on a signal first using `FOCUS SIG_1`
- **Commands not working?** → Commands are case-insensitive; try TAB completion
- **Performance issues?** → Use `PERFORMANCE CLEANUP` to free memory

### Save System
- **Save failed?** → Check disk space and permissions; saves go to `saves/` directory
- **Load failed?** → Verify filename exists; use `LOAD` without filename to see available saves
- **Corrupted save?** → Delete the corrupted file and use an earlier save or start new game

## 📊 Game Statistics

After completing development and testing:
- **5 Explorable Sectors** with unique characteristics
- **9 Signal Types** across difficulty spectrum  
- **4 Equipment Upgrades** for enhanced capabilities
- **10+ Achievements** to unlock and master
- **6 Analysis Tools** for specialized signal processing
- **Complete Progression System** with meaningful advancement
- **Robust Save System** supporting multiple playthroughs
- **Performance Optimized** for smooth long-term gameplay

## 🤝 Contributing

Contributions are welcome! Areas for contribution:
- Additional signal types or sectors
- New achievements or upgrade paths
- Performance improvements
- Cross-platform testing
- Documentation improvements

Please feel free to submit issues, feature requests, or pull requests.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with the amazing [Textual](https://github.com/Textualize/textual) framework
- Inspired by classic sci-fi and signal analysis themes
- Thanks to the Python community for excellent tooling
- Special thanks to contributors and testers

---

**🚀 Ready to explore the void? Launch the game and start your signal cartography journey!**

*The signals are waiting... what secrets will you discover in the depths of space?*
