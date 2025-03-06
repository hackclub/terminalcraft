import socket
import threading
from colorama import Fore, Style, init

init(autoreset=True)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = "localhost"
    return ip

HOST = get_local_ip()  # Auto-detect local IP
PORT = 5555
clients = {}

USERNAME_COLORS = [Fore.BLUE, Fore.GREEN, Fore.YELLOW, Fore.MAGENTA, Fore.CYAN, Fore.LIGHTRED_EX]
user_color_map = {}

def get_username_color(username):
    if username not in user_color_map:
        user_color_map[username] = USERNAME_COLORS[len(user_color_map) % len(USERNAME_COLORS)]
    return user_color_map[username]

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

print(Fore.CYAN + Style.BRIGHT + "╔════════════════════════════════════════╗")
print(Fore.CYAN + Style.BRIGHT + "║          ChatNow Server Setup          ║")
print(Fore.CYAN + Style.BRIGHT + "╚════════════════════════════════════════╝")
print("ChatNow server is starting...\n")
print(Fore.GREEN + f"✅ Server is running on {Fore.YELLOW}{HOST}:{PORT}\n")
print("🔊 Waiting for incoming connections...\n")
print("Did you know that you can change the server IP and port in the server.py file?")
print("You can also change the username colors by modifying the USERNAME_COLORS list.\n")
print("Fantasy names are cool, but real names are cooler! 😉\n")

def broadcast(message, sender=None):
    for client in clients.values():
        if client != sender:
            client.send(message)

def handle_client(client, username):
    while True:
        try:
            message = client.recv(1024).decode("utf-8")
            if not message:
                break

            colored_username = get_username_color(username) + f"[{username}]" + Fore.RESET
            print(colored_username + " " + message)

            formatted_message = f"{colored_username} {message}".encode("utf-8")
            broadcast(formatted_message, sender=client)

        except:
            break

    print(Fore.RED + f"❌ {username} has disconnected.")
    del clients[username]
    broadcast(f"🔴 {username} has left the chat.".encode("utf-8"))
    client.close()

def accept_clients():
    while True:
        client, addr = server.accept()
        username = client.recv(1024).decode("utf-8")

        clients[username] = client
        print(get_username_color(username) + f"🟢 {username} connected from {addr[0]}:{addr[1]}" + Fore.RESET)

        broadcast(f"🟢 {username} has joined the chat!".encode("utf-8"))

        threading.Thread(target=handle_client, args=(client, username)).start()

accept_clients()
