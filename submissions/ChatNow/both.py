import subprocess
import time

server_process = subprocess.Popen(['python', 'server.py'])

time.sleep(1)

client_process = subprocess.Popen(['python', 'client.py'])

server_process.wait()
client_process.wait()
