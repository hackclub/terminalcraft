# MorseyType-cli - Morse Code Typing Trainer

NOTE: it's a little bit less advanced, but fully x11-less version of my previous project, that you can find [here](https://github.com/piter231/morseytype/), where you only use space to write . and -, instead of D and K.

MorseyType is a terminal-based Morse code typing trainer designed to help you improve your Morse code proficiency through structured practice sessions. The application presents words from common language vocabulary lists, challenges you to type them in Morse code, and provides real-time performance feedback.

## Features

- 🎯 Word-based Morse code training with customizable word lists
- ⏱ Real-time performance tracking with WPM (Words Per Minute) calculation
- 🌍 Support for multiple languages via included word lists
- 📊 Dynamic Morse code reference table for quick lookup
- 📈 Real-time feedback on your Morse input and decoding

## Run
IMPORTANT: you need at least 30-lines height terminal, otherwise some strange graphic glitches may occur

in order to run it, just run (made for aarch64 architecture, works perfectly on rpi zero)
```bash
chmod +x morseytype-cli
./morseytype-cli
```
in the directory with the thousand-most-common-words folder and its content.

## Dependencies
just run by cargo, all dependencies should be installed by default

## Installation

1. Clone the repository with submodules:
```bash
git clone --recurse-submodules https://github.com/piter231/morseytype-cli.git
cd morseytype-cli
```

2. Build the application:
```bash
cargo build --release
```

## Usage

### Basic Command
```bash
cargo run -- [LANGUAGE_CODE] [WORD_COUNT]
```

### Examples
```bash
# English (default), 10 words
cargo run

# Polish, 5 words
cargo run -- pl 5

# German, 15 words
cargo run -- de 15
```

### Parameters
| Parameter      | Default | Description |
|----------------|---------|-------------|
| LANGUAGE_CODE  | `en`    | Language code (e.g., en, pl, de) |
| WORD_COUNT     | `10`    | Number of words to practice |

### Key Bindings
| Key          | Function |
|--------------|----------|
| `D`          | dot (.) |
| `K`          | dash (-) |
| `F`          | Insert letter separator (/) |
| `J`          | Insert word separator (space) |
| `;`          | Backspace (remove last character) |
| `Q` or `Esc` | Exit program |

## Supported Languages

MorseyType supports all languages available in the [thousand-most-common-words](https://github.com/SMenigat/thousand-most-common-words) repository. The application will automatically detect and use the appropriate word list based on the language code you provide.

| Language      | Code | Language      | Code |
|---------------|------|---------------|------|
| English       | `en` | French        | `fr` |
| Polish        | `pl` | German        | `de` |
| Spanish       | `es` | Italian       | `it` |
| Russian       | `ru` | Japanese      | `jp` |
| Chinese       | `zh` | ...and [more](https://github.com/SMenigat/thousand-most-common-words/tree/master/words) | |

## Word List Credits

Special thanks to [SMenigat](https://github.com/SMenigat) for creating and maintaining the [thousand-most-common-words](https://github.com/SMenigat/thousand-most-common-words) repository, which provides the word lists used in this application. These lists are included as a submodule in this project.

## Technical Notes

1. **Font Requirements**: The application currently only supports Latin-based character sets. Non-Latin languages may not display correctly in the terminal.

2. **Performance**: The real-time WPM calculation is based on completed words. The final average WPM is calculated based on the total time taken to complete all words.

## Development Journey

Simplified version of main project, that I mentioned at the beginning. Sadly, you can't precisely measure the duration of button being pressed being in fully cli mode, but its still pretty fun project.

OLD PART:

The main inspiration to make this project was watching the experienced morse operator on the video, and how quickly he does his job.
Developing MorseyType was a challenging but rewarding experience. One of the most difficult aspects was implementing the precise timing mechanism for distinguishing between dots and dashes. After several iterations of trial and error with different timing approaches, I finally succeeded in creating a reliable system that:

1. Accurately measures key press duration
2. Provides consistent feedback
3. Handles system interrupts gracefully
4. Maintains performance across different platforms

The result is a responsive typing experience that faithfully translates your key presses into Morse code characters.

## Contribution

Contributions are welcome! If you'd like to improve MorseyType, please follow these steps:

1. Fork the repository
2. Create a new branch for your feature (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

