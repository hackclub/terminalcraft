import socket
import threading
import os
import shutil
import struct
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip_address = ''
ip_address = input("please enter the server's private IP address")
client.connect((ip_address, 9000))#ip address here
filename = ""
filepath = ""
def receive():
    while True:
        try:
            data = client.recv(1024)
            if data:
                print(data.decode('utf-8'))
        except:
            continue


def send_file(filepath, client):
    file_name = os.path.basename(filepath).encode('utf-8')
    file_size = os.path.getsize(filepath)
    client.send("sending...".encode('utf-8'))
    ack = client.recv(1024)  # Add this line
    if ack.decode() != "READY":
        print("Server not ready, aborting file transfer.")
        return
    client.send(struct.pack("!I", len(file_name)))
    client.send(file_name)
    client.send(struct.pack("!Q", file_size))
    with open(filepath, "rb") as file:
        while chunk := file.read(4096):
            client.send(chunk)

    print(f"File '{filepath}' sent successfully.")
while True:
    thread_receive = threading.Thread(target=receive, daemon=True).start()
    print("Type your message:   ")
    data = input()
    if data == "send_file":
        print("ENTER FILE PATH:")
        filepath = input()
        send_file(filepath, client)
    elif data == "exit_chat":
        print("Closing connection...")
        client.close()
        break
    else:
        client.send(data.encode('utf-8'))
