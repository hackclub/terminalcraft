import psutil
import time
import speedtest
from rich.console import Console
from rich.table import Table
from rich.live import Live
import threading
import socket
import sys
import matplotlib.pyplot as plt
import numpy as np


speed_test_results = {
    "Download Speed": "Calculating... Please be patient, this will take ~ 2 epochs to calculate",
    "Upload Speed": "Calculating... Please be patient, this will take ~ 2 epochs to calculate"
}


cpu_usage_data = []
ram_usage_data = []
network_sent_data = []
network_received_data = []
timestamps = []

import random

def get_random_fact():
    facts = [  
        "The first email was sent by Ray Tomlinson to himself in 1971.",  
        "NASA still uses 1970s computers for some space missions due to reliability.",  
        "The first computer virus, 'Creeper', was created in 1971 as an experiment.",  
        "The 'Ctrl+Alt+Del' command was invented by IBM engineer David Bradley.",  
        "The term 'debugging' was popularized by Grace Hopper after removing a moth from a computer.",  
        "Alan Turing is considered the father of modern computing.",  
        "The first hard drive, created by IBM in 1956, could store only 5MB of data.",  
        "The World Wide Web was invented by Tim Berners-Lee in 1989.",  
        "The first domain name ever registered was 'symbolics.com' in 1985.",  
        "The 'USB' was designed to be reversible but was made non-reversible due to cost.",  
        "A single Google search uses more computing power than the Apollo 11 mission.",  
        "There are over 700 programming languages in existence today.",  
        "The first 1GB hard drive, released in 1980, cost $40,000.",  
        "Douglas Engelbart invented the computer mouse in 1964.",  
        "The term 'spam' for unwanted emails comes from a Monty Python sketch.",  
        "Bill Gates wrote his first computer program at the age of 13.",  
        "The first computer game, 'Spacewar!', was created in 1962.",  
        "The floppy disk was invented by IBM in 1967.",  
        "The world's smallest computer is smaller than a grain of rice.",  
        "The term 'robot' comes from the Czech word 'robota', meaning forced labor.",  
        "The first website is still online at info.cern.ch.",  
        "Google's first storage system was built using LEGO bricks.",  
        "The first text message ever sent said 'Merry Christmas' in 1992.",  
        "The first webcam was used to monitor a coffee pot at Cambridge University.",  
        "The first-ever computer algorithm was written before computers existed.",  
        "The first Apple logo featured Isaac Newton sitting under an apple tree.",  
        "The ENIAC computer weighed over 27 tons.",  
        "The concept of artificial intelligence dates back to ancient mythology.",  
        "The first iPhone was released in 2007 and revolutionized smartphones.",  
        "The '@' symbol in email addresses was chosen because it was rarely used.",  
        "IBM's Watson once debated humans in a live debate competition.",  
        "There are more than 4 billion IP addresses in the IPv4 system.",  
        "The first Android phone was released in 2008.",  
        "Google's search index is over 100 million gigabytes in size.",  
        "Bluetooth technology is named after a Viking king, Harald Bluetooth.",  
        "The first-ever tweet was sent by Jack Dorsey in 2006.",  
        "The original PlayStation was a collaboration between Sony and Nintendo.",  
        "The '404 error' code comes from a room at CERN where the web was developed.",  
        "Steve Jobs was fired from Apple in 1985 before returning in 1997.",  
        "Windows XP was so popular that some ATMs still run on it.",  
        "The first YouTube video was uploaded on April 23, 2005.",  
        "The term 'wiki' comes from the Hawaiian word for 'quick'.",  
        "The Raspberry Pi computer was created to teach programming to students.",  
        "The original iPod could hold 1,000 songs.",  
        "The 'Deep Blue' computer defeated world chess champion Garry Kasparov in 1997.",  
        "CAPTCHA tests help digitize old books.",  
        "The first digital camera was created by Kodak in 1975.",  
        "The Facebook 'Like' button was originally supposed to be called 'Awesome'.",  
        "The first animated GIF was created in 1987.",  
        "Quantum computers can perform calculations exponentially faster than classical computers.",  
        "The first CD was pressed in 1982 and contained an album by ABBA.",  
        "Elon Musk founded OpenAI, which developed ChatGPT.",  
        "The first microprocessor was the Intel 4004, released in 1971.",  
        "The Unicode standard includes over 143,000 characters.",  
        "NASA used PowerPoint to present the risks of the Columbia disaster.",  
        "The first Android logo was a green robot inspired by restroom signs.",  
        "The first mobile phone call was made in 1973 by Martin Cooper.",  
        "Microsoft's first-ever product was a BASIC interpreter for the Altair 8800.",  
        "Apple's original iPhone prototype had a physical keyboard.",  
        "The 'Mosaic' web browser helped popularize the internet in the 1990s.",  
        "The term 'phishing' was coined in the 1990s to describe email scams.",  
        "Computer passwords have been around since the 1960s.",  
        "The first Wikipedia article was written in 2001.",  
        "TikTok's algorithm is one of the most advanced recommendation engines ever made.",  
        "The 'Cloud' simply refers to data stored in remote servers.",  
        "The largest data center in the world is in China.",  
        "The first self-replicating computer program was created in 1984.",  
        "Facebook's original name was 'The Facebook'.",  
        "A single quantum bit (qubit) can hold both 0 and 1 simultaneously.",  
        "Twitter was originally called 'Twttr'.",  
        "The first text-based adventure game was 'Colossal Cave Adventure' in 1976.",  
        "IBM's Watson once diagnosed a rare form of leukemia missed by doctors.",  
        "The modern emoji set was first standardized in 2010.",  
        "Tesla cars run on software that can be updated remotely.",  
        "The first email spam message was sent in 1978.",  
        "The world's first SMS-based banking service was launched in 1999.",  
        "Apple's AirDrop uses a combination of Bluetooth and Wi-Fi.",  
        "Google once changed its name to 'Topeka' as an April Fools' joke.",  
        "Netflix originally rented DVDs before switching to streaming.",  
        "The 'Caps Lock' key was originally called 'Shift Lock'.",  
        "The first domain name auction sold 'business.com' for $7.5 million.",  
        "Mark Zuckerberg wore the same gray t-shirt daily to reduce decision fatigue.",  
        "The average smartphone has more processing power than the entire Apollo program.",  
        "The first deepfake video was created in 2017.",  
        "USB stands for 'Universal Serial Bus'.",  
        "The term 'cyberspace' was coined by author William Gibson in 1982.",  
        "Google's first office was in a garage.",  
        "Windows 95 introduced the 'Start' menu.",  
        "Amazon started as an online bookstore.",  
        "The first smartwatch was made in 1972 by Hamilton Watch Company.",  
        "Apple was founded on April 1, 1976.",  
        "The first e-commerce transaction was a sale of marijuana in the 1970s.",  
        "The first Bitcoin transaction was for two pizzas in 2010.",  
        "The floppy disk icon is still used as the save button in software.",  
        "The world's fastest supercomputer can perform over a quintillion calculations per second.",  
        "More than 90% of the world's currency exists only in digital form.",
        "The first computer bug was an actual moth stuck in a relay!",
        "The QWERTY keyboard layout was designed to slow typists down to prevent jamming.",
        "The world's first computer programmer was Ada Lovelace in the 1840s.",
        "The Apollo 11 guidance computer had less processing power than a modern calculator.",
        "The term 'byte' was coined by Werner Buchholz in 1956."
        "75% of these quotes were found by ChatGPT, OpenAI's most popular LLM model!"
    ]  

    return random.choice(facts)

