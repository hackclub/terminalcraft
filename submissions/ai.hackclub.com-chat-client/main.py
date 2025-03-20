import requests
import json
import os
import time
import copy


class SearchSession:
    def __init__(self):
        self.url = "https://ai.hackclub.com/chat/completions"
        self.headers = {
            "Content-Type": "application/json"
        }
        self.messages = [
            #{"role": "system", "content": "The user is looking for a past session that has a name and a description attached to it. He is asked to tell you what the session was about and from that you must choose one of the following and only respond with the name of the sessions that match what the user said the most."}
        ]
        self.existing_session = False
        self.filename_of_existing_session = ""
    
    def add_list_of_sessions(self, list_of_sessions):
        self.messages.append({"role": "system", "content": "You have to respond only with a name in the list. The user will tell you what the session was about and you have to choose one item out of this list that most closely matches the name which is also a description. * ONLY RESPOND WITH THE EXACT NAME OF THE SESSION. Here is the list of sessions you can choose from: " + str(list_of_sessions)})

    

    def get_filename_of_existing_session(self):
        return self.filename_of_existing_session

    def add_user_message(self, content):
        self.messages.append({"role": "user", "content": content})


    def add_system_message(self, content):
        self.messages.append({"role": "system", "content": content})

    def get_response(self):

        data = {"messages": self.messages}
        response = requests.post(self.url, headers=self.headers, json=data)

        #print(self.messages)
        if response.status_code == 200:

            assistant_message = response.json().get('choices')[0].get('message').get('content')
            self.messages.append({"role": "assistant", "content": assistant_message})
            return assistant_message
        
        else:
            return f"Failed to get a response. Status code: {response.status_code}"

class ChatSession:
    def __init__(self):
        
        self.url = "https://ai.hackclub.com/chat/completions"
        self.headers = {
            "Content-Type": "application/json"
        }
        # load system message from settings.json
        try:
            with open ("data/settings.json", 'r') as json_file:
                data = json.load(json_file)
                system_message = data.get("system_messages")
            self.messages = [
                {"role": "system", "content": system_message}
            ]
        except:
            self.messages = [
                {"role": "system", "content": "You are a terminal assitant that helps the user get what they want done in the terminal."}
            ]
        self.existing_session = False
        self.filename_of_existing_session = ""

    
    def load_session(self, filename):
        with open("sessions/" + filename, 'r') as json_file:
            self.messages = json.load(json_file)

        self.filename_of_existing_session = filename
        self.existing_session = True

    def get_filename_of_existing_session(self):
        return self.filename_of_existing_session

    def add_user_message(self, content):
        self.messages.append({"role": "user", "content": content})

    def add_system_message(self, content):
        self.messages.append({"role": "system", "content": content})

    def get_response(self):

        data = {"messages": self.messages}
        response = requests.post(self.url, headers=self.headers, json=data)

        #print(self.messages)
        if response.status_code == 200:

            assistant_message = response.json().get('choices')[0].get('message').get('content')
            self.messages.append({"role": "assistant", "content": assistant_message})
            return assistant_message
        
        else:
            return f"Failed to get a response. Status code: {response.status_code}"
        
    
        

def find_session():
    search_session = SearchSession()
    found_session_name = ""
    found_session = False

    search_session.list_of_sessions = os.listdir("sessions")
    print(search_session.list_of_sessions)
    search_session.add_list_of_sessions(os.listdir("sessions"))

    while found_session == False:
        search_query_for_session = input("What do you remember about the conversation: ")
        search_session.add_user_message(search_query_for_session)
        response = search_session.get_response()
        print(f"\n  AI: {response}")
        #print(search_session.messages)

        if response in search_session.list_of_sessions:
            found_session = True
            found_session_name = response
        else:
            print("Session not found. Try again.")
            search_session.add_system_message("Invalid session name. the user will give you more info and choose again.")

    return found_session_name

