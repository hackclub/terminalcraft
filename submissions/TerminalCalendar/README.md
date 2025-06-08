# TerminalCalendar
*An inuitive calendar in your terminal*

## Features
- Add New Events and Reminders to your calendar
- View upcoming events this week, month, year, and all time, sorted by due date.
- Delete and edit events

## Installation
Begin with downloading the repository and unzipping it, and ensure you have python installed.

Enter the repository folder with a terminal and run 

`pip install -r requirements.txt`

This will install all of TerminalCalender's dependencies. (It has a lot, mostly preinstalled python libraries that I don't want to risk removing.)
You may need to use a virtual environment, or if you want to install these packages globally, you may need to use the flag `--break-system-packages`.

Next you can navigate to the directory that you downloaded and run the program with

`python3 calendar.py [ARGUMENTS]` or
`python calendar.py [ARGUMENTS]`

## Arguments
`add` - add an event or reminder to your calendar. 

`show` - view your calendar.

`edit` - edit an event on your calendar.

`about` - get information about the author (me!).

If you ever do something wrong or want to change some data around, all of your events are stored in `data.csv`
