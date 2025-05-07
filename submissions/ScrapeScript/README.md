# ScrapeScript
This terminal program allows for the web scraping of most structured websites for data and the ability to that data into an Excel document for further analysis.

## Time
I used Pycharm to make this and didn't have a time extension, however I'd estimate ~9 hrs because ths was my first time working with OpenPyXL and Pandas

## Features
- Scraping capability for most sites with efficiently formatted data
- Choice of scrape data from HTML tags and classes
- Support for uploading scraped data to Excel for independent analysis
- Creation of organized Excel documents


## Libraries
Before utilizing this program, please install the following libraries with the following command:
##### pip install requests bs4 openpyxl pandas

## Installation

1. Ensure libraries and Python are installed.
2. Clone this repository.
3. Run the project in your terminal using python.

## Usage
In order to use this program, here is an example set of inputs using a sample scrape site. For testing, I recommend either another scrape test site or a wikipedia list. Here is a set of demo inputs for the program using a practice scrape website and 3 different HTML classes to be scraped:
##### Enter the website URL: https://www.scrapethissite.com/pages/forms/
##### Enter HTML tags you're looking for separated by spaces (one tag for each selection of data you want: td td td
##### Enter the HTML classes you are looking for, again in order and one per selection. If none, type "N": name year wins
##### Enter your Excel document's name: Hockey Teams
##### Enter the title of each Excel column separated by commas: Team Name,Year,Wins
####
This set of inputs will lead to the creation of an excel document that looks like this:
![Image of Excel spreadsheet with 3 columns of information: one titled "Team Name" with every team name from the page, and so on]
##### ![Screenshot 2025-03-18 180342](https://github.com/user-attachments/assets/b1743e1c-5761-4811-a4f5-533a54021a2c)
####
All you need to do is enter the tags and elements in order (i.e. first tag and first element are for the same data, second with second, and so forth).

## Other
If you have any suggestions, bug reports, or anything of the like, feel free to let me know!
