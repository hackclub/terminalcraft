#!/usr/bin/python3

import click
from inquirer import *
import datetime

version = "0.1.0"

@click.group("calendar")
@click.version_option(version, prog_name="TerminalCalender")
def calendar():
    pass

@calendar.command()
def show():
    """Show your calendar."""

    termQuestion = [List(
        "term",
        message="How far do you want to see?",
        choices=["Today", "This Week", "This Month", "This Year", "All"],
    )]

    term = prompt(termQuestion)["term"]

    file = open("data.csv", "r")
    lines = file.read().splitlines()
    entries = []

    for i in lines[1:]:
        words = i.split()
        newEntry = {"name": words[1].removesuffix(","), "date": int(words[2].removesuffix(",")), "start": int(words[3].removesuffix(",")), "end": int(words[4].removesuffix(","))}
        entries.append(newEntry)

    entries = sorted(entries, key=lambda e: (e["date"], e["start"], e["end"]))

    if term == "All":
        pass
    else:
        date = datetime.datetime.now()
        year = date.year
        month = date.month
        week = date.strftime("%W")
        day = date.day

        newEntries = []

        for i in entries:
            if term == "This Year":
                if int(str(i["date"])[0:4]) == int(year):
                    newEntries.append(i)
            elif term == "This Month":
                if int(str(i["date"])[4:6]) == int(month):
                    newEntries.append(i)
            elif term == "This Week":
                entryDate = datetime.datetime(int(str(i["date"])[0:4]), int(str(i["date"])[4:6]), int(str(i["date"])[6:8]))
                entryWeek = entryDate.strftime("%W")
                if entryWeek == week:
                    newEntries.append(i)
            elif term == "Today":
                currentDate = int(date.strftime("%Y%m%d"))
                if currentDate == int(i["date"]):
                    newEntries.append(i)
        entries = newEntries

    for i in entries:
        finalDate = ""
        finalDate += str(i["date"])[0:4] + "-" + str(i["date"])[4:6] + "-" + str(i["date"])[6:8]

        startTime = ""
        startTime += str(i["start"])[0:2] + ":" + str(i["start"])[2:4]

        endTime = ""
        endTime += str(i["end"])[0:2] + ":" + str(i["end"])[2:4]

        click.echo(f'{i["name"]}, on {finalDate} from {startTime} to {endTime}.')

    file.close()

@calendar.command()
def add():
    """Add an event to your calendar."""
    typeQuestion = [List(
            "type",
            message="What type of event?",
            choices=["Reminder", "Event"]
        )]
    event = [
        Text(
            "name",
            message="What is the event?",
        ),
        Text(
            "date",
            message="What is the date? [YYYY-MM-DD]",
        ),
        Text(
            "start",
            message="What is the start time? (24-hour) [HH:MM]",
        ),
        Text(
            "end",
            message="What is the end time? (24-hour) [HH:MM]",
        )
    ]

    reminder = [
        Text(
            "name",
            message="What is the event?",
        ),
        Text(
            "date",
            message="What is the date? [YYYY-MM-DD]",
        ),
        Text(
            "time",
            message="What time? (24-hour) [HH:MM]",
        ),
    ]

    type = prompt(typeQuestion)["type"]

    file = open("data.csv", "a")

    if type == "Reminder":
        reminder = prompt(reminder)
        file.write(f'reminder, {reminder["name"]}, {reminder["date"].replace("-", "")}, {reminder["time"].replace(":", "")}, \n')
    elif type == "Event":
        event = prompt(event)
        file.write(f'event, {event["name"]}, {event["date"].replace("-", "")}, {event["start"].replace(":", "")}, {event["end"].replace(":", "")}\n')
    file.close()

@calendar.command()
def about():
    """About the app."""

    click.echo("TerminalCalender was created using click by Owen Schmidt, 2025, for Hackclub's TerminalCraft program.")

@calendar.command()
def edit():
    """Edit your calendar."""
    file = open("data.csv", "r")
    lines = file.read().splitlines()

    entries = []

    for i in lines[1:]:
        words = i.split()
        newEntry = {"type": words[0], "name": words[1].removesuffix(","), "date": int(words[2].removesuffix(",")), "start": int(words[3].removesuffix(",")), "end": int(words[4].removesuffix(","))}
        entries.append(newEntry)

    entries = sorted(entries, key=lambda e: (e["date"], e["start"], e["end"]))

    events = []

    for i in entries:
        finalDate = ""
        finalDate += str(i["date"])[0:4] + "-" + str(i["date"])[4:6] + "-" + str(i["date"])[6:8]

        startTime = ""
        startTime += str(i["start"])[0:2] + ":" + str(i["start"])[2:4]

        endTime = ""
        endTime += str(i["end"])[0:2] + ":" + str(i["end"])[2:4]

        events.append(f'{i["name"]}, on {finalDate} from {startTime} to {endTime}.')

    eventQuestion = [List(
        "event",
        message="Pick an event to edit.",
        choices=events
    )]

    answer = prompt(eventQuestion)["event"]

    index = events.index(answer)

    questions = [
        List(
            "field",
            message="What field do you want to edit?",
            choices=["Name", "Date", "Start", "End"]
        ),
        Text(
            "newValue",
            message="What is the new value? Date: [YYYY-MM-DD], Time: (24 Hour)[HH:MM]",
        )
    ]

    answers = prompt(questions)
    try:
        if answers["field"] == "Name":
            entries[index]["name"] = str(answers["newValue"])
        elif answers["field"] == "Date":
            entries[index]["date"] = str(answers["newValue"].replace("-", ""))
        elif answers["field"] == "Start":
            entries[index]["start"] = str(answers["newValue"].replace(":", ""))
        elif answers["field"] == "End":
            entries[index]["end"] = str(answers["newValue"].replace(":", ""))
    except KeyError:
        click.secho("Sorry, something went wrong.", fg="red")

    file = open("data.csv", "w")
    newText = "Type, Name, Date, Start, End\n"
    for i in entries:
        newText += f"{i['type']}, {i['name']}, {i['date']}, {i['start']}, {i['end']}\n"

    file.write(newText)
    file.close()

if __name__ == "__main__":
    calendar()