def get_system_stats():
    cpu_usage = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    net_io = psutil.net_io_counters()
    gpu_usage = "N/A (If you see this, you most likely have bad drivers or AMD GPU)"
    
    try:
        import GPUtil
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu_usage = f"{gpus[0].load * 100:.2f} %"
    except ImportError:
        gpu_usage = "GPUtil not installed"
    
    return {
        "CPU Usage": f"{cpu_usage} %",
        "RAM Usage": f"{ram.percent} %",
        "RAM Total": f"{ram.total / (1024 ** 3):.2f} GB",
        "RAM Used": f"{ram.used / (1024 ** 3):.2f} GB",
        "Network Sent": f"{net_io.bytes_sent / (1024 ** 2):.2f} MB",
        "Network Received": f"{net_io.bytes_recv / (1024 ** 2):.2f} MB",
        "GPU Usage": gpu_usage
    }

def run_speed_test():
    st = speedtest.Speedtest(secure=1)
    st.get_best_server() 
    st.download()  
    st.upload()   
    results = st.results.dict()
    return {
        "Download Speed": f"{results['download'] / (1024 ** 2):.2f} Mbps",
        "Upload Speed": f"{results['upload'] / (1024 ** 2):.2f} Mbps"
    }

def run_speed_test_async():
    global speed_test_results
    while True:
        try:
            speed_test_results = run_speed_test()
        except Exception as e:
            speed_test_results = {
                "Download Speed": f"Error: {e}",
                "Upload Speed": f"Error: {e}"
            }
        time.sleep(30)  

