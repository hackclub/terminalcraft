from 2PlayerGamesCLI.Multiplayer_CLI import main
from 2PlayerGamesCLI.guess_num import main_game
from 2PlayerGamesCLI.HangMan import hangman_game
from 2PlayerGamesCLI.TruthLie import game
from 2PlayerGamesCLI.WordChain import word_chain_game
from 2PlayerGamesCLI.Unscramble import scrambled_word_game
from 2PlayerGamesCLI.ConnectFour import play_game

__all__ = [
    "main",
    "main_game",
    "hangman_game",
    "game",
    "word_chain_game",
    "scrambled_word_game",
    "play_game"
]

# ✅ Only run `main()` if the script is executed directly
if __name__ == "__main__":
    main()
