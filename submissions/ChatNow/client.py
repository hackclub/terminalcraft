import socket
import threading
import sys
import emoji
from colorama import Fore, Style, init

init(autoreset=True)  # Automatically resets colors after printing

USERNAME_COLORS = [Fore.BLUE, Fore.GREEN, Fore.YELLOW, Fore.MAGENTA, Fore.CYAN, Fore.LIGHTRED_EX]

def get_username_color(username):
    return USERNAME_COLORS[hash(username) % len(USERNAME_COLORS)]

server_ip = input(Fore.CYAN + "🌍 Enter server IP: " + Fore.RESET)
server_port = int(input(Fore.CYAN + "🔌 Enter server port: " + Fore.RESET))
username = input(Fore.CYAN + "👤 Enter your username: " + Fore.RESET)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    client.connect((server_ip, server_port))
    client.send(username.encode("utf-8"))
except:
    print(Fore.RED + "❌ Failed to connect to the server.")
    sys.exit()

print(Fore.GREEN + "✅ Connected to ChatNow! Type your message or use /about or /users.\n")

def receive():
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            if not message:
                break
            print(message)
        except:
            print(Fore.RED + "❌ Connection lost.")
            client.close()
            break

def send():
    while True:
        message = input()

        if message == "/about":
            print(Fore.YELLOW + "ℹ️  ChatNow | Chat with anyone, securely on your local network.")
            print(Fore.YELLOW + "   Created by BennyGaming635 for the Hack Foundation. 😊")
            continue
        elif message == "/users":
            client.send("/users".encode("utf-8"))
            continue

        message = emoji.emojize(message, language="alias")

        formatted_message = f"{get_username_color(username)}[{username}] {Fore.RESET}{message}"
        client.send(formatted_message.encode("utf-8"))

# Start threads
receive_thread = threading.Thread(target=receive)
receive_thread.start()

send_thread = threading.Thread(target=send)
send_thread.start()
