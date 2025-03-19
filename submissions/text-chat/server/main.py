import socket
import threading
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 3000))
server.listen(1)
def receive(client_socket):
    while True:
        try:
            data = client_socket.recv(1024)
            if data:
                print(f"{addr} said: {data.decode('utf-8')}")
                if data.decode('utf-8') == "sending...":
                    receive_file(client_socket)
        except:
            continue
def receive_file(client_socket):
    file_name = client_socket.recv(1024).decode()
    print(f"Receiving file: {file_name}")
    file_size = int(client_socket.recv(1024).decode())
    print(f"File size: {file_size} bytes")
    file_data = b""
    while len(file_data) < file_size:
        data = client_socket.recv(1024)
        file_data += data
    with open(file_name, "wb") as file:
        file.write(file_data)
    print(f"File received successfully: {file_name}")


client_socket, addr = server.accept()
print(f'Connected by {addr}')
thread_receive = threading.Thread(target=receive, args=(client_socket,))
thread_receive.start()
while True:
    data = input()
    if data == "exit_chat":
        print("Closing connection...")
        client_socket.close()
        server.close()
        break
    else:
        client_socket.send(data.encode('utf-8'))

