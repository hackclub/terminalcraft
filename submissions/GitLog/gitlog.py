from github import Github, Auth
import json
import datetime
import keyring


class user:
    def __init__(self):
        self.access_token = keyring.get_password("system", "github-access-token")
        self.running = True
        self.cur_repo = ""

    def main_menu(self):
        print("\nwelcome to GitLog: Options\n\n")
        menu_option = input("1) Create Log \n2) Set Current Repo \n3) Update Repo Data \n4) Setup \n5) close\n") # get menu input
        if menu_option == "1":
            self.update_log() # update logs
            return
        if menu_option == "2":
            self.set_current_repo() # setting current repo
            return
        if menu_option == "3": 
            self.update_repo_data() # update repo data
            return
        if menu_option == "4":
            self.setup_client() # setup client .config file
            return
        if menu_option == "5":
            self.running = False # quit
        else:
            print("input not recognized\n")

    def setup_client(self):
        print("read the readme for a explanation on how to get the needed variables \nhttps://github.com/BoaN235/GitLog/blob/main/readme.md")
        self.access_token = input("please input your github access token:\n")
        keyring.set_password("system", "github-access-token", self.access_token)
        self.connect_to_github()

    def access_github(self):
        # using an access token
        try: 
            self.connect_to_github()
        except:
            print("looks like your settings are not setup or your github access token is wrong")
            self.setup_client()
        while self.running:
            self.main_menu()
        self.g.close()

    def connect_to_github(self):
            auth = Auth.Token(self.access_token)
            self.g = Github(auth=auth)
            self.user = self.g.get_user()

    def update_repo_data(self):
        data = [] 
        for repo in self.user.get_repos(): # grabs repo names from github
            data.append(str(repo.full_name))
        with open('data.json', 'w') as f: # updates a json file
            json.dump(data, f, sort_keys=True)
        print("updated repo list")

    def set_current_repo(self):
        print(self.cur_repo)
        with open('data.json', 'r') as f: # open serialized data 
            data = json.load(f)
        print("Which repo would you like to add a log file to")
        i = 0 
        for repo in data: # create the options of each repo
            print(str(i) + ") " + str(repo) + "")
            i += 1
        repo_input = input("Which repo would you like to add a log file to \n")
        try: # check if the number is an int 
            repo_index = int(repo_input)
            if repo_index < i:
                self.cur_repo = data[int(repo_input)] # sets current repo
            else:
                print("input is not a valid number\n")
        except ValueError:
            print("input is not a valid character\n")


    def update_log(self):
        if self.cur_repo == "":
            print("current repo not set\n")
            self.set_current_repo()
        with open('data.json', 'r') as f:
            data = json.load(f)
        for repo_name in data: 
            if repo_name == self.cur_repo:
                l = log()
                current_repo = self.g.get_repo(str(repo_name))
                r = repository(current_repo)
                r.add_log(l)

class repository:
    def __init__(self, repo):
        self.repo = repo
        self.name = repo.full_name
        self.contents = self.repo.get_contents("")

    def add_log(self, log):
        Has_Log_File = False
        #if log.log_has_img:
         #   with open(log.img, "rb") as f:
        #        image_file = f.read()
        #        image_md = base64.b64encode(image_file).decode("utf-8")
        #else:
        #    image_md = ""
        log_msg = f"\n\n### {log.title} -- {log.date}\n\n{log.value}\n" #+ image_md
        for content in self.contents:
            org_content = content.decoded_content.decode()
            if content.path == "LOG.md":
                msg = str(org_content) +  log_msg
                self.repo.update_file(content.path, "updated LOG.MD file", msg , content.sha)
                Has_Log_File = True
        if Has_Log_File == False:
            msg = "# Log\n\n## created with [GitLog](https://github.com/BoaN235/GitLog)" + log
            self.repo.create_file("LOG.md", "added LOG.MD file", msg)
        print("\nCompleted Log")
        return
        

class log:
    def __init__(self):
        self.date = datetime.datetime.now().strftime("%A, %B %d, %Y %H:%M:%S")
        self.title = input("input title:\n")
        self.value = input("input log:\n")
        #if input("do you want to add an image?[Y/N]") == "Y":
        #    self.log_has_img = True
        #    self.img = input("input image path:\n")
        #else:
        #    self.log_has_img = False

u = user()

u.access_github()