def main():
    session = ChatSession()


    print('Type "-exit" to exit session and "-help" for more info.\n')

    valid_input = False

    while valid_input == False:

        continue_last_session = input("continue with last session y/n choose an other one o : ([y]/n/o): ").lower()

        if continue_last_session == 'y' or continue_last_session == 'yes' or continue_last_session == '':

            with open("data/data.json", 'r') as json_file:

                data = json.load(json_file)
                last_session = data.get("last_session")

                if last_session:

                    with open("sessions/" + last_session, 'r') as json_file:
                        session.messages = json.load(json_file)
                        print("Continuing with : " + last_session)

                    session.existing_session = True
                    session.filename_of_existing_session = last_session
                    print(session.filename_of_existing_session) # here it works

                else:
                    print("No last session found.")
                valid_input = True
        
        elif continue_last_session == 'n' or continue_last_session == 'no':
            print("Starting a new session...")
            valid_input = True
        
        elif continue_last_session == 'o' or continue_last_session == 'past' or continue_last_session == 'other':
            session.existing_session = True
            session.load_session(find_session())
            print("Continuing with : " + session.filename_of_existing_session)
            valid_input = True

        else:
            print("Invalid input.")

    # main loop
    while True:

        user_input = input("\n  you: ")

        if user_input.lower() == '-exit':
            exit_sequence(session)
            break 
        elif user_input.lower() == '-help':
            print('\n  you can change the min number of messages to save in the settings.json file. The default is 3. \ncommands :\n-exit : exit the session\n-help : show this message\n-load "filename" : load a file into the chat (must be in this directory)')
        elif user_input.lower().startswith('-load'):
            try:
                filename = user_input.split(" ")[1].removeprefix('"').removesuffix('"')
                with open(filename, 'r') as file:
                    file_contents = file.read()
                session.add_system_message(f"The user loaded the following file: '{filename}' here are its contents:\n{file_contents}")
                print(f"successfully loaded {filename}.")
            except Exception as e:
                print(f"Failed to load file. error : {e}")
        else:
            session.add_user_message(user_input)
            response = session.get_response()
            print(f"\n  AI: {response}")



def load_min_messages_to_save():
    try:
        with open("data/settings.json", 'r') as json_file:
            data = json.load(json_file)
            return int(data.get("min_messages_to_save"))
    except:
        print("Failed to load settings.json. Using default value of 3 min messages to save.")
        return 3

def exit_sequence(session):
    json_data = copy.deepcopy(session.messages)

    session.add_system_message("The user has ended the session. Choose at most 10 keywords that represent the session and that the user will be able to associate with this session when he sees it. Only respond with the name you chose, put space between words, do NOT end it with .json and make sure that if the user asks a question center the answer around the main idea and make it recoginsable..")
 
    ai_decided_name = session.get_response() + ".json"

    

    if session.existing_session == True:

        name = session.get_filename_of_existing_session()
        if name == "": print("name of existing session is empty")

        file_path = os.path.join("sessions", name)

        with open(file_path, 'w') as json_file:
            json.dump(json_data, json_file, indent=4)
            print("\n   Session saved as " + session.get_filename_of_existing_session() + "\n")

        json_data = {"last_session": session.filename_of_existing_session}
        
        with open(os.path.join("data", "data.json"), 'w') as json_file:
            json.dump(json_data, json_file, indent=4)

    else:
        min_messages_to_save = load_min_messages_to_save() #default 3
        
        print(len(session.messages))
        if len(session.messages) <= min_messages_to_save + 3: 
            print(f"Session not saved. Session doesnt have more than {min_messages_to_save} messages.")
            return
        
        else:

            with open(os.path.join("sessions", ai_decided_name), 'w') as json_file:
                json.dump(json_data, json_file, indent=4)
                print("\n   Session saved as " + ai_decided_name + "\n")

            json_data = {"last_session": ai_decided_name}

            with open(os.path.join("data", "data.json"), 'w') as json_file:
                json.dump(json_data, json_file, indent=4)


    





if __name__ == "__main__":
    main()