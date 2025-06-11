import json
import os
import random
from datetime import datetime, timedelta
import curses
import curses.textpad
import traceback

class Card:
    def __init__(self, front, back, card_id=None, due_date=None, interval=1, ease_factor=2.5):
        self.card_id = card_id if card_id else self._generate_id()
        self.front = front
        self.back = back
        self.due_date = due_date if due_date else datetime.now()
        self.interval = interval
        self.ease_factor = ease_factor

    def _generate_id(self):
        return random.randint(1000, 9999)

    def __str__(self):
        return f"Front: {self.front}\nBack: {self.back}"

    def to_dict(self):
        return {
            'card_id': self.card_id,
            'front': self.front,
            'back': self.back,
            'due_date': self.due_date.isoformat(),
            'interval': self.interval,
            'ease_factor': self.ease_factor
        }

    @classmethod
    def from_dict(cls, data):
        data['due_date'] = datetime.fromisoformat(data['due_date'])
        return cls(**data)

    def update_spaced_repetition(self, quality):
        """
        Update card's due date based on SM-2 algorithm.
        quality: 0-5 (0: complete blackout, 5: perfect recall)
        """
        if quality < 3:
            self.interval = 1
        else:
            if self.interval == 1:
                self.interval = 6
            else:
                self.interval = round(self.interval * self.ease_factor)
        
        self.ease_factor = self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if self.ease_factor < 1.3:
            self.ease_factor = 1.3

        self.due_date = datetime.now() + timedelta(days=self.interval)


class Deck:
    def __init__(self, name, deck_id=None):
        self.deck_id = deck_id if deck_id else self._generate_id()
        self.name = name
        self.cards = []

    def _generate_id(self):
        return random.randint(100, 999)

    def add_card(self, card):
        self.cards.append(card)

    def remove_card(self, card_id):
        self.cards = [card for card in self.cards if card.card_id != card_id]

    def get_due_cards(self):
        return [card for card in self.cards if card.due_date <= datetime.now()]

    def __str__(self):
        return f"Deck: {self.name} ({len(self.cards)} cards)"

    def to_dict(self):
        return {
            'deck_id': self.deck_id,
            'name': self.name,
            'cards': [card.to_dict() for card in self.cards]
        }

    @classmethod
    def from_dict(cls, data):
        deck = cls(data['name'], data['deck_id'])
        deck.cards = [Card.from_dict(card_data) for card_data in data['cards']]
        return deck