def get_system_uptime():
    uptime_seconds = int(time.time() - psutil.boot_time())
    days = uptime_seconds // (24 * 3600)
    uptime_seconds %= (24 * 3600)
    hours = uptime_seconds // 3600
    uptime_seconds %= 3600
    minutes = uptime_seconds // 60
    return f"{days} days, {hours} hours, {minutes} minutes"



def check_ollama_running():
    try:
        host = "localhost"
        port = 11434 
        
        sock = socket.create_connection((host, port), timeout=5)
        sock.close()
        return True
    except (socket.error, socket.timeout) as e:
        print("Ollama service is not running.")
        return False

try:
    import ollama
    ollama_installed = True
except ImportError:
    ollama_installed = False

def analyze_performance(stats):
    if ollama_installed and check_ollama_running():
        prompt = f"""
        Given the following system stats:
        {stats}

        Identify potential performance bottlenecks and suggest optimizations.
        """
        response = ollama.chat(model="llama3.1", messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"]
    else:
        return "Ollama is not installed or the Ollama service is not running. Skipping performance analysis."

shownnumber = 0
print("AI will analyze only only once every eigth iteration")

import requests

def get_weather(api_key, city="New York"):
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={city}"
    try:
        response = requests.get(url)
        response.raise_for_status()  
        data = response.json()
        
        
        weather_description = data["current"]["condition"]["text"]
        temperature = data["current"]["temp_c"]
        humidity = data["current"]["humidity"]
        wind_speed = data["current"]["wind_kph"]
        
        return f"{weather_description}, {temperature}°C, {humidity}% humidity, {wind_speed} kph wind"
    except requests.exceptions.RequestException as e:
        return f"Weather data unavailable: {e}"

def display_dashboard():
    global shownnumber
    console = Console()
    
    
    speed_test_thread = threading.Thread(target=run_speed_test_async, daemon=True)
    speed_test_thread.start()
    
    while True:
        table = Table(title="Real-Time System Monitor")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        stats = get_system_stats()
        stats["System Uptime"] = get_system_uptime()

        if shownnumber % 8 == 0:
            print('ANALYZING VIA AI... Please be patient!')
            analysis = analyze_performance(stats)
            print("AI Insights:", analysis)
            time.sleep(45)
                
        combined_stats = {**stats, **speed_test_results}
        
        for key, value in combined_stats.items():
            table.add_row(key, value)
        
        console.print(table)
        console.print(f"\nFun Fact: {get_random_fact()}")
        weather = get_weather("680ce0f09e454d61aab173209251703", "Ann Arbor")
        console.print(f"Weather: {weather}")
        
        time.sleep(15) 
        console.clear() 
        shownnumber += 1

if __name__ == "__main__":
    display_dashboard()