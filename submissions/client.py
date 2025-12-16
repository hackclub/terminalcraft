from requests import sessions
from iformat import iprint
from sys import argv
import colorama as cr

if len(argv) < 2:
    url = f"http://localhost:5000/api"
else:
    url = argv[1]

s = sessions.Session()

current_convo_id = None
current_convo_name = None
current_user_id = None
current_history_start = 0
current_history_end = None  # Not currently in use

cached_users = {}

def make_request(method, url, json=None, suppress_errors=False, **kwargs):
    print(f"{cr.Fore.MAGENTA}Loading...{cr.Style.RESET_ALL}\r", end="")
    response = s.__getattribute__(method)(url, json=json, **kwargs)
    if response.status_code//100 == 2:
        return response.json()
    elif not suppress_errors:
        print(f"{cr.Fore.RED}Error: {response.status_code}, {response.json().get('error') or response.text}{cr.Style.RESET_ALL}")

def clear_screen():
    print("\033[H\033[J")

def help():
    print(f"""
{cr.Fore.BLUE}Commands:
    {cr.Fore.CYAN}/h{cr.Style.RESET_ALL}, {cr.Fore.CYAN}/help{cr.Style.RESET_ALL}: Show this help message
    {cr.Fore.CYAN}/q{cr.Style.RESET_ALL}, {cr.Fore.CYAN}/quit{cr.Style.RESET_ALL}: Quit the client
    {cr.Fore.CYAN}/c{cr.Style.RESET_ALL}, {cr.Fore.CYAN}/create{cr.Style.RESET_ALL}: Create a conversation
    {cr.Fore.CYAN}/j{cr.Style.RESET_ALL}, {cr.Fore.CYAN}/join{cr.Style.RESET_ALL}: Join a conversation
    {cr.Fore.CYAN}/l{cr.Style.RESET_ALL}, {cr.Fore.CYAN}/leave{cr.Style.RESET_ALL}: Leave the current conversation
    {cr.Fore.CYAN}/r{cr.Style.RESET_ALL}, {cr.Fore.CYAN}/reload{cr.Style.RESET_ALL}: Reload the conversation to check for new messages
    {cr.Fore.CYAN}/h{cr.Style.RESET_ALL}, {cr.Fore.CYAN}/history{cr.Style.RESET_ALL}: Read back through the conversation history
    {cr.Fore.CYAN}/m{cr.Style.RESET_ALL}, {cr.Fore.CYAN}/message{cr.Style.RESET_ALL}: Send a message to the current conversation

    When in a conversation, you can type messages directly and press Enter to send them. Press enter with no message to reload the conversation. Commands can still be used.
""")

def create_user(username):
    r = make_request("post", f"{url}/users", json={
        "name": username
    })
    if r:
        print(f"{cr.Fore.CYAN}User created: {username} (#{r.get('user_id')}){cr.Style.RESET_ALL}")
        global current_user_id
        current_user_id = r.get('user_id')

def create_convo(name):
    r = make_request("post", f"{url}/convos", json={
        "name": name
    })
    if r:
        print(f"{cr.Fore.CYAN}Conversation created: {name} (#{r.get('convo_id')}){cr.Style.RESET_ALL}")
        return r.get('convo_id')

def join_convo(convo_id):
    r = make_request("get", f"{url}/convos/{convo_id}")
    if r:
        clear_screen()
        global current_convo_name
        global current_convo_id
        current_convo_name = r.get('name')
        current_convo_id = convo_id
        print(f"{cr.Fore.CYAN}Joined conversation: {r.get('name')} (#{convo_id}){cr.Style.RESET_ALL}")

def convo_banner():
    print(f"{cr.Fore.BLUE}{current_convo_name} (#{current_convo_id}){cr.Style.RESET_ALL}")

def reload_convo():
    r = make_request("get", f"{url}/messages?convo_ids={current_convo_id}&start={current_history_start}")
    if r:
        clear_screen()
        convo_banner()
        for message in r:
            uid = message.get('user_id')
            if uid not in cached_users:
                user = make_request("get", f"{url}/users/{uid}", suppress_errors=True)
                if user is None:
                    cached_users[uid] = f"<Deleted User {uid}>"
                else:
                    cached_users[uid] = user.get('name')
            print(f"{cr.Fore.GREEN}{cached_users[uid]}{cr.Style.RESET_ALL}: {message.get('content')}")

def create_message(content):
    r = make_request("post", f"{url}/messages", json={
        "convo_id": current_convo_id,
        "user_id": current_user_id,
        "content": content
    })
    if r:
        print(f"{cr.Fore.CYAN}Message sent: {content}{cr.Style.RESET_ALL}")

def leave_convo():
    global current_convo_id
    global current_convo_name
    global current_history_start
    global current_history_end
    current_convo_id = None
    current_convo_name = None
    current_history_start = -10
    current_history_end = 0
    print(f"{cr.Fore.CYAN}Left conversation.{cr.Style.RESET_ALL}")

name = input(f"{cr.Fore.CYAN}[/h for help]{cr.Style.RESET_ALL} Creating a new user... Enter your desired username: ")
while name == "/h" or name == "/help":
    help()
    name = input(f"Creating a new user... Enter your desired username: ")
create_user(name)

while True:
    try:
        cmd = input("          \n> ")
        if cmd == "":
            reload_convo()
            continue
        elif cmd.startswith("/"):
            if cmd in ["/h", "/help"]:
                help()
            elif cmd in ["/q", "/quit"]:
                break
            elif cmd in ["/c", "/convo"]:
                name = input("Enter the name of the conversation: ")
                cid = create_convo(name)
                if cid is not None:
                    join_convo(cid)
                    reload_convo()
            elif cmd in ["/j", "/join"]:
                convo_id = int(input("Enter the conversation ID: "))
                join_convo(convo_id)
                reload_convo()
            elif cmd in ["/l", "/leave"]:
                if current_convo_id is None:
                    print(f"{cr.Fore.RED}Join a conversation first.{cr.Style.RESET_ALL}")
                    continue
                leave_convo()
            elif cmd in ["/r", "/reload"]:
                if current_convo_id is None:
                    print(f"{cr.Fore.RED}Join a conversation first.{cr.Style.RESET_ALL}")
                    continue
                reload_convo()
            elif cmd in ["/h", "/history"]:
                print("History feature coming soon!")
            elif cmd in ["/m", "/message"]:
                if current_convo_id is None:
                    print(f"{cr.Fore.RED}Join a conversation first.{cr.Style.RESET_ALL}")
                    continue
                content = input("Enter your message: ")
                create_message(content)
                reload_convo()
            else:
                print("Invalid command.")
        else:
            if current_convo_id is None:
                print(f"{cr.Fore.RED}Join a conversation first.{cr.Style.RESET_ALL}")
                continue
            create_message(cmd)
            reload_convo()
    except KeyboardInterrupt:
        break
#print("Quitting...")
#make_request("delete", f"{url}/users/{current_user_id}")