class FlashcardApp:
    def __init__(self, data_file="flashcard_data.json"):
        self.data_file = data_file
        self.decks = self._load_data()

    def _load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                try:
                    data = json.load(f)
                    return [Deck.from_dict(deck_data) for deck_data in data]
                except json.JSONDecodeError:
                    return [] 
        return []

    def _save_data(self):
        with open(self.data_file, 'w') as f:
            json.dump([deck.to_dict() for deck in self.decks], f, indent=4)

    def create_deck(self, stdscr, name):
        stdscr.clear()
        if not name.strip():
            stdscr.addstr(0, 0, "Deck name cannot be empty.")
            stdscr.addstr(2, 0, "Press any key to continue...")
            stdscr.refresh()
            stdscr.getch()
            return None, "Deck creation failed: empty name."

        if self.get_deck(name):
            stdscr.addstr(0, 0, f"Deck '{name}' already exists.")
            stdscr.addstr(2, 0, "Press any key to continue...")
            stdscr.refresh()
            stdscr.getch()
            return None, f"Deck creation failed: '{name}' already exists."

        deck = Deck(name)
        self.decks.append(deck)
        self._save_data()
        stdscr.addstr(0, 0, f"Deck '{name}' created successfully.")
        stdscr.addstr(2, 0, "Press any key to continue...")
        stdscr.refresh()
        stdscr.getch()
        return deck, f"Deck '{name}' created."

    def get_deck(self, deck_id_or_name):
        if isinstance(deck_id_or_name, int):
             for deck in self.decks:
                if deck.deck_id == deck_id_or_name:
                    return deck
        else:
            for deck in self.decks:
                if deck.name == deck_id_or_name:
                    return deck
        return None

    def add_card_to_deck(self, stdscr, deck_id_or_name, front, back):
        stdscr.clear()
        deck = self.get_deck(deck_id_or_name)
        if deck:
            if not front.strip() or not back.strip():
                stdscr.addstr(0, 0, "Card front and back cannot be empty.")
                stdscr.addstr(2, 0, "Press any key to continue...")
                stdscr.refresh()
                stdscr.getch()
                return "Card creation failed: empty front or back."

            card = Card(front, back)
            deck.add_card(card)
            self._save_data()
            stdscr.addstr(0, 0, f"Card added to deck '{deck.name}'.")
        else:
            stdscr.addstr(0, 0, f"Deck '{deck_id_or_name}' not found.")
        
        stdscr.addstr(2, 0, "Press any key to continue...")
        stdscr.refresh()
        stdscr.getch()
        return f"Card added to {deck.name}" if deck else f"Deck {deck_id_or_name} not found"


    def study_deck(self, stdscr, deck_id_or_name, mode="standard"):
        stdscr.clear()
        deck = self.get_deck(deck_id_or_name)
        if not deck:
            stdscr.addstr(0, 0, f"Deck '{deck_id_or_name}' not found.")
            stdscr.addstr(2, 0, "Press any key to continue...")
            stdscr.refresh()
            stdscr.getch()
            return

        if not deck.cards:
            stdscr.addstr(0, 0, f"Deck '{deck.name}' has no cards to study.")
            stdscr.addstr(2, 0, "Press any key to continue...")
            stdscr.refresh()
            stdscr.getch()
            return

        stdscr.addstr(0, 0, f"Studying deck: {deck.name} (Mode: {mode})")
        stdscr.refresh()

        if mode == "standard":
            self._study_standard(stdscr, deck)
        elif mode == "spaced_repetition":
            self._study_spaced_repetition(stdscr, deck)
        elif mode == "quiz":
            self._study_quiz(stdscr, deck)
        else:
            stdscr.addstr(2, 0, "Invalid study mode.")
            stdscr.addstr(4, 0, "Press any key to continue...")
            stdscr.refresh()
            stdscr.getch()

    def _study_standard(self, stdscr, deck):
        cards_to_study = list(deck.cards)
        random.shuffle(cards_to_study)
        for i, card in enumerate(cards_to_study):
            stdscr.clear()
            stdscr.addstr(0, 0, f"Studying Deck: {deck.name} - Card {i+1}/{len(cards_to_study)}")
            stdscr.addstr(2, 0, f"Front: {card.front}")
            stdscr.addstr(4, 0, "Press Enter to reveal back...")
            stdscr.refresh()
            while stdscr.getch() not in [curses.KEY_ENTER, 10, 13]: pass

            stdscr.clear()
            stdscr.addstr(0, 0, f"Studying Deck: {deck.name} - Card {i+1}/{len(cards_to_study)}")
            stdscr.addstr(2, 0, f"Front: {card.front}")
            stdscr.addstr(4, 0, f"Back: {card.back}")
            stdscr.addstr(6, 0, "Press Enter for next card...")
            stdscr.refresh()
            while stdscr.getch() not in [curses.KEY_ENTER, 10, 13]: pass

        stdscr.clear()
        stdscr.addstr(0, 0, "Finished studying this deck.")
        stdscr.addstr(2, 0, "Press any key to return to menu...")
        stdscr.refresh()
        stdscr.getch()

    def _study_spaced_repetition(self, stdscr, deck):
        due_cards = deck.get_due_cards()
        if not due_cards:
            stdscr.clear()
            stdscr.addstr(0, 0, "No cards due for review in this deck right now.")
            stdscr.addstr(2, 0, "Press any key to continue...")
            stdscr.refresh()
            stdscr.getch()
            return

        random.shuffle(due_cards)
        for i, card in enumerate(due_cards):
            stdscr.clear()
            stdscr.addstr(0, 0, f"Spaced Repetition: {deck.name} - Card {i+1}/{len(due_cards)}")
            stdscr.addstr(2, 0, f"Front: {card.front}")
            stdscr.addstr(4, 0, "Press Enter to reveal back...")
            stdscr.refresh()
            while stdscr.getch() not in [curses.KEY_ENTER, 10, 13]: pass

            stdscr.clear()
            stdscr.addstr(0, 0, f"Spaced Repetition: {deck.name} - Card {i+1}/{len(due_cards)}")
            stdscr.addstr(2, 0, f"Front: {card.front}")
            stdscr.addstr(4, 0, f"Back: {card.back}")
            stdscr.addstr(6, 0, "Rate your recall (0-5, 0=worst, 5=best): ")
            stdscr.refresh()
            
            quality = -1
            while True:
                try:
                    curses.echo()
                    rating_char_code = stdscr.getch(6, 42) 
                    curses.noecho()
                    quality_str = chr(rating_char_code)
                    stdscr.addstr(6, 42, quality_str)
                    stdscr.refresh()

                    quality = int(quality_str)
                    if 0 <= quality <= 5:
                        stdscr.addstr(7,0, " " * 60) 
                        break
                    else:
                        stdscr.addstr(7, 0, "Invalid rating (0-5). Try again: ")
                        stdscr.move(6,42) 
                        stdscr.clrtoeol() 
                        stdscr.refresh()
                except ValueError:
                    stdscr.addstr(7, 0, "Invalid input (number 0-5). Try again: ")
                    stdscr.move(6,42)
                    stdscr.clrtoeol()
                    stdscr.refresh()
            
            card.update_spaced_repetition(quality)
            stdscr.addstr(8, 0, f"Card updated. Next review in {card.interval} days. Due: {card.due_date.strftime('%Y-%m-%d')}")
            stdscr.addstr(9, 0, "Press Enter for next card...")
            stdscr.refresh()
            while stdscr.getch() not in [curses.KEY_ENTER, 10, 13]: pass

        self._save_data()
        stdscr.clear()
        stdscr.addstr(0, 0, "Finished spaced repetition session.")
        stdscr.addstr(2, 0, "Press any key to return to menu...")
        stdscr.refresh()
        stdscr.getch()

    def _study_quiz(self, stdscr, deck, num_questions=5):
        stdscr.clear()
        if len(deck.cards) < 2:
            stdscr.addstr(0, 0, "Not enough cards for a quiz (min 2).")
            stdscr.addstr(2, 0, "Press any key...")
            stdscr.refresh()
            stdscr.getch()
            return

        questions_to_ask = min(num_questions, len(deck.cards))
        quiz_cards = random.sample(deck.cards, questions_to_ask)
        score = 0

        for i, card in enumerate(quiz_cards):
            stdscr.clear()
            stdscr.addstr(0, 0, f"Quiz: {deck.name} - Question {i+1}/{questions_to_ask}")
            stdscr.addstr(2, 0, f"Question: {card.front}")

            options = [card.back]
            other_cards_backs = [c.back for c in deck.cards if c.card_id != card.card_id and c.back != card.back]
            random.shuffle(other_cards_backs)
            
            num_choices_needed = 3
            options.extend(other_cards_backs[:num_choices_needed])

            while len(options) < 2 and deck.cards :
                all_backs = [c.back for c in deck.cards]
                if not all_backs: break
                potential_option = random.choice(all_backs)
                if potential_option not in options:
                    options.append(potential_option)
                elif len(options) < 4 :
                    options.append(potential_option) 
                else:
                    break


            random.shuffle(options)
            
            current_y = 4
            for idx, option_text in enumerate(options):
                stdscr.addstr(current_y + idx, 2, f"{chr(65+idx)}. {option_text}")
            
            prompt_y = current_y + len(options) + 1
            stdscr.addstr(prompt_y, 0, "Your answer (A, B, C...): ")
            stdscr.refresh()

            user_choice_letter = ''
            while True:
                curses.echo()
                char_code = stdscr.getch(prompt_y, 28) 
                curses.noecho()
                user_choice_letter = chr(char_code).upper()
                stdscr.addstr(prompt_y, 28, user_choice_letter)
                stdscr.refresh()

                if len(user_choice_letter) == 1 and 'A' <= user_choice_letter < chr(65 + len(options)):
                    user_answer_idx = ord(user_choice_letter) - 65
                    user_answer = options[user_answer_idx]
                    break
                else:
                    stdscr.addstr(prompt_y + 1, 0, "Invalid choice. Try again: ")
                    stdscr.move(prompt_y, 28) 
                    stdscr.clrtoeol() 
                    stdscr.refresh()
            
            result_y = prompt_y + 2
            stdscr.addstr(result_y -1, 0, " " * 60)
            if user_answer == card.back:
                stdscr.addstr(result_y, 0, "Correct!")
                score += 1
            else:
                stdscr.addstr(result_y, 0, f"Incorrect. Correct: {card.back}")
            
            stdscr.addstr(result_y + 2, 0, "Press Enter to continue...")
            stdscr.refresh()
            while stdscr.getch() not in [curses.KEY_ENTER, 10, 13]: pass
        
        stdscr.clear()
        stdscr.addstr(0, 0, f"Quiz finished! Score: {score}/{questions_to_ask}")
        stdscr.addstr(2, 0, "Press any key...")
        stdscr.refresh()
        stdscr.getch()

    def list_decks(self, stdscr, selectable=False):
        max_y, max_x = stdscr.getmaxyx()

        if not self.decks:
            stdscr.clear()
            header_text = "Select a Deck:" if selectable else "Available Decks:"
            stdscr.addstr(0, 0, header_text)
            stdscr.addstr(2, 0, "No decks available.")
            stdscr.addstr(4, 0, "Press any key to continue...")
            stdscr.refresh()
            stdscr.getch()
            return None

        if selectable:
            current_selection = 0
            deck_count = len(self.decks)

            while True:
                stdscr.clear()
                stdscr.addstr(0, 0, "Select a Deck:")

                for i, deck in enumerate(self.decks):
                    if 2 + i >= max_y - 2:
                        stdscr.addstr(max_y - 2, 0, "(More decks exist but are not shown)")
                        break
                    
                    due_count = len(deck.get_due_cards())
                    deck_info = f"{i+1}. {deck.name} ({len(deck.cards)} cards, {due_count} due)"
                    
                    if i == current_selection:
                        stdscr.addstr(i + 2, 0, deck_info, curses.A_REVERSE)
                    else:
                        stdscr.addstr(i + 2, 0, deck_info)
                
                stdscr.addstr(max_y - 1, 0, "UP/DOWN to navigate, ENTER to select, ESC to cancel.")
                stdscr.refresh()

                key = stdscr.getch()

                if key == curses.KEY_UP:
                    current_selection = (current_selection - 1 + deck_count) % deck_count
                elif key == curses.KEY_DOWN:
                    current_selection = (current_selection + 1) % deck_count
                elif key == curses.KEY_ENTER or key == 10 or key == 13:
                    return self.decks[current_selection]
                elif key == 27 or key == ord('q') or key == ord('Q'):
                    return None
        else:
            stdscr.clear()
            stdscr.addstr(0, 0, "Available Decks:")
            
            start_line = 2
            more_decks_message_shown = False
            for i, deck in enumerate(self.decks):
                if start_line + i >= max_y - 2:
                    stdscr.addstr(max_y - 2, 0, "More decks... (not scrollable in this view)")
                    more_decks_message_shown = True
                    break
                due_count = len(deck.get_due_cards())
                deck_info = f"{i+1}. {deck.name} ({len(deck.cards)} cards, {due_count} due)"
                stdscr.addstr(start_line + i, 0, deck_info)
            
            stdscr.addstr(max_y - 1, 0, "Press any key to return...")
            stdscr.refresh()
            stdscr.getch()
            return None

    def view_deck(self, stdscr, deck_id_or_name):
        stdscr.clear()
        deck = self.get_deck(deck_id_or_name)
        max_y, max_x = stdscr.getmaxyx()
        
        if deck:
            stdscr.addstr(0, 0, f"--- Deck: {deck.name} ---")
            if not deck.cards:
                stdscr.addstr(2, 0, "This deck is empty.")
            else:
                current_y = 2
                for i, card in enumerate(deck.cards):
                    if current_y + 3 >= max_y -1:
                        stdscr.addstr(current_y, 0, "More cards... (Press key for next page - not implemented)")
                        stdscr.refresh()
                        stdscr.getch()
                        stdscr.clear()
                        stdscr.addstr(0,0, f"--- Deck: {deck.name} (continued) ---")
                        current_y = 2
                    
                    stdscr.addstr(current_y, 2, f"Card {i+1}:")
                    front_display = (card.front[:max_x-10] + '...') if len(card.front) > max_x-10 else card.front
                    back_display = (card.back[:max_x-10] + '...') if len(card.back) > max_x-10 else card.back
                    
                    stdscr.addstr(current_y + 1, 4, f"Front: {front_display}")
                    stdscr.addstr(current_y + 2, 4, f"Back: {back_display}")
                    stdscr.addstr(current_y + 3, 4, f"Due: {card.due_date.strftime('%Y-%m-%d %H:%M')}")
                    current_y += 4
        else:
            stdscr.addstr(0, 0, f"Deck '{deck_id_or_name}' not found.")

        stdscr.addstr(max_y - 2, 0, "Press any key to return...")
        stdscr.refresh()
        stdscr.getch()
            
    def import_deck_from_csv(self, stdscr, file_path, deck_name):
        stdscr.clear()
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                first_line = f.readline().strip().lower()
                if 'front' not in first_line or 'back' not in first_line:
                    f.seek(0)

                deck = self.get_deck(deck_name)
                created_new_deck = False
                if not deck:
                    deck = Deck(deck_name)
                    self.decks.append(deck)
                    created_new_deck = True
                    stdscr.addstr(0,0, f"Deck '{deck_name}' will be created for import.")
                else:
                    stdscr.addstr(0,0, f"Importing into existing deck '{deck_name}'.")
                stdscr.refresh()

                imported_count = 0
                line_num = 0
                for line_content in f:
                    line_num+=1
                    parts = line_content.strip().split(',', 1)
                    if len(parts) == 2:
                        front, back = parts[0].strip(), parts[1].strip()
                        if front.startswith('"') and front.endswith('"'): front = front[1:-1].replace('""', '"')
                        if back.startswith('"') and back.endswith('"'): back = back[1:-1].replace('""', '"')
                        
                        if front and back:
                            card = Card(front, back)
                            deck.add_card(card)
                            imported_count +=1
                
                if imported_count > 0 or created_new_deck:
                    self._save_data()
                stdscr.addstr(2, 0, f"Imported {imported_count} cards into deck '{deck.name}'.")

        except FileNotFoundError:
            stdscr.addstr(0, 0, f"Error: File not found at '{file_path}'.")
        except Exception as e:
            stdscr.addstr(0, 0, f"An error occurred during import: {e}")
        
        stdscr.addstr(4, 0, "Press any key to continue...")
        stdscr.refresh()
        stdscr.getch()

    def export_deck_to_csv(self, stdscr, deck_id_or_name, file_path):
        stdscr.clear()
        deck = self.get_deck(deck_id_or_name)
        if not deck:
            stdscr.addstr(0, 0, f"Deck '{deck_id_or_name}' not found.")
        else:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("front,back\n")
                    for card in deck.cards:
                        front = card.front.replace('"', '""')
                        back = card.back.replace('"', '""')
                        if ',' in front or '"' in front or '\n' in front: front = f'"{front}"'
                        if ',' in back or '"' in back or '\n' in back: back = f'"{back}"'
                        f.write(f"{front},{back}\n")
                stdscr.addstr(0, 0, f"Deck '{deck.name}' exported to '{file_path}'.")
            except Exception as e:
                stdscr.addstr(0, 0, f"An error occurred during export: {e}")
        
        stdscr.addstr(2, 0, "Press any key to continue...")
        stdscr.refresh()
        stdscr.getch()

    def search_cards(self, stdscr, query):
        stdscr.clear()
        results = []
        query_lower = query.lower()
        for deck in self.decks:
            for card in deck.cards:
                if query_lower in card.front.lower() or query_lower in card.back.lower():
                    results.append({'deck_name': deck.name, 'card': card})
        
        max_y, max_x = stdscr.getmaxyx()
        if not results:
            stdscr.addstr(0, 0, f"No cards found matching '{query}'.")
        else:
            stdscr.addstr(0, 0, f"Search results for '{query}':")
            current_y = 2
            for res_idx, res in enumerate(results):
                if current_y + 4 >= max_y -1: 
                    stdscr.addstr(current_y, 0, "More results... Press key for next page.")
                    stdscr.refresh()
                    stdscr.getch()
                    stdscr.clear()
                    stdscr.addstr(0,0, f"Search results for '{query}' (Page {res_idx // ((max_y-3)//4) +1 }):")
                    current_y = 2

                stdscr.addstr(current_y, 2, f"Deck: {res['deck_name']}")
                front_display = (res['card'].front[:max_x-15] + '...') if len(res['card'].front) > max_x-15 else res['card'].front
                back_display = (res['card'].back[:max_x-15] + '...') if len(res['card'].back) > max_x-15 else res['card'].back
                stdscr.addstr(current_y + 1, 4, f"Front: {front_display}")
                stdscr.addstr(current_y + 2, 4, f"Back: {back_display}")
                stdscr.addstr(current_y + 3, 2, "-" * 10)
                current_y += 4
        
        stdscr.addstr(max_y - 2, 0, "Press any key to return to menu...")
        stdscr.refresh()
        stdscr.getch()
        return results

