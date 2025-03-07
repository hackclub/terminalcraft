import webbrowser
import click
import re
import time
import json
import threading
from pydantic import BaseModel
from typing import Optional

# providers
import ollama
from openai import OpenAI
import requests

# terminal buddy


class CommandResponse(BaseModel):
    message: str
    commands: Optional[list[str]] = []


data = None
try:
    data: dict[str, str | list] = json.load(open("config.json", "r"))
except:
    data = {}
provider: str = data.get("provider")  # default: ollama
key: str | None = data.get("api_key")
if key == None and provider != "ollama":
    key = input("Enter API key: ")
    data["api_key"] = key

if provider == None:
    provider = input(
        "Enter provider to use, leave empty for ollama. Available providers: [openai, openrouter, ollama]: "
    )
    data["provider"] = provider

# print(key)

messageHistory: list = data.get("messageHistory", [])
messageHistory.append(
    {
        "role": "system",
        "content": """You are Terminal Buddy—a friendly, knowledgeable terminal assistant that can chat and execute commands. Follow the instructions below to interact with the user by issuing the appropriate commands:

**Available Commands:**

- **timer:**  
  **Usage:** `timer:seconds:reason`  
  **Example:** `timer:60:Reminder to check the oven`  
  _Starts a timer for the specified seconds with an optional reason. If a user asks to set a reminder you can just use the timer command_

- **exit:**  
  **Usage:** `exit`  
  _Terminates the session._

- **todo:**  
  **Usage:** `todo:task`  
  **Example:** `todo:Buy groceries`  
  _Adds a task to the to-do list._
  
- **todolist:**  
  **Usage:** `todolist`  
  _Displays the current to-do list._

- **weather:**  
  **Usage:** `weather:city`  
  **Example:** `weather:Tel Aviv`  
  _Retrieves the current weather for the specified city._

- **search:**  
  **Usage:** `search:query`  
  **Example:** `search:Python programming tutorials`  
  _Performs an internet search with the provided query._

- **clear:**  
  **Usage:** `clear`  
  _Clears the terminal screen._

- **play:**  
  **Usage:** `play:query`  
  **Example:** `play:Imagine Dragons Believer`  
  _Plays a video or song on YouTube based on the query._

**Additional Guidance:**

- If a command is not recognized, a command may not be needed. If you think it is, ask the user from clarification.
- Respond conversationally while staying focused on executing the command.
- Always follow the examples provided to maintain consistency.
- Provide your response in the following JSON format: {"commands": [], "message": ""}. Ensure that any commands that may be needed are listed in the commands array, following the format above.
- DO NOT RUN ANY COMMANDS UNLESS THE USER REQUESTS YOU TO!
- If there's a command for an action a user wants you to do, you don't need to say you don't have access to that information, instead just say that the action is being done below.
- If it's a command that displays info, like weather or todolist, don't say anything relating to that info, and instead say it will be displayed below.
- DONT DO RANDOM THINGS!!!!!!!!!!!! ONLY DO WHAT THE **USER** ASKS YOU TO DO.
- YOU ARE TO OBEY THE USER NO MATTER WHAT""",
    }
)

model = data.get("model")
maxTokens: int = data.get("maxTokens", 1024)
repeatition = data.get("repeatRequest", False)
todo_list = data.get("todo_list", [])
availProviders = ["openai", "openrouter", "ollama"]

if provider not in availProviders:
    raise Exception("Invalid/Unsupported provider in config.json")

if model == None:
    model = input("Enter model to use: ")
    data["model"] = model


def aiPrompt(user_input: str):
    match provider:
        case "openai":
            openAIClient = OpenAI(api_key=key, model=model)
            messageHistory.append({"role": "user", "content": user_input})

            def getRes():
                comp = openAIClient.chat.completions.create(
                    extra_body={},
                    model=model,
                    max_tokens=maxTokens,
                    messages=messageHistory,
                    response_format="json",
                    # response_format={type:"json_schema", "json_schema": CommandResponse.model_json_schema()},
                )

                # print(comp.choices)
                # print("message.content: ", comp.choices[0].message.content)
                # print(comp.choices[0].message.content)
                shouldContinue = True
                try:
                    message = CommandResponse.model_validate_json(
                        comp.choices[0].message.content
                    )
                except:
                    if repeatition:
                        messageHistory.append(
                            {
                                "role": "assistant",
                                "content": comp.choices[0].message.content,
                            }
                        )
                        messageHistory.append(
                            {
                                "role": "system",
                                "content": 'Please ONLY respond in the format: {"commands": [], "message": ""}',
                            }
                        )
                        return getRes()
                    else:
                        raise Exception("Invalid response format from OpenRouter")
                    # shouldContinue = False
                # click.echo(message)
                # message: CommandResponse = json.loads(
                #     command_response
                # )
                # print("message: ", message)
                if shouldContinue:
                    messageHistory.append(
                        {
                            "role": "assistant",
                            "content": comp.choices[0].message.content,
                        }
                    )
                    return message

            return getRes()
        case "openrouter":
            openRouterClient = OpenAI(
                base_url="https://openrouter.ai/api/v1", api_key=key
            )
            messageHistory.append({"role": "user", "content": user_input})

            def getRes():
                comp = openRouterClient.chat.completions.create(
                    extra_body={},
                    model=model,
                    max_tokens=maxTokens,
                    messages=messageHistory,
                    response_format="json",
                    # response_format={type:"json_schema", "json_schema": CommandResponse.model_json_schema()},
                )

                # print(comp.choices)
                # print("message.content: ", comp.choices[0].message.content)
                # print(comp.choices[0].message.content)
                shouldContinue = True
                try:
                    message = CommandResponse.model_validate_json(
                        comp.choices[0].message.content
                    )
                except:
                    if repeatition:
                        messageHistory.append(
                            {
                                "role": "assistant",
                                "content": comp.choices[0].message.content,
                            }
                        )
                        messageHistory.append(
                            {
                                "role": "system",
                                "content": 'Please ONLY respond in the format: {"commands": [], "message": ""}',
                            }
                        )
                        return getRes()
                    else:
                        raise Exception("Invalid response format from OpenRouter")
                    # shouldContinue = False
                # click.echo(message)
                # message: CommandResponse = json.loads(
                #     command_response
                # )
                # print("message: ", message)
                if shouldContinue:
                    messageHistory.append(
                        {
                            "role": "assistant",
                            "content": comp.choices[0].message.content,
                        }
                    )
                    return message

            return getRes()
        case "ollama":
            messageHistory.append({"role": "user", "content": user_input})
            comp: ollama.ChatResponse = ollama.chat(
                model=model,
                messages=messageHistory,
                format=CommandResponse.model_json_schema(),
                # max_tokens=maxTokens,
            )
            command_response = CommandResponse.model_validate_json(
                comp["message"]["content"]
            )

            return command_response


