import socket
import threading
import os
import shutil
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip_address = ''
ip_address = input("please enter the server's private IP address")
client.connect((ip_address, 2000))#ip address here
project = os.getcwd()
filename = ""
filepath = ""
new = ""
def receive():
    while True:
        try:
            data = client.recv(1024)
            if data:
                print(data.decode('utf-8'))
        except:
            continue
def send_file(filepath, new):
    new_filepath = os.path.join(project, new)
    shutil.copy(filepath, new_filepath)
    client.send("sending...".encode('utf-8'))
    with open(new, "rb") as file:
        file_size = os.path.getsize(new)
        client.send(new.encode())
        client.send(str(file_size).encode())
        file_data = file.read()
        client.sendall(file_data)
    client.send(b"<LOL>")
    print(f"File {new} sent successfully.")


while True:
    thread_receive = threading.Thread(target=receive, daemon=True).start()
    data = input()
    if data == "send_file":
        print("ENTER FILE PATH:")
        filepath = input()
        print("Enter new name for image (must end with the extension type):")
        new = input()
        send_file(filepath, new)
    elif data == "exit_chat":
        print("Closing connection...")
        client.close()
        break
    else:
        client.send(data.encode('utf-8'))
