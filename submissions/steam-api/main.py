from colorama import Fore, Back, Style

import getopt

from steam.steamid import SteamID

from steam.client import SteamClient
client = SteamClient()

from steam.webapi import WebAPI

import sys

#For the user pfp
import climage
import urllib.request

#For getting timestamps
import datetime

import math

arguments = sys.argv[1:]


key = "8140AC02CC93F03CE63F09BE49F1DA48"
api = WebAPI(key)

def clear_previous_line():
    CURSOR_UP = "\033[1A"
    CLEAR = "\x1b[2K"
    print(CURSOR_UP + CLEAR, end="")   # clears ONE line

def crash_error(error):
    print(error)
    exit()

def get_id(user):
    link = 'https://steamcommunity.com/id/' + user
    id = SteamID.from_url(link)
    if(id == None):
        crash_error("Couldn't find the steam account")
    return id

def get_games(id):
    response = api.IPlayerService.GetOwnedGames(
        steamid=id,
        include_appinfo=True,
        include_played_free_games=True,
        include_free_sub=True,  # Or False, depending on your needs
        appids_filter=None,
        language='english',  # Or another language code, e.g., 'spanish', 'french'
        include_extended_appinfo=True  # Or False, depending on your needs
    )
    return response


def get_game_achivements(id, gameid):
    response = api.ISteamUserStats.GetPlayerAchievements(
        steamid=id,
        appid=gameid,
        l='english'  # Or another language code, e.g., 'spanish', 'french'
    )
    return response

def get_user_data(id):
    response = api.ISteamUser.GetPlayerSummaries(
        steamids=str(id)
    )
    return response

#Needs response from get_user_data(id)
def get_user_state(response):
    players = response['response']['players']
    for player in players:
        #Printing the user pfp
        image_path = "./downloaded_image.jpg"
        urllib.request.urlretrieve(player["avatar"], image_path)
        output_pfp = climage.convert(image_path, False, False, True, False, False, 50)
        
        print("\n" + output_pfp + "\n")
        print(f"{Fore.BLUE}Joined in:{Fore.CYAN}: " + str(datetime.datetime.fromtimestamp(player["timecreated"]) ) + Fore.WHITE)
        try:
            player["lastlogoff"]
            print(f"{Fore.BLUE}Last logoff:{Fore.CYAN}: " + str(datetime.datetime.fromtimestamp(player["lastlogoff"]) ) + Fore.WHITE + "\n" )
        except:
            print("Couldn't get user last logoff")

        status = "Offline"
        match player["personastate"]:
            case 1:
                status = "Online"
            case 2:
                status = "Busy"
            case 3:
                status = "Away"
            case 4:
                status = "Snoozing"
            case 5:
                status = "Looking to trade"
            case 6:
                status = "Looking to play"
        print(f"{Fore.BLUE}The user is currently: {Fore.CYAN}{status}{Fore.WHITE}") 

def main():
    #User case
    for argument in arguments:
        if(argument == '-u'):
            #Get achivements
            if(len(sys.argv) > 2 and sys.argv[2] == "-a"):
                user = sys.argv[3]
                id = get_id(user)
                gameid = sys.argv[4]
                response = get_game_achivements(id, gameid)
                achivements = response["playerstats"]["achievements"]
                game_name = response["playerstats"]["gameName"]
                
                print(f"The achivements of {user} in {game_name} are:")
                i = 0
                #if the game has achievements
                achieved_total = 0
                if(response):
                    #Get percentage
                    for achiv in achivements:
                        if(achiv["achieved"]):
                            achieved_total += 1
                    percentage = math.floor((100/len(achivements)) * achieved_total)
                    print(f"{Fore.MAGENTA}Achieved {percentage}%, {achieved_total} of {len(achivements)}")
                    #Print achievements
                    for achiv in achivements:
                        i += 1
                        if(i >= 10):
                            input("CONTINUE.. ")
                            i = 0
                            clear_previous_line()
                        achieved = f"{Fore.CYAN}Achieved, at {str(datetime.datetime.fromtimestamp(achiv["unlocktime"])) }" if achiv["achieved"] else f"{Fore.WHITE}Not Achieved"
                        print(f"{Fore.BLUE}{achiv["name"]}: {achieved} {Fore.WHITE}")
                break
            #Get friends
            elif(len(sys.argv) > 2 and sys.argv[2] == "-f"):
                user = sys.argv[3]
                id = get_id(user)
                gameid = sys.argv[4]
                response = get_game_achivements(id, gameid)
                achivements = response["playerstats"]["achievements"]
                game_name = response["playerstats"]["gameName"]
                
                break
            elif(len(sys.argv) > 2 and sys.argv[2] == "-g"):
                #Find steam account by username and get id 
                user = sys.argv[3]
                id = get_id(user)
                #Get games of account
                response = get_games(id)
                games = response['response']['games']
                print(f"Use {Fore.CYAN}-u -a (USER)(GAME_ID) to see the achivements of a game id")
                if(games):
                    i = 0
                    total_playtime = 0
                    played = 0
                    for game in games:
                        if(game['playtime_forever'] > 10):
                            played += 1
                        total_playtime += game['playtime_forever']
                    percentage = ( 100/len(games) ) * played
                    print(f"{Fore.BLUE}{user}{Fore.CYAN} has played {Fore.CYAN}{played}{Fore.BLUE} games from the {Fore.CYAN}{len(games)}{Fore.BLUE} games bought, {Fore.CYAN}%{round(percentage)}{Fore.WHITE}")
                    print(f"{math.floor(total_playtime/60)} Hours on record\n")

                    for game in games:
                        i += 1
                        if(i >= 10):
                            input("CONTINUE.. ")
                            i = 0
                            clear_previous_line()
                        print(f"{Fore.BLUE}{game['name']}:{Fore.CYAN} AppId:{Fore.WHITE} {game['appid']}, {Fore.CYAN} Total Playtime: {Fore.WHITE}{game['playtime_forever']}")
                break
        else:
            #In case of not having another aditional argument, get steam account and write the id of it
            user = sys.argv[2]
            id = get_id(user)
            account = client.get_user(id)
            print(f"{Fore.BLUE}User {Fore.WHITE}{user}, {Fore.CYAN}id {Fore.WHITE}{id}")
            status_response = get_user_data(id)
            status = get_user_state(status_response)
            print("")
            print(f"{Fore.BLUE}Aditional arguments:{Fore.WHITE}")
            print(f"Use {Fore.CYAN}-u -g{Fore.WHITE} to see the games")
            break

main()
