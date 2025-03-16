#PyTyper
#A hackertyper knockoff by j4y_boi
#https://github.com/j4y-boi/pytyper

import random
import sys
from time import sleep as wait
import readchar
import os

# This piece of code was adapted from:
# https://gist.github.com/kgriffs/5726314
#---------------------------------------------
if not os.name == "nt":
    import termios
    import atexit

    def enable_echo(enable):
        fd = sys.stdin.fileno()
        new = termios.tcgetattr(fd)
        if enable:
            new[3] |= termios.ECHO
        else:
            new[3] &= ~termios.ECHO

        termios.tcsetattr(fd, termios.TCSANOW, new)

    atexit.register(enable_echo, True)
    enable_echo(False)
#---------------------------------------------

typedSnippets = 0
leaving = False
termSize = False
last_choice = None
typedcode = ""

notifLength = 30

oldx = 0
oldy = 0

TerminalCol = 62
TerminalLin = 12

splashscreenText = [
    "hacking = True",
    "s0 3p1k h4x0r",
    "Accessing mainframe...",
    "404, didn't find text",
    "*keyboard noises*",
    "gotta love Hollywood",
    "bypassing the firewall??? :0",
]

snippets = [
    "----\nimport os\nimport sys\nimport random\nimport socket\nimport struct\nimport hashlib\n\n"
    "def breach_mainframe():\n    mainframe_ip = '198.51.100.14'\n    session_key = hashlib.md5(mainframe_ip.encode()).hexdigest()\n    exploit_code = os.urandom(16).hex()\n    checksum = hashlib.sha256(exploit_code.encode()).hexdigest()\n    return f'[+] Injecting zero-day exploit {exploit_code} into {mainframe_ip} with session {session_key} (checksum: {checksum})'",
    "class Exploit:\n    def __init__(self, target):\n        self.target = target\n    def attack(self):\n        payload = os.urandom(32).hex()\n        response_code = random.choice([200, 403, 500])\n        payload_signature = hashlib.md5(payload.encode()).hexdigest()\n        return f'[+] Sent crafted payload {payload} (sig: {payload_signature}) to {self.target}, response: {response_code}'",
    "def brute_force(password):\n    for attempt in range(1000, 9999):\n        hashed_attempt = hashlib.sha256(str(attempt).encode()).hexdigest()\n        if hashed_attempt == password:\n            return f'[+] Access Granted with password {attempt}'\n    return '[-] Access Denied'",
    "def encrypt_data(data):\n    encrypted = ''.join(chr(ord(c) ^ 42) for c in data)\n    key_hash = hashlib.sha256(str(42).encode()).hexdigest()\n    return f'Encrypted: {encrypted} (key hash: {key_hash})'",
    "def backdoor():\n    key = hashlib.sha512(str(random.randint(100000, 999999)).encode()).hexdigest()\n    session_id = os.urandom(8).hex()\n    return f'Access key: {key[:16]} (session: {session_id})'",
    "class Virus:\n    def __init__(self):\n        self.payload = 'rm -rf / --no-preserve-root'\n    def execute(self):\n        checksum = hashlib.md5(self.payload.encode()).hexdigest()\n        encoded_payload = self.payload.encode('utf-8').hex()\n        return f'[+] Payload checksum: {checksum}, encoded: {encoded_payload}, executing...'",
    "def spoof_ip():\n    return f'192.168.1.{random.randint(2, 254)}'",
    "def deep_web_access():\n    nodes = random.randint(50, 200)\n    session_key = os.urandom(16).hex()\n    return f'Connected to {nodes} Tor nodes. Session key: {session_key}.'",
    "def bypass_firewall():\n    proxy_chain = [f'proxy-{random.randint(1000, 9999)}' for _ in range(5)]\n    tunnel_id = hashlib.md5(''.join(proxy_chain).encode()).hexdigest()\n    return f'[+] Routing traffic through: {' -> '.join(proxy_chain)} (Tunnel ID: {tunnel_id[:12]})'",
    "def inject_sql():\n    query = 'SELECT * FROM users WHERE username = \'admin\' AND password = \' OR \'1\'=\"1\" --\''\n    query_hash = hashlib.sha1(query.encode()).hexdigest()\n    return f'[+] Executing SQL Injection: {query} (Query Hash: {query_hash})'",
    "def scramble_logs():\n    log_files = ['/var/log/auth.log', '/var/log/syslog', '/var/log/nginx/access.log']\n    scrambled_hashes = {log: hashlib.md5(log.encode()).hexdigest() for log in log_files}\n    operation_id = os.urandom(8).hex()\n    return f'[+] Logs overwritten with hashes: {scrambled_hashes} (Operation ID: {operation_id})'",
    "def reverse_shell():\n    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n    sock.connect(('1337.42.0.1', 4444))\n    local_port = sock.getsockname()[1] \n    session_token = os.urandom(16).hex()\n    return f'[+] Reverse shell connected to 1337.42.0.1:4444 (Local Port: {local_port}, Session: {session_token})'",
    "def fake_identity():\n    user_agent = random.choice(['Mozilla/5.0', 'curl/7.68.0', 'Nmap Scripting Engine'])\n    return f'User-Agent: {user_agent}/Python'",
    "class ZeroDay:\n    def __init__(self, target):\n        self.target = target\n    def deploy(self):\n        exploit_code = os.urandom(24).hex()\n        return f'[+] Exploiting unknown vulnerability on {self.target} with payload {exploit_code}'",
    "def create_botnet():\n    bot_count = random.randint(1000, 5000)\n    network_id = hashlib.md5(str(bot_count).encode()).hexdigest()\n    return f'[+] Botnet online. Nodes: {bot_count}, Network ID: {network_id[:12]}'",
    "def decrypt_data(data, key):\n    decrypted = ''.join(chr(ord(c) ^ key) for c in data)\n    return f'Decrypted: {decrypted}'",
    "def obfuscate_payload():\n    polymorph_key = os.urandom(8).hex()\n    return f'[+] Obfuscating payload with polymorph key {polymorph_key}. Signature undetected!'",
    "class Darknet:\n    def __init__(self):\n        self.market = 'Fabricroute 3.0'\n    def access(self):\n        session_id = os.urandom(16).hex()\n        return f'[+] Browsing {self.market} with session {session_id}...'",
    "class AI_Hacker:\n    def __init__(self):\n        self.model = 'GPT-1337'\n    def generate_exploit(self):\n        attack_vector = os.urandom(16).hex()\n        return f'[+] AI-generated exploit vector: {attack_vector}'"
]


