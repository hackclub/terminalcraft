# MorseyType - Morse Code Typing Trainer


MorseyType is a terminal-based Morse code typing trainer designed to help you improve your Morse code proficiency through structured practice sessions. The application presents words from common language vocabulary lists, challenges you to type them in Morse code, and provides real-time performance feedback.

## Features

- 🎯 Word-based Morse code training with customizable word lists
- ⏱ Real-time performance tracking with WPM (Words Per Minute) calculation
- 🌍 Support for multiple languages via included word lists
- 📊 Dynamic Morse code reference table for quick lookup
- ⚙️ Adjustable threshold for dot/dash distinction
- 📈 Real-time feedback on your Morse input and decoding

## Run
in order to run it, just run
```bash
chmod +x speedtester
./speedtester
```
in the directory with the thousand-most-common-words folder and its content.

## Dependencies
its dependency is x11, should be installed by default, otherwise just install libx11 using your os package manager.

## Installation

1. Clone the repository with submodules:
```bash
git clone --recurse-submodules https://github.com/piter231/morseytype.git
cd morseytype
```

2. Build the application:
```bash
cargo build --release
```

## Usage

### Basic Command
```bash
cargo run -- [LANGUAGE_CODE] [WORD_COUNT] [THRESHOLD_MS]
```

### Examples
```bash
# English (default), 10 words, 150ms threshold
cargo run

# Polish, 5 words, 200ms threshold
cargo run -- pl 5 200

# German, 15 words, 100ms threshold
cargo run -- de 15 100
```

### Parameters
| Parameter      | Default | Description |
|----------------|---------|-------------|
| LANGUAGE_CODE  | `en`    | Language code (e.g., en, pl, de) |
| WORD_COUNT     | `10`    | Number of words to practice |
| THRESHOLD_MS   | `150`   | Duration threshold in milliseconds to distinguish dots (.) and dashes (-) |

### Key Bindings
| Key          | Function |
|--------------|----------|
| `Space`      | Press and release quickly for dot (.), hold longer for dash (-) |
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

2. **Input Handling**: The application uses precise timing to distinguish between dots (.) and dashes (-). The default threshold is 150ms, but you can adjust this based on your typing speed and preference.

3. **Performance**: The real-time WPM calculation is based on completed words. The final average WPM is calculated based on the total time taken to complete all words.

## Development Journey

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