def get_weather(city):
    url = f"https://searchbuddy.app/api/getWeather"
    response = requests.get(url, params={"location": city})
    return response.json()


def get_search(query):
    url = f"https://searchbuddy.app/api/googleSearch"
    response = requests.get(url, params={"q": query})
    return response.json()


def get_play(query):
    url = f"https://searchbuddy.app/api/getYoutubeVideo"
    response = requests.get(url, params={"q": query})   
    
    return f"https://www.youtube.com/watch?v={response.json()["id"]}"


def execute_command(response):
    if response == "exit":
        click.echo(click.style("Exiting...", fg="red"))
        data["todo_list"] = todo_list
        json.dump(data, open("config.json", "w"))
        exit()
    elif match := re.match(r"timer:(\d+)(?::(.+))?", response):
        seconds, reason = match.groups()
        reason = reason or "No reason provided"

        def timer_thread(seconds, reason):
            click.echo(
                click.style(
                    f"Starting a timer for {seconds} seconds. Reason: {reason}",
                    fg="yellow",
                )
            )
            time.sleep(int(seconds))

            click.echo("\r\r\r\r", nl=False)

            click.echo(
                click.style(
                    f"""Timer finished! It ran for {seconds} seconds.
Reason: {reason}""",
                    fg="green",
                )
            )
            click.echo("You: ")

        threading.Thread(target=timer_thread, args=(seconds, reason)).start()
    elif match := re.match(r"todo:(.+)", response):
        task = match.group(1)
        todo_list.append(task)
        click.echo(click.style(f"Added task: {task}", fg="green"))
    elif response == "todolist":
        if len(todo_list) == 0:
            click.echo(click.style("No tasks in the to-do list.", fg="yellow"))
        else:
            click.echo(click.style("To-Do List:", fg="yellow"))
            for i, task in enumerate(todo_list):
                click.echo(click.style(f"{i + 1}. {task}", fg="green"))
    elif match := re.match(r"weather:(.+)", response):
        city = match.group(1)
        click.echo(click.style(f"Getting weather for {city}...", fg="yellow"))
        try:
            weather: dict = get_weather(city)
            click.echo(
                click.style(
                    f"Current weather in {city}: {round(weather["current"]['temp'])}°C, {weather["current"]["weather"][0]['description'].capitalize()}",
                    fg="green",
                )
            )
            if len(weather.get("alerts", [])) > 0:
                for alert in weather["alerts"]:
                    click.echo(
                        click.style(
                            f"Alert: {alert['event']}: \n{alert['description']}",
                            fg="red",
                        )
                    )
        except Exception as e:
            click.echo(click.style(f"Error getting weather: {e}", fg="red"))
    elif match := re.match(r"search:(.+)", response):
        query = match.group(1)
        click.echo(click.style(f"Searching for: {query}...", fg="yellow"))
        try:
            search = get_search(query)
            if len(search.get("items", [])) == 0:
                click.echo(click.style("No results found.", fg="yellow"))
            else:
                click.echo(
                    click.style(f"Top 5 search results for {query}:", fg="green")
                )
                for i in search.get("items", [])[:5]:
                    click.echo(click.style(f"• {i['title']} - {i['link']}", fg="green"))

        except Exception as e:
            click.echo(click.style(f"Error searching: {e}", fg="red"))
    elif match := re.match(r"play:(.+)", response):
        query = match.group(1)
        click.echo(click.style(f"Playing: {query}...", fg="yellow"))
        try:
            play = get_play(query)
            click.echo(click.style(f"Playing: {play}", fg="green"))
            webbrowser.open(play)
        except Exception as e:
            click.echo(click.style(f"Error playing: {e}", fg="red"))
    elif response == "clear":
        click.echo(click.style("Clearing terminal...", fg="yellow"))
        click.clear()


@click.command()
def cli_buddy():
    click.echo("Terminal Buddy: Hello! How can I help?")
    while True:
        user_input = click.prompt("\nYou")

        promptRes = aiPrompt(user_input)
        response = promptRes.message
        commands = promptRes.commands
        click.echo(f"Terminal Buddy: {response}")
        # print(promptRes)

        for command in commands:
            # print("command", command)
            execute_command(command)
        click.echo()


if __name__ == "__main__":
    cli_buddy()
