# reddit-cli-browser
A command-line interface (CLI) tool to browse Reddit, built with Python using [praw](https://github.com/praw-dev/praw)!
## Features
- Browse Subreddits
- Search Subreddits
- Add and browse favourite Subreddits
- View saved posts
## Installation
1. Clone the repository  
  ```git clone https://github.com/bojanradjenovic/reddit-cli-browser.git```
2. Navigate to the repository directory  
   ```cd reddit-cli-browser```
3. Make a virtual environment (recommended)
4. Install the required dependencies  
   ```pip install -r requirements.txt```
6. Fill out configuration file (rename to config.json afterwards)
7. Run ```main.py```!

## Reddit API Credentials
Go [here](https://www.reddit.com/prefs/apps) to generate your own API credentials (select ```script``` and set redirect uri to ```http://localhost```).  

For the user agent, I recommend filling something out like ```linux:reddit-cli-browser:1.0 (by u/YourUsername)```.
