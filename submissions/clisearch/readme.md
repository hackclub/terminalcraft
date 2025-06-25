# clisearch

## What is it? 
- Cli search is a tool made to make it faster to search stuff when already inside the terminal, it uses duck duck go bangs to easily navigate to wherever you want to be without all the extra clicks

## What are duck duck go bangs?
- Bangs are a feature in the duck duck go browser that let you add shortcuts to your search query to open the website you actually want to search on faster, for example:

Adding !gh to your search query would take you to https://github.com/search?q=(your-query-here)&type=repositories removing all the extra time it would take to use your search engine

## How to use
- To search run `search [query]`, by default this will take you to googles search engine
- To use bangs, first learn a couple from https://duckduckgo.com/bangs, some useful ones are shown at the bottom of this readme, bangs can then be added on by using !(bang choice)
- Bang example: `search !yt [query]`, this takes you to youtube.com and searches for a video with your query
- To change your default bang use `search --default "yt"` where `yt` is the bang of your choice
- History can be viewed in your home user folder inside of `.clisearch/history.json`

## How to install
### Option 1, pip
- package is available on pypi, to download simply run `pip install clisearch` and your done!

### Option 2, compiling
- The package can also be compiled in case you want anything edited or want to contribute to the repository
1. Clone the repository with `git clone https://github.com/cloudyio/clisearch`
2. Navigate to new folder
3. Run `pip install -r requirements.txt` to install the `click` package
4. Run `pip install .` in your command line
5. Package is now compiled!

## Some useful Bangs:
- gh: github.com
- yt: youtube.com
- g: google.com
- x: x.com (previously twitter)
- w: wikipedia.com
- a: amazon.com
There are thousands of bangs, you can find your own here: https://duckduckgo.com/bangs