def printBox(lenv:int,*sentences:str):
    length = lenv
    lines = []

    for sentence in sentences:
        split_lines = sentence.split("\n")
        lines.extend(split_lines)

    for i in lines:
        if len(i) > length:
            length = len(i)

    print(f"┌{"─"*length}┐")
    for r in lines:
        print(f"│{r.center(length)}│")
    print(f"└{"─"*length}┘")

def clearterminal(header:bool,typed:bool,returnlines:int=0): #compatibility, am i right
    if returnlines == 0:
        os.system("cls" if os.name == "nt" else "clear")
    else:
        for i in range(returnlines):
            sys.stdout.write("\033[2K\r") 
            sys.stdout.write("\033[1A")
            sys.stdout.flush()

    sys.stdout.write("\033[32m") #green color :0
    if header:
        printBox(60,"[H A C K I N G   T E R M I N A L]",f"-\nsplashscreen_text = {chosenSplashscreen}")
    if typed:
        print(typedcode,end="")

def hacker_typer():
    global leaving
    global typedSnippets
    global typedcode
    global termSize
    global last_choice
    
    if not last_choice == None:
        code = random.choice([s for s in snippets if s != last_choice])  # Exclude last choice
        last_choice = code
    else:
        code = snippets[0]
        last_choice = ""

    index = 0

    while index < len(code):
        key = readchar.readkey()
        if key == '\x1b':  # esc for exit
            clearterminal(False,False)
            print("[ See ya next time :) ]")
            leaving = True
            break
        if os.get_terminal_size().columns < TerminalCol or os.get_terminal_size().lines < TerminalLin:
            termSize = True
            break  # terminal too small

        for i in range(random.randint(1,5)):
            try:
                sys.stdout.write(code[index])
                typedcode = typedcode + code[index]
                sys.stdout.flush()
                index += 1
            except IndexError:
                continue
        #wait(0.01)

    if not leaving:
        sys.stdout.write("\n\n")
        typedcode = typedcode + "\n\n"

    typedSnippets += 1

