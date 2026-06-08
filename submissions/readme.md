# Socket Communication: Client-Server Chat Application

A simple client-server chat application with file transfer capabilities, built using Python and sockets. This project allows real-time text messaging and file transfers between a client and server.

---

## Credits & Inspiration
This project is inspired by the simplicity and power of socket programming in Python. It is published mainly for **Hack Club** and for others to learn about networking and socket communication.

---

## Features
- Real-time text messaging between client and server.
- Server broadcasts to all connected to client.
- File transfer functionality (e.g., images, documents).
- Graceful connection termination.
- Cross-platform compatibility (Windows, macOS, Linux).

---

## Bugs
- If the socket doesn’t close correctly, you may need to change the port number the next time you run the server and client.


## Installation

### Command prompt
1. Clone the repository or download the script:
   ```sh
   git clone https://github.com/Abdo1713/socket-communication-python.git
   cd socket-communication-python
   pip install -r requirements.txt
2. Run the script:
   ```sh
   Server:
     cd "text chat\server"
     python main.py
   Client:
     cd "text chat\client"
     python main.py

---

### **Dependencies, How to Use, Important Notes, Contributing, and License**

```markdown
## Dependencies
The project uses only built-in Python libraries: socket threading os shutil

No additional installations are required.

---

## How to Use
1. Start the server first by running the server script.
2. Start the client in a separate terminal window.
3. Use the client to send messages or files to the server.
4. To send a file, type `send_file` in the client and follow the prompts.
5.File sent will be at `C:\Users\YourUsername\socket-communication-python\text chat\server\`
6. To end the chat, type `end_chat` in the client or `end_chat` in the server.

---

## Important Notes
1. **Server Dependency**:
   - The client will not work if the server is not running. Ensure the server is functional before starting the client.

2. **Socket Issues**:
   - If the socket doesn’t close correctly, you may need to change the port number the next time you run the server and client.

3. **File Naming**:
   - When naming the new file during file transfer, include the file extension (e.g., `.jpg`, `.docx`).

4. **Server IP Address**:
   - When the client code runs, it first asks you for the server's private IP_address

5. **Send_file**:
   -For some reason sending files over cmd sometimes malfunctions and doesn't get sent through but texting works perfectly fine
---

## Contributing
Feel free to contribute to this project by opening issues or submitting pull requests.


  
