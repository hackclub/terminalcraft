"""
Menu system and user interface for the atom visualizer.
Handles user input and navigation.
"""

import sys
from colors import Colors, clear_screen
from elements import get_element, ELEMENTS

class AtomMenu:
    """Handles the menu system and user interaction"""
    
    def __init__(self):
        self.running = True
    
    def display_banner(self):
        """Display the application banner"""
        print(f"""
{Colors.BOLD}{Colors.HEADER}
    ⚛️  TERMINAL ATOM VISUALIZER  ⚛️
{Colors.RESET}
{Colors.INFO}Explore the beautiful structure of atoms in your terminal!{Colors.RESET}
{Colors.DIM}═══════════════════════════════════════════════════════{Colors.RESET}
        """)
    
    def display_popular_elements(self):
        """Show a comprehensive list of popular elements"""
        print(f"{Colors.BOLD}{Colors.HIGHLIGHT}Popular Elements:{Colors.RESET}")
        
        # Organize by categories
        categories = {
            "Light Elements": [(1, "Hydrogen"), (2, "Helium"), (3, "Lithium"), (4, "Beryllium")],
            "Life Elements": [(6, "Carbon"), (7, "Nitrogen"), (8, "Oxygen"), (9, "Fluorine")],
            "Noble Gases": [(10, "Neon"), (18, "Argon"), (36, "Krypton"), (54, "Xenon")],
            "Common Metals": [(11, "Sodium"), (12, "Magnesium"), (13, "Aluminum"), (26, "Iron")],
            "Precious Metals": [(29, "Copper"), (47, "Silver"), (78, "Platinum"), (79, "Gold")],
            "Heavy Elements": [(82, "Lead"), (92, "Uranium"), (94, "Plutonium"), (118, "Oganesson")]
        }
        
        for category, elements in categories.items():
            print(f"\n{Colors.SUCCESS}{category}:{Colors.RESET}")
            for i, (num, name) in enumerate(elements):
                print(f"  {Colors.INFO}{num:3d}.{name:<12}{Colors.RESET}", end="")
                if (i + 1) % 2 == 0:
                    print()
            if len(elements) % 2 != 0:
                print()
        print()
    
    def get_atomic_number(self) -> int:
        """Get atomic number from user input"""
        self.display_popular_elements()
        
        while True:
            try:
                print(f"{Colors.BOLD}Enter atomic number (1-118) or 'q' to quit:{Colors.RESET} ", end="")
                user_input = input().strip()
                
                if user_input.lower() in ['q', 'quit', 'exit']:
                    return -1
                
                atomic_number = int(user_input)
                
                if 1 <= atomic_number <= 118:
                    return atomic_number
                else:
                    print(f"{Colors.ERROR}Please enter a number between 1 and 118.{Colors.RESET}")
                    
            except ValueError:
                print(f"{Colors.ERROR}Please enter a valid number.{Colors.RESET}")
            except KeyboardInterrupt:
                print(f"\n{Colors.HIGHLIGHT}Goodbye!{Colors.RESET}")
                return -1
    
    def get_visualization_mode(self) -> int:
        """Get visualization mode from user"""
        print(f"\n{Colors.BOLD}Choose visualization mode:{Colors.RESET}")
        print(f"{Colors.INFO}1. {Colors.HIGHLIGHT}Animated{Colors.INFO} - Watch electrons orbit in real-time{Colors.RESET}")
        print(f"{Colors.INFO}2. {Colors.HIGHLIGHT}Static{Colors.INFO} - Traditional atomic model view{Colors.RESET}")
        
        while True:
            try:
                print(f"{Colors.BOLD}Enter choice (1-2):{Colors.RESET} ", end="")
                choice = input().strip()
                
                if choice in ['1', '2']:
                    return int(choice)
                else:
                    print(f"{Colors.ERROR}Please enter 1 or 2.{Colors.RESET}")
                    
            except KeyboardInterrupt:
                print(f"\n{Colors.HIGHLIGHT}Returning to main menu...{Colors.RESET}")
                return -1
    
    def display_element_info(self, element):
        """Display detailed element information"""
        clear_screen()  # Clear screen before showing element info
        self.display_banner()
        
        print(f"\n{Colors.BOLD}{Colors.SUCCESS}✨ Element Selected:{Colors.RESET}")
        print(f"{Colors.INFO}Name: {Colors.HIGHLIGHT}{element.name}{Colors.RESET}")
        print(f"{Colors.INFO}Symbol: {Colors.HIGHLIGHT}{element.symbol}{Colors.RESET}")
        print(f"{Colors.INFO}Atomic Number: {Colors.HIGHLIGHT}{element.atomic_number}{Colors.RESET}")
        print(f"{Colors.INFO}Atomic Mass: {Colors.HIGHLIGHT}{element.atomic_mass}{Colors.RESET}")
        print(f"{Colors.INFO}Category: {Colors.HIGHLIGHT}{element.category}{Colors.RESET}")
    
    def wait_for_continue(self):
        """Wait for user to continue"""
        print(f"\n{Colors.DIM}Press Enter to continue...{Colors.RESET}", end="")
        try:
            input()
        except KeyboardInterrupt:
            pass
    
    def run_interactive_mode(self, renderer):
        """Run the interactive menu system with proper screen clearing"""
        while self.running:
            clear_screen()
            self.display_banner()
            
            # Get atomic number
            atomic_number = self.get_atomic_number()
            if atomic_number == -1:
                break
            
            # Get element data and display info (clears screen)
            element = get_element(atomic_number)
            self.display_element_info(element)
            
            # Get visualization mode
            mode = self.get_visualization_mode()
            if mode == -1:
                continue  # This will clear screen and return to main menu
            
            # Render the atom
            if mode == 1:
                renderer.draw_animated_atom(element)
                # Animation handles its own screen clearing
            else:
                renderer.draw_static_atom(element)
                self.wait_for_continue()
                # Loop will clear screen when returning to menu
        
        clear_screen()
        print(f"\n{Colors.BOLD}{Colors.SUCCESS}Thank you for exploring the periodic table!{Colors.RESET}")
        print(f"{Colors.INFO}🧪 You discovered the amazing world of {Colors.BRIGHT_CYAN}118 elements{Colors.RESET}{Colors.INFO}! ⚛️{Colors.RESET}\n")
    
    def run_direct_mode(self, renderer, atomic_number: int):
        """Run with direct atomic number (command line argument)"""
        element = get_element(atomic_number)
        
        clear_screen()
        self.display_banner()
        self.display_element_info(element)
        
        mode = self.get_visualization_mode()
        if mode == 1:
            renderer.draw_animated_atom(element)
        elif mode == 2:
            renderer.draw_static_atom(element)
            self.wait_for_continue()
