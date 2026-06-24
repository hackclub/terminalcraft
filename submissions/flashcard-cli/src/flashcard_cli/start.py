from flashcard_cli.data import load_flashcards

def draw_card(text, title="CARD"):
    lines = text.splitlines() or [""]
    width = max(len(line) for line in lines + [title]) + 4
    top = f"┌{'─' * (width - 2)}┐"
    title_line = f"│ {title.center(width - 4)} │"
    sep = f"├{'─' * (width - 2)}┤"
    content = "\n".join(f"│ {line.ljust(width - 4)} │" for line in lines)
    bottom = f"└{'─' * (width - 2)}┘"
    return f"{top}\n{title_line}\n{sep}\n{content}\n{bottom}"

def start_flashcards():
    flashcards = load_flashcards()
    if not flashcards:
        print("No flashcards found.")
        return

    correct = 0
    total = len(flashcards)
    for idx, card in enumerate(flashcards, 1):
        print(f"\nCard {idx}/{total}")
        print(draw_card(card['question'], title="QUESTION"))
        input("Press Enter to flip the card...")
        print(draw_card(card['answer'], title="ANSWER"))
        got_right = input("Did you get it right? (y/n): ").strip().lower()
        if got_right == "y":
            correct += 1
    print(f"\nSession complete! You got {correct}/{total} correct ({(correct/total)*100:.1f}%).")

if __name__ == "__main__":
    start_flashcards()
