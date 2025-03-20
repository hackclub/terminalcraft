from TwoPlayerGamesCLI.Multiplayer_CLI import main
from TwoPlayerGamesCLI.guess_num import main_game
from TwoPlayerGamesCLI.HangMan import hangman_game
from TwoPlayerGamesCLI.TruthLie import game
from TwoPlayerGamesCLI.WordChain import word_chain_game
from TwoPlayerGamesCLI.Unscramble import scrambled_word_game
from TwoPlayerGamesCLI.ConnectFour import play_game

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
