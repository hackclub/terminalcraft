#!/usr/bin/env python3

import argparse
import json
import sys
import requests
import os
import time
import random
from typing import List, Dict, Optional
import readline  

"""COLORS TO USE"""

class Colors:

    RED1 = '\033[38;5;196m'    
    RED2 = '\033[38;5;197m'    
    RED3 = '\033[38;5;203m'   
    RED4 = '\033[38;5;209m'    
    RED5 = '\033[38;5;160m'  
    GRAY = '\033[38;5;245m'
    PINK = '\033[38;5;198m'
    PURPLE = '\033[38;5;129m'
    BLUE = '\033[38;5;39m'
    CYAN = '\033[38;5;51m'
    GREEN = '\033[38;5;46m'
    YELLOW = '\033[38;5;226m'
    ORANGE = '\033[38;5;214m'
    MAGENTA = '\033[38;5;201m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    RESET = '\033[0m'
    BG_RED = '\033[48;5;196m'
    BG_BLUE = '\033[48;5;39m'
    BG_GREEN = '\033[48;5;46m'
    BG_PURPLE = '\033[48;5;129m'
    FIRE = '🔥'
    ROCKET = '🚀'
    SPARKLES = '✨'
    LIGHTNING = '⚡'
    STAR = '⭐'
    HEART = '❤️'
    COOL = '😎'
    MIND_BLOWN = '🤯'
    PARTY = '🎉'
    RAINBOW = '🌈'
    GHOST = '👻'
    ALIEN = '👽'
    ROBOT = '🤖'
    DIAMOND = '💎'
    CROWN = '👑'
    UNICORN = '🦄'



def get_random_color():
    colors = [Colors.RED1, Colors.RED2, Colors.PINK, Colors.PURPLE, Colors.BLUE, 
              Colors.CYAN, Colors.GREEN, Colors.YELLOW, Colors.ORANGE, Colors.MAGENTA]
    return random.choice(colors)

def print_rainbow_text(text):
    colors = [Colors.RED1, Colors.ORANGE, Colors.YELLOW, Colors.GREEN, Colors.CYAN, Colors.BLUE, Colors.PURPLE, Colors.PINK]
    for i, char in enumerate(text):
        color = colors[i % len(colors)]
        print(f"{color}{char}{Colors.RESET}", end='')
    print()

def print_gradient_logo():
    logo = """
██╗  ██╗ █████╗  ██████╗██╗  ██╗ ██████╗██╗     ██╗   ██╗██████╗ 
██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔════╝██║     ██║   ██║██╔══██╗
███████║███████║██║     █████╔╝ ██║     ██║     ██║   ██║██████╔╝
██╔══██║██╔══██║██║     ██╔═██╗ ██║     ██║     ██║   ██║██╔══██╗
██║  ██║██║  ██║╚██████╗██║  ██╗╚██████╗███████╗╚██████╔╝██████╔╝
╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝ ╚═════╝╚══════╝ ╚═════╝ ╚═════╝ 
    """

    lines = logo.strip().split('\n')
    colors = [Colors.RED1, Colors.RED2, Colors.RED3, Colors.RED4, Colors.RED5, Colors.RED1]

    for i, line in enumerate(lines):
        color = colors[i % len(colors)]
        print(f"{color}{Colors.BOLD}{line}{Colors.RESET}")

def print_typing_effect(text, delay=0.02):
    for char in text:
        print(char, end='', flush=True)
        time.sleep(delay)
    print()

def print_epic_banner():
    print_gradient_logo()
    subtitle = f"{Colors.FIRE} AI-Powered Terminal for Epic Teenagers {Colors.FIRE}"
    print(f"\n{Colors.CYAN}{Colors.BOLD}{subtitle}{Colors.RESET}")
    tagline = f"{Colors.RAINBOW} Unlimited AI chat • No limits • Pure teenage energy {Colors.LIGHTNING}"
    print(f"{Colors.MAGENTA}{tagline}{Colors.RESET}")
    separator = "═" * 80
    print(f"{Colors.RED1}{separator}{Colors.RESET}")
    welcome_msgs = [
        f"{Colors.PARTY} Ready to chat with Opherus? Let's gooo! {Colors.ROCKET}",
        f"{Colors.SPARKLES} Time to get creative with AI magic! {Colors.UNICORN}",
        f"{Colors.FIRE} Opherus is waiting - let's make something awesome! {Colors.DIAMOND}",
        f"{Colors.LIGHTNING} HackClub vibes activated! {Colors.COOL} Ready to build? {Colors.CROWN}"
    ]

    print(f"{get_random_color()}{random.choice(welcome_msgs)}{Colors.RESET}\n")

"""COOL AI STUFF"""

class HackClubAI:
    def __init__(self):
        self.base_url = "https://ai.hackclub.com"
        self.session = requests.Session()
        self.conversation_history: List[Dict[str, str]] = []
        self.session.headers.update({
            'User-Agent': 'HackClub-FunCLI/2.0 (Epic Teenage Terminal)'
        })

        self.loading_messages = [
            f"{Colors.SPARKLES} Opherus is thinking hard...",
            f"{Colors.LIGHTNING} Processing your epic request...",
            f"{Colors.FIRE} Cooking up something amazing...",
            f"{Colors.ROCKET} Launching AI magic...",
            f"{Colors.MIND_BLOWN} Brain cells working overtime...",
            f"{Colors.DIAMOND} Crafting the perfect response...",
            f"{Colors.UNICORN} Sprinkling some AI magic...",
            f"{Colors.GHOST} Summoning digital wisdom..."
        ]

    def get_current_model(self) -> str:
        try:
            response = self.session.get(f"{self.base_url}/model", timeout=10)
            response.raise_for_status()
            return response.text.strip()
        except requests.RequestException as e:
            return f"Error getting model: {e}"

    def send_message(self, message: str, include_history: bool = True) -> str:
        messages = []

        if include_history:
            messages = self.conversation_history.copy()

        messages.append({"role": "user", "content": message})

        payload = {"messages": messages}

        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            data = response.json()
            ai_response = data['choices'][0]['message']['content']
            if include_history:
                self.conversation_history.append({"role": "user", "content": message})
                self.conversation_history.append({"role": "assistant", "content": ai_response})

            return ai_response

        except requests.RequestException as e:
            return f"{Colors.RED1}{Colors.FIRE} Network Error:{Colors.RESET} {e} {Colors.GHOST}"
        except (KeyError, IndexError) as e:
            return f"{Colors.RED1}{Colors.MIND_BLOWN} Response Error:{Colors.RESET} {e} {Colors.ALIEN}"

    def clear_history(self):
        self.conversation_history = []
        clear_msgs = [
            f"{Colors.SPARKLES} Memory wiped clean! Fresh start! {Colors.ROCKET}",
            f"{Colors.FIRE} History cleared! Ready for new adventures! {Colors.PARTY}",
            f"{Colors.LIGHTNING} Clean slate activated! {Colors.DIAMOND}",
            f"{Colors.UNICORN} Past conversations vanished into the void! {Colors.GHOST}"
        ]
        print(f"{get_random_color()}{random.choice(clear_msgs)}{Colors.RESET}")

    def show_history(self):
        if not self.conversation_history:
            no_history_msgs = [
                f"{Colors.GHOST} No conversation history yet - start chatting! {Colors.ROCKET}",
                f"{Colors.ALIEN} The void is empty... say something! {Colors.SPARKLES}",
                f"{Colors.UNICORN} History is blank - time to make some magic! {Colors.FIRE}"
            ]
            print(f"{get_random_color()}{random.choice(no_history_msgs)}{Colors.RESET}")
            return

        print(f"\n{Colors.RAINBOW}{Colors.BOLD} Conversation History {Colors.PARTY}{Colors.RESET}")
        print(f"{Colors.RED1}{'═' * 60}{Colors.RESET}")

        for i, msg in enumerate(self.conversation_history):
            if msg["role"] == "user":
                print(f"{Colors.CYAN}{Colors.BOLD}{Colors.COOL} HackCluber:{Colors.RESET} {Colors.BLUE}{msg['content']}{Colors.RESET}")
            else:
                print(f"{Colors.MAGENTA}{Colors.BOLD}{Colors.ROBOT} Opherus:{Colors.RESET} {Colors.GREEN}{msg['content']}{Colors.RESET}")

            if i < len(self.conversation_history) - 1:
                print(f"{Colors.DIM}{Colors.GRAY}   {Colors.LIGHTNING * 3}{Colors.RESET}")

    def show_stats(self):
        total_messages = len(self.conversation_history)
        user_messages = len([m for m in self.conversation_history if m["role"] == "user"])
        ai_messages = len([m for m in self.conversation_history if m["role"] == "assistant"])

        print(f"\n{Colors.DIAMOND}{Colors.BOLD} Epic Session Stats {Colors.CROWN}{Colors.RESET}")
        print(f"{Colors.RED1}{'═' * 40}{Colors.RESET}")
        print(f"{Colors.FIRE} Total Messages: {Colors.YELLOW}{Colors.BOLD}{total_messages}{Colors.RESET}")
        print(f"{Colors.COOL} Your Messages: {Colors.CYAN}{Colors.BOLD}{user_messages}{Colors.RESET}")
        print(f"{Colors.ROBOT} Opherus Responses: {Colors.GREEN}{Colors.BOLD}{ai_messages}{Colors.RESET}")
        print(f"{Colors.SPARKLES} Awesomeness Level: {Colors.PINK}{Colors.BOLD}MAXIMUM!{Colors.RESET} {Colors.UNICORN}")

    def interactive_mode(self):
        print(f"{Colors.ROCKET}{Colors.BOLD} Interactive Chat Mode Activated! {Colors.FIRE}{Colors.RESET}")
        print(f"{Colors.PURPLE}Chat with Opherus and use commands starting with '/' for special powers!{Colors.RESET}\n")

        commands = [
            ("/help", f"{Colors.SPARKLES} Show all epic commands"),
            ("/model", f"{Colors.ROBOT} Show current AI model"),
            ("/clear", f"{Colors.FIRE} Clear conversation history"),
            ("/history", f"{Colors.RAINBOW} Show conversation history"),
            ("/stats", f"{Colors.DIAMOND} Show session statistics"),
            ("/vibes", f"{Colors.UNICORN} Get random motivational vibes"),
            ("/quit", f"{Colors.GHOST} Exit interactive mode")
        ]

        print(f"{Colors.CROWN}{Colors.BOLD}Epic Commands Available:{Colors.RESET}")
        for cmd, desc in commands:
            print(f"  {Colors.YELLOW}{Colors.BOLD}{cmd:<12}{Colors.RESET} {desc}{Colors.RESET}")
        print()

        while True:
            try:
                prompt_emojis = [Colors.COOL, Colors.FIRE, Colors.ROCKET, Colors.LIGHTNING, Colors.STAR, Colors.DIAMOND]
                emoji = random.choice(prompt_emojis)

                user_input = input(f"{Colors.CYAN}{Colors.BOLD}╭─ {emoji} HackCluber{Colors.RESET}\n{Colors.CYAN}{Colors.BOLD}╰─▶{Colors.RESET} ").strip()

                if not user_input:
                    continue
                if user_input.lower() in ['/quit', '/exit', '/q']:
                    goodbye_msgs = [
                        f"\n{Colors.PARTY} Thanks for the epic session! Keep building amazing things! {Colors.ROCKET}",
                        f"\n{Colors.SPARKLES} See you later, legend! Go change the world! {Colors.CROWN}",
                        f"\n{Colors.FIRE} That was awesome! Until next time, HackCluber! {Colors.HEART}",
                        f"\n{Colors.UNICORN} You're absolutely incredible! Keep being amazing! {Colors.RAINBOW}"
                    ]
                    print(f"{get_random_color()}{random.choice(goodbye_msgs)}{Colors.RESET}")
                    break

                elif user_input.lower() == '/help':
                    print(f"\n{Colors.CROWN}{Colors.BOLD}Epic Commands Available:{Colors.RESET}")
                    for cmd, desc in commands:
                        print(f"  {Colors.YELLOW}{Colors.BOLD}{cmd:<12}{Colors.RESET} {desc}{Colors.RESET}")
                    continue

                elif user_input.lower() == '/model':
                    model = self.get_current_model()
                    print(f"\n{Colors.ROBOT}{Colors.BOLD} Current AI Model:{Colors.RESET} {Colors.YELLOW}{Colors.BOLD}{model}{Colors.RESET} {Colors.FIRE}")
                    continue

                elif user_input.lower() == '/clear':
                    self.clear_history()
                    continue

                elif user_input.lower() == '/history':
                    self.show_history()
                    continue

                elif user_input.lower() == '/stats':
                    self.show_stats()
                    continue

                elif user_input.lower() == '/vibes':
                    vibes = [
                        f"{Colors.FIRE} You're absolutely crushing it! Keep going! {Colors.ROCKET}",
                        f"{Colors.SPARKLES} Your creativity is off the charts! {Colors.UNICORN}",
                        f"{Colors.LIGHTNING} You're destined for greatness! {Colors.CROWN}",
                        f"{Colors.DIAMOND} Every line of code makes you stronger! {Colors.COOL}",
                        f"{Colors.RAINBOW} You're building the future, one idea at a time! {Colors.STAR}",
                        f"{Colors.PARTY} Your potential is infinite! {Colors.MIND_BLOWN}",
                        f"{Colors.HEART} The world needs more builders like you! {Colors.FIRE}"
                    ]
                    print(f"\n{get_random_color()}{Colors.BOLD}{random.choice(vibes)}{Colors.RESET}\n")
                    continue
                loading_msg = random.choice(self.loading_messages)
                print(f"\n{Colors.MAGENTA}{Colors.BOLD}╭─ {loading_msg}{Colors.RESET}")
                print(f"{Colors.MAGENTA}{Colors.BOLD}╰─▶{Colors.RESET} ", end="", flush=True)

                response = self.send_message(user_input)
                response_color = get_random_color()
                print(f"{response_color}{response}{Colors.RESET}")
                print()

            except KeyboardInterrupt:
                print(f"\n\n{Colors.SPARKLES} Caught you trying to escape! Thanks for the epic session! {Colors.PARTY}{Colors.RESET}")
                break
            except EOFError:
                print(f"\n\n{Colors.ROCKET} Session ended! You're amazing - keep building! {Colors.HEART}{Colors.RESET}")
                break

def main():
    parser = argparse.ArgumentParser(
        description=f"{Colors.FIRE} HACKCLUB AI - Epic Teenage CLI Tool {Colors.ROCKET}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
{Colors.CROWN}{Colors.BOLD}Epic Examples:{Colors.RESET}
  {Colors.YELLOW}hackclub{Colors.RESET}                           # Start interactive mode {Colors.PARTY}
  {Colors.YELLOW}hackclub "Tell me a joke"{Colors.RESET}         # Send a single message {Colors.COOL}
  {Colors.YELLOW}hackclub --model{Colors.RESET}                  # Show current model {Colors.ROBOT}
  {Colors.YELLOW}hackclub "Explain Python" --no-history{Colors.RESET}  # Send without context {Colors.LIGHTNING}
  {Colors.YELLOW}hackclub --version{Colors.RESET}                # Show version info {Colors.SPARKLES}

{Colors.HEART} Made with epic teenage energy for HackClub legends {Colors.UNICORN}
        """
    )

    parser.add_argument(
        'message', 
        nargs='?', 
        help='Message to send to Opherus'
    )

    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Start interactive chat mode'
    )

    parser.add_argument(
        '--model',
        action='store_true',
        help='Show the current AI model'
    )

    parser.add_argument(
        '--no-history',
        action='store_true',
        help='Send message without conversation context'
    )

    parser.add_argument(
        '--json',
        action='store_true',
        help='Output response in JSON format'
    )

    parser.add_argument(
        '--version',
        action='store_true',
        help='Show version information'
    )

    parser.add_argument(
        '--no-banner',
        action='store_true',
        help='Skip the epic banner (for scripting)'
    )

    args = parser.parse_args()
    if not args.no_banner and not args.json:
        if args.interactive or not args.message:
            print_epic_banner()

    ai = HackClubAI()
    if args.version:
        print(f"{Colors.CROWN}{Colors.BOLD}HACKCLUB AI - Epic Teenage CLI{Colors.RESET}")
        print(f"{Colors.FIRE}Version: 2.0.0 - Maximum Fun Edition{Colors.RESET}")
        print(f"{Colors.ROBOT}API: ai.hackclub.com{Colors.RESET}")
        print(f"{Colors.SPARKLES}Built by teens, for teens with {Colors.HEART}{Colors.RESET}")
        print(f"{Colors.RAINBOW}Awesomeness Level: LEGENDARY! {Colors.UNICORN}{Colors.RESET}")
        return
    if args.model:
        model = ai.get_current_model()
        if args.json:
            print(json.dumps({"model": model}))
        else:
            print(f"{Colors.ROBOT}{Colors.BOLD} Current Model:{Colors.RESET} {Colors.YELLOW}{Colors.BOLD}{model}{Colors.RESET} {Colors.FIRE}")
        return

    if args.interactive or not args.message:
        ai.interactive_mode()
        return
    if args.message:
        include_history = not args.no_history

        if not args.json and not args.no_banner:
            loading_msg = random.choice(ai.loading_messages)
            print(f"{Colors.MAGENTA}{Colors.BOLD}{Colors.ROBOT} {loading_msg}{Colors.RESET} ")

        response = ai.send_message(args.message, include_history)

        if args.json:
            print(json.dumps({"response": response}))
        else:
            response_color = get_random_color()
            print(f"{response_color}{response}{Colors.RESET}")
        return

    ai.interactive_mode()

if __name__ == "__main__":
    main()
