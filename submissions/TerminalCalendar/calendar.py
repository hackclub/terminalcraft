#!/usr/bin/python3
import json
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

    with open("data.json", "r") as file:
        entries = json.load(file)

    entries = sorted(entries, key=lambda e: (e["date"]["year"], e["date"]["month"], e["date"]["day"], e["start"], e["end"]))

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
                if int(i["date"]["year"]) == int(year):
                    newEntries.append(i)
            elif term == "This Month":
                if int(i["date"]["month"]) == int(month):
                    newEntries.append(i)
            elif term == "This Week":
                entryDate = datetime.datetime(int(i["date"]["year"]), int(i["date"]["month"]), int(i["date"]["day"]))
                entryWeek = entryDate.strftime("%W")
                if entryWeek == week:
                    newEntries.append(i)
            elif term == "Today":
                if date.day == int(i["date"]["day"]) and date.month == int(i["date"]["month"]) and date.year == int(i["date"]["year"]):
                    newEntries.append(i)
        entries = newEntries

    for i in entries:
        click.echo(f'{i["name"]}, on {i["date"]["month"]}-{i["date"]["day"]}-{i["date"]["year"]} from {str(i["start"])[0:2]}:{str(i["start"])[2:4]} to {str(i["end"])[0:2]}:{str(i["end"])[2:4]}.', nl=False)
        click.secho(" ("+i["tag"]["name"] + ")", fg=i["tag"]["color"])

@calendar.command()
def add():
    """Add an event to your calendar."""

    with open("tags.json", "r") as file:
        tags = json.load(file)

    tagNames = []
    for i in tags:
        tagNames.append(i["name"])

    event = [
        Text(
            "name",
            message="What is the event?",
        ),
        Text(
            "date",
            message="What is the date? [MM-DD-YYYY]",
        ),
        Text(
            "start",
            message="What is the start time? (24-hour) [HH:MM]",
        ),
        Text(
            "end",
            message="What is the end time? (24-hour) [HH:MM]",
        ),
        List(
            "tag",
            message="What is the tag?",
            choices=tagNames,
        )
    ]

    event = prompt(event)

    tag = tags[tagNames.index(event["tag"])]

    with open("data.json", "r") as file:
        entries = json.load(file)

    date = event["date"].split("-")
    start = event["start"].split(":")
    end = event["end"].split(":")

    entries.append({
        "name": event["name"],
        "date": {
            "year": int(date[2]),
            "month":int(date[0]),
            "day": int(date[1]),
        },
        "start": int(start[0] + start[1]),
        "end": int(end[0] + end[1]),
        "tag": tag,
    })

    with open("data.json", "w") as file:
        json.dump(entries, file)

@calendar.command()
def about():
    """About the app."""

    click.echo("TerminalCalender was created using click by Owen Schmidt, 2025, for Hackclub's TerminalCraft program.")

@calendar.command()
def tags():
    """Create new tags."""
    colors = [
        "red",
        "orange",
        "yellow",
        "green",
        "blue",
        "purple",
        "cyan",
        "pink",
        "grey",
        "white",
    ]

    questions = [
        Text(
            "name",
            message="What is the tag?",
        ),
        List(
            "color",
            message="What is the color?",
            choices=colors,
        )
    ]

    answers = prompt(questions)

    with open("tags.json", "r") as file:
        tags = json.load(file)

    tags.append({
        "name": answers["name"],
        "color": answers["color"],
    })

    with open("tags.json", "w") as file:
        json.dump(tags, file)

@calendar.command()
def edit():
    """Edit your calendar."""
    with open("data.json", "r") as file:
        entries = json.load(file)

    entries = sorted(entries, key=lambda e: (e["date"]["year"], e["date"]["month"], e["date"]["day"], e["start"], e["end"]))

    events = []

    for i in entries:
        events.append(f'{i["name"]}, on {i["date"]["month"]}-{i["date"]["day"]}-{i["date"]["year"]} from {str(i["start"])[-4:-2]}:{str(i["start"])[-2]}{str(i["start"])[-1]} to {str(i["end"])[-4:-2]}:{str(i["end"])[-2]}{str(i["end"])[-1]}.')

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
            date = answers["newValue"].split("-")
            entries[index]["date"]["year"] = int(date[2])
            entries[index]["date"]["month"] = int(date[0])
            entries[index]["date"]["day"] = int(date[1])
        elif answers["field"] == "Start":
            start = answers["newValue"].split(":")
            entries[index]["start"] = int(start[0] + start[1])
        elif answers["field"] == "End":
            end = answers["newValue"].split(":")
            entries[index]["end"] = int(end[0] + end[1])
    except KeyError:
        click.echo("Sorry, something went wrong.", fg="red")

    with open("data.json", "w") as file:
        json.dump(entries, file)

@calendar.command()
def viewTags():
    """View by tag."""

    with open("tags.json", "r") as file:
        tags = json.load(file)

    tagNames = []
    for i in tags:
        tagNames.append(i["name"])

    tagQuestion = [List(
        "tag",
        message="What tag do you want to view?",
        choices=tagNames,
    )]

    tag = prompt(tagQuestion)["tag"]

    with open("data.json", "r") as file:
        entries = json.load(file)

    entries = sorted(entries,
                     key=lambda e: (e["date"]["year"], e["date"]["month"], e["date"]["day"], e["start"], e["end"]))

    date = datetime.datetime.now()
    year = date.year
    month = date.month
    week = date.strftime("%W")
    day = date.day

    newEntries = []

    for i in entries:
        if i["tag"]["name"] == tag:
            newEntries.append(i)
    entries = newEntries

    for i in entries:
        click.echo(
            f'{i["name"]}, on {i["date"]["month"]}-{i["date"]["day"]}-{i["date"]["year"]} from {str(i["start"])[0:2]}:{str(i["start"])[2:4]} to {str(i["end"])[0:2]}:{str(i["end"])[2:4]}.')

if __name__ == "__main__":
    calendar()