def get_string_input_curses(stdscr, y, x, prompt_string, max_len=60):
    stdscr.addstr(y, x, prompt_string)
    input_y = y + 1
    max_y_scr, max_x_scr = stdscr.getmaxyx()
    if input_y >= max_y_scr: input_y = max_y_scr -1
    
    stdscr.addstr(input_y, x, " " * min(max_len, max_x_scr - x -1))
    stdscr.refresh()
    
    win_rows, win_cols = 1, min(max_len, max_x_scr - x -1)
    if win_cols <=0 : win_cols = 1
    
    editwin = curses.newwin(win_rows, win_cols, input_y, x)
    box = curses.textpad.Textbox(editwin)
    content = box.edit()
    
    stdscr.addstr(y, x, " " * (len(prompt_string) + 5))
    stdscr.addstr(input_y, x, " " * win_cols)
    stdscr.refresh()
    del editwin

    return content.strip().replace('\n', '')

def display_menu(stdscr, selected_idx, menu_title, menu_items):
    stdscr.clear()
    stdscr.addstr(0, 0, menu_title)
    for i, item_text in enumerate(menu_items):
        if i == selected_idx:
            stdscr.addstr(i + 2, 0, item_text, curses.A_REVERSE)
        else:
            stdscr.addstr(i + 2, 0, item_text)
    stdscr.refresh()

