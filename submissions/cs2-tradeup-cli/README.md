# CS2 tradeup cli
 A CLI interface for calculating the results and chances of a CS2 traedup - written in python using curses

## How to run
install numpy and scikit using `pip install numpy scikit-learn`

### Note for windows
if running on windows install `windows-curses` using `pip install windows-curses` (this isnt required on linux as curses works natively)

If running on windows 11 this program works a lot better in the legacy command prompt. You can assess this by searching for `conhost` in windows search - it *works* on the usual terminal but the colours will be a bit messed up.
(this does not apply for windows 10)


## Usage
Use tab/shift-tab to select the item, and use the up/down arrow keys to select options with the item.
Press enter to select an option and edit it

### Searching for items
Press enter on the item name to edit it, then start typing the skin name to find the skin you are looking for.You should see a drop down pop up which will contain items you may be looking for. You can select these using the arrow keys and press enter to select that search result. If you are typing and press enter the top result will be automatically selected if there is one.

### Changing the float
Select the float and press enter, then choose your new float value and press enter again.

## Abbreviations:
Abbreviated values are used for the exterior values: FN, MW, FT, WW, BS correspond to Factory New, Medium Wear, Field Tested, Well Worn and Battle scarred respectively