chosenSplashscreen = splashscreenText[random.randint(0,len(splashscreenText)-1)]

if __name__ == "__main__":
    clearterminal(False,False)
    printBox(60,"▀█▀ █▄█ █▀█ █▀▀ █▀█ █▀█ █▄█\n █   █  █▀▀ ██▄ █▀▄ █▀▀  █ \nA hackertyper knockoff by j4y_boi","-","[Press any key to type, press 'ESC' to exit.]","(Go in fullscreen for the FULL experience.)","Press any key to begin.")
    key = readchar.readkey()
    clearterminal(True,False)
    while not leaving:
        term_x, term_y = os.get_terminal_size().columns, os.get_terminal_size().lines
        if term_x < TerminalCol or term_y < TerminalLin:
            while term_x < TerminalCol or term_y < TerminalLin:
                newx, newy = os.get_terminal_size().columns, os.get_terminal_size().lines
                if newx != oldx or newy != oldy:
                    oldx, oldy = newx, newy
                    clearterminal(False,False)
                    print("\n" * (newy // 2 - 1))  # Centering
                    print("Your terminal is too small!".center(newx))
                
                wait(0.5)
                term_x, term_y = os.get_terminal_size().columns, os.get_terminal_size().lines

            clearterminal(True,False)
        else:
            hacker_typer()

            if leaving or termSize:
                continue

            if typedSnippets % 10 == 0 and typedSnippets != 0:
                clearterminal(True,False)
                printBox(notifLength, "Processing packets...")
                wait(5)
                for i in range(6):
                    clearterminal(False,False,3)
                    if i % 2 == 0:
                        printBox(notifLength, f"Processed units: {typedSnippets}")
                    else:
                        printBox(notifLength, "")
                    wait(1)
                clearterminal(False,False,3)
                printBox(notifLength, "Continuing...")
                wait(5)
                clearterminal(True,True)

            elif random.randint(1,15) == 1:
                choices = {
                    1: ["Bypassing passcode...", "Access Denied", "Access Granted", "ERROR: COULDN'T RESOLVE PASS_BYPASS"],
                    2: ["Resolving hash...", "FAILED: INSUFFICIENT RESOURCES", "Success!", "ERROR: ERROR WHILE RESOLVING"],
                    3: ["Installing virus...", "Failed!", "Installed!", "ERROR: HOST_DISCONNECTED"],
                }
                choiced = random.randint(1,len(choices))

                printBox(notifLength, choices[choiced][0])
                wait(5)
                choice = random.randint(1,3)
                for i in range(6):
                    clearterminal(False,False,3)
                    if choice == 1:
                        print("\033[31m",end="")
                    elif choice == 3:
                        print("\033[33m",end="")
                    
                    if i % 2 == 0:
                        if choice == 1:
                            printBox(notifLength, choices[choiced][1])
                        elif choice == 2:
                            printBox(notifLength, choices[choiced][2])
                        elif choice == 3:
                            printBox(notifLength, choices[choiced][3])
                    else:
                        printBox(notifLength, "")
                    wait(1)

                clearterminal(False,False,3)
                printBox(notifLength, "Continuing...")
                wait(5)
                clearterminal(True,True)