def main_curses_loop(stdscr):
    app = FlashcardApp()
    curses.curs_set(0) 
    curses.noecho()
    current_selection = 0
    
    main_menu_items = [
        "1. Create Deck", "2. Add Card to Deck", "3. Study Deck",
        "4. List Decks", "5. View Deck Details", "6. Import Deck from CSV",
        "7. Export Deck to CSV", "8. Search Cards", "9. Exit"
    ]
    menu_item_count = len(main_menu_items)

    while True:
        display_menu(stdscr, current_selection, "--- TermiCards Menu ---", main_menu_items)
        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_selection = (current_selection - 1 + menu_item_count) % menu_item_count
        elif key == curses.KEY_DOWN:
            current_selection = (current_selection + 1) % menu_item_count
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            choice_idx = current_selection

            if choice_idx == 0:
                stdscr.clear()
                name = get_string_input_curses(stdscr, 0, 0, "Enter deck name: ")
                if name: app.create_deck(stdscr, name)
            elif choice_idx == 1:
                stdscr.clear()
                selected_deck = app.list_decks(stdscr, selectable=True)
                
                if selected_deck:
                    stdscr.clear()
                    stdscr.addstr(0, 0, f"Adding card to deck: '{selected_deck.name}'")
                    front = get_string_input_curses(stdscr, 2, 0, "Enter card front (question/term): ")
                    if front:
                        stdscr.clear()
                        stdscr.addstr(0, 0, f"Deck: '{selected_deck.name}', Front: '{front}'")
                        back = get_string_input_curses(stdscr, 2, 0, "Enter card back (answer/definition): ")
                        if back:
                            app.add_card_to_deck(stdscr, selected_deck.name, front, back)
                        else:
                            stdscr.clear()
                            stdscr.addstr(0,0, "Card creation cancelled (no back provided).")
                            stdscr.addstr(2,0, "Press any key..."); stdscr.refresh(); stdscr.getch()
                    else:
                        stdscr.clear()
                        stdscr.addstr(0,0, "Card creation cancelled (no front provided).")
                        stdscr.addstr(2,0, "Press any key..."); stdscr.refresh(); stdscr.getch()
                else:
                    stdscr.clear()
                    stdscr.addstr(0,0, "No deck selected or operation cancelled.")
                    stdscr.addstr(2,0, "Press any key..."); stdscr.refresh(); stdscr.getch()
            elif choice_idx == 2:
                stdscr.clear()
                selected_deck_study = app.list_decks(stdscr, selectable=True)

                if selected_deck_study:
                    study_menu_items = ["a. Standard Flipping", "b. Spaced Repetition", "c. Quiz Mode"]
                    study_mode_selection = 0
                    while True:
                        display_menu(stdscr, study_mode_selection, f"Study Deck: {selected_deck_study.name}\\nChoose Study Mode:", study_menu_items)
                        sm_key = stdscr.getch()
                        if sm_key == curses.KEY_UP: study_mode_selection = (study_mode_selection - 1 + 3) % 3
                        elif sm_key == curses.KEY_DOWN: study_mode_selection = (study_mode_selection + 1) % 3
                        elif sm_key == curses.KEY_ENTER or sm_key == 10 or sm_key == 13:
                            mode = ""
                            if study_mode_selection == 0: mode = "standard"
                            elif study_mode_selection == 1: mode = "spaced_repetition"
                            elif study_mode_selection == 2: mode = "quiz"
                            app.study_deck(stdscr, selected_deck_study.name, mode)
                            break 
                        elif sm_key == 27 or sm_key == ord('q') or sm_key == ord('Q'):
                            break 
                else:
                    stdscr.clear()
                    stdscr.addstr(0,0, "No deck selected or operation cancelled.")
                    stdscr.addstr(2,0, "Press any key..."); stdscr.refresh(); stdscr.getch()
            elif choice_idx == 3:
                app.list_decks(stdscr, selectable=False)
            elif choice_idx == 4:
                stdscr.clear()
                selected_deck_view = app.list_decks(stdscr, selectable=True)

                if selected_deck_view:
                    app.view_deck(stdscr, selected_deck_view.name)
                else:
                    stdscr.clear()
                    stdscr.addstr(0,0, "No deck selected or operation cancelled.")
                    stdscr.addstr(2,0, "Press any key..."); stdscr.refresh(); stdscr.getch()
            elif choice_idx == 5:
                stdscr.clear()
                file_path = get_string_input_curses(stdscr, 0, 0, "Enter CSV file path to import from: ")
                if file_path:
                    stdscr.clear()
                    deck_name_import = get_string_input_curses(stdscr, 0, 0, "Enter name for the new or existing deck: ")
                    if deck_name_import: 
                        app.import_deck_from_csv(stdscr, file_path, deck_name_import)
                    else:
                        stdscr.clear()
                        stdscr.addstr(0,0, "Import cancelled (no deck name provided).")
                        stdscr.addstr(2,0, "Press any key..."); stdscr.refresh(); stdscr.getch()
                else:
                    stdscr.clear()
                    stdscr.addstr(0,0, "Import cancelled (no file path provided).")
                    stdscr.addstr(2,0, "Press any key..."); stdscr.refresh(); stdscr.getch()
            elif choice_idx == 6:
                stdscr.clear()
                selected_deck_export = app.list_decks(stdscr, selectable=True)

                if selected_deck_export:
                    stdscr.clear()
                    stdscr.addstr(0,0, f"Exporting deck: {selected_deck_export.name}")
                    file_path_export_prompt = "Enter CSV file path for export (e.g., export.csv): "
                    file_path_export = get_string_input_curses(stdscr, 2, 0, file_path_export_prompt)
                    
                    if file_path_export:
                        if not file_path_export.lower().endswith(".csv"):
                            file_path_export += ".csv"
                        
                        app.export_deck_to_csv(stdscr, selected_deck_export.name, file_path_export)
                    else:
                        stdscr.clear()
                        stdscr.addstr(0,0, "Export cancelled: No file path entered.")
                        stdscr.addstr(2,0, "Press any key to continue..."); stdscr.refresh(); stdscr.getch()
                else:
                    stdscr.clear()
                    stdscr.addstr(0,0, "No deck selected or operation cancelled.")
                    stdscr.addstr(2,0, "Press any key..."); stdscr.refresh(); stdscr.getch()
            elif choice_idx == 7:
                stdscr.clear()
                query = get_string_input_curses(stdscr, 0, 0, "Enter search term for cards: ")
                if query: app.search_cards(stdscr, query)
            elif choice_idx == 8:
                stdscr.clear()
                stdscr.addstr(0,0, "Exiting Flashcard App. Your data is saved.")
                stdscr.refresh()
                stdscr.getch()
                break 
            

        elif key == ord('q') or key == ord('Q') or key == 27:
            stdscr.clear()
            stdscr.addstr(0,0, "Exiting Flashcard App. Your data is saved.")
            stdscr.refresh()
            stdscr.getch()
            break

if __name__ == "__main__":
    try:
        curses.wrapper(main_curses_loop)
    except curses.error as e:
        print(f"Curses error: {e}")
        print("If you are on Windows, you might need to install 'windows-curses'.")
        print("Try: pip install windows-curses")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()