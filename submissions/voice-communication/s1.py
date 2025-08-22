# Server Code 1 testing

import socket
import threading
import signal
import sys
import pyaudio

clients = []

def broadcast(message, sender_socket):
    for client in clients:
        if client != sender_socket:
            try:
                client.sendall(message)
            except Exception as e:
                print("Error broadcasting message:", e)
                clients.remove(client)


def handle_client(client_socket, client_address):
    try:
 
        client_name = client_socket.recv(1024).decode()
        print(f"{client_name} connected from {client_address}")

      
        welcome_message = f"Welcome, {client_name}!"
        client_socket.sendall(welcome_message.encode())

        while True:
            message = client_socket.recv(4096)  
            if not message:
                break
            print(f"Received audio from {client_name}")
            broadcast(message, client_socket)
    except Exception as e:
        print("Error handling client:", e)
    finally:
        print(f"{client_name} disconnected")
        client_socket.close()
        clients.remove(client_socket)


def signal_handler(sig, frame):
    print('Exiting server...')
    for client_socket in clients:
        client_socket.close()
    sys.exit(0)

# Main server function
def start_server():
    HOST = '0.0.0.0'  
    PORT = 12345

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Server started on {HOST} port {PORT}")

 
    signal.signal(signal.SIGINT, signal_handler)

    while True:
        client_socket, client_address = server.accept()
        clients.append(client_socket)
        client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_handler.start()

if __name__ == "__main__":
    start_server()
