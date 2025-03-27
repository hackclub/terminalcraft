import socket
import threading
import struct
clients = []
def receive_file(client_socket):
    try:
        file_name_size = struct.unpack("I", client_socket.recv(4))[0]
        file_name = client_socket.recv(file_name_size).decode()
        print(f"Receiving file: {file_name}")
        file_size = struct.unpack("Q", client_socket.recv(8))[0]
        print(f"File size: {file_size} bytes")
        file_data = b""
        while len(file_data) < file_size:
            data = client_socket.recv(4096)
            file_data += data
        with open(file_name, "wb") as file:
            file.write(file_data)
        print(f"File received successfully: {file_name}")
    except Exception as e:
        print(f"Error occurred: {e}")
def server_send():
    while True:
        message = input()
        if message.lower() == "exit":
            print("Shutting down server...")
            for client in clients:
                client.close()
            break
        else:
            broadcast(None, f"Server: {message}".encode('utf-8'))


def broadcast(client_socket, data):
    for client in clients:
        if client != client_socket:
            try:
                client.send(data)
            except:
                clients.remove(client)
def handle_client(client_socket, addr):
    print(f'Connected by {addr}')
    clients.append(client_socket)
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"{addr} said: {data.decode('utf-8')}")
            if data.decode('utf-8') == "sending...":
                receive_file(client_socket)
            else:
                broadcast(client_socket, f"{addr} said: {data}".encode('utf-8'))
    except:
        pass
    finally:
        print(f"Connection closed: {addr}")
        clients.remove(client_socket)
        client_socket.close()

def start_server(host='0.0.0.0', port=9000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"Server listening on {host}:{port}")
    threading.Thread(target=server_send).start()
    while True:
        client_socket, address = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, address))
        client_thread.start()



if __name__ == "__main__":
    start_server()
