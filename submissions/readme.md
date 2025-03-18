<h1>Real-Time System Monitoring Dashboard</h1>

<h2>Overview</h2>

This Python script provides a real-time system monitoring dashboard with various system statistics, including CPU, RAM, network usage, GPU utilization, and internet speed. Additionally, it includes fun random tech facts, system uptime tracking, weather information, and an optional AI-powered performance analysis using Ollama.

<h2>Features</h2>

Real-time CPU, RAM, Network, and GPU Monitoring

Speed Test for Internet Connection

System Uptime Tracking

Fun Random Tech Facts Generator

Weather Information Retrieval

AI-Based Performance Analysis (Ollama Integration)

<h2>Dependencies</h2>

Ensure you have the following Python libraries installed before running the script:

pip install psutil speedtest-cli rich GPUtil matplotlib numpy requests

If you want AI-based performance analysis, install Ollama:

pip install ollama

<h2>Usage</h2>

Run the script using:

python script.py and Llama3.1

or run the exe with Ollama running Llama3.1

<h2>System Monitoring</h2>

The dashboard updates in real-time, displaying CPU, RAM, and network statistics.

GPU usage is displayed if GPUtil is installed.

Speed Test

The script performs periodic internet speed tests using the speedtest library.

Download and upload speeds are updated every 30 seconds.

<h2>Weather Information</h2>

The script can fetch weather updates for a specified city.

You need an API key from WeatherAPI and can update the city in the script.

AI-Based Performance Analysis

If Ollama is installed and running, the script will analyze system stats and suggest optimizations.

Ollama listens on port 11434, which should be active for the AI module to work.

<h2>Disclaimers</h2>

If you use an AMD GPU, GPU monitoring might not work correctly.

The script is designed to be run continuously in a terminal window.

Internet speed tests may take a while to compute.

Weather API requires an active internet connection and a valid API key.

<h2>Contributing</h2>

Feel free to modify and enhance this script. Pull requests are welcome!

<h1>PROTECTED BY MIT LICENSE!</h1>
