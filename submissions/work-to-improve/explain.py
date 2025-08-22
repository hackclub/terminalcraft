import datetime


# thx chatgpt
def barGraphRange(numbers, max_bars=8):
    min_val = min(numbers)
    max_val = max(numbers)
    range_size = (max_val - min_val + 1) // max_bars + 1
    # Initialize ranges
    ranges = [[min_val + i * range_size, min_val + (i + 1) * range_size - 1] for i in range(max_bars)]
    ranges[-1] = [ranges[-1][0], max_val]  # Ensure the last range includes the max value
    # Count occurrences in each range
    range_counts = [0] * max_bars
    for num in numbers:
        for i, (start, end) in enumerate(ranges):
            if start <= num <= end:
                range_counts[i] += 1
                break
    return ranges, range_counts


# prints a bar garph in terminal
def barGraph(numbers):
    ranges, range_counts = barGraphRange(numbers)
    total = sum(range_counts)

    for (start, end), count in zip(ranges, range_counts):
        percentage = (count / total) * 100 if total > 0 else 0
        label = f"{round(start)}s-{round(end)}s"
        print(f"{label:10}: {('=' * count * 2):20} ({percentage:.1f}%)")


# prints a vertical bar garph in terminal about timeline
def timelineBarGraph(numbers):
    # get number info
    ranges, range_counts = barGraphRange(numbers)
    #normalize unixtime to time
    for i in range(len(ranges)):
        for j in (0,1):
            ranges[i][j] = datetime.datetime.fromtimestamp(ranges[i][j]).strftime("%H:%M")
    max_count = 10
    total = sum(range_counts)  # Total numbers for percentage calculation

    # print counts to percentages
    for count in range_counts:
        print(f"({((count / total) * 100 if total > 0 else 0):.1f}%)", end="\t")
    print()

    # a 252406230147-252406233252.json
    # Build the graph row by row
    for level in range(max(range_counts), 0, -round(max(range_counts) / max_count)):
        row = ""
        for count in range_counts:
            row += "   #    " if count >= level else " "*8
        print(row)

    # Display the range labels and percentages
    print("   -    " * len(ranges))
    for start, _ in ranges:
        print(f"{start}", end="\t")
    print()
    for _ in ranges:
        print("~", end="\t")
    print()
    for _, end in ranges:
        print(f"{end}", end="\t")
    print()


# explain XD
def explainAnalysis(actionStatistics, active, stops, activeTotle, stopTotle, timeline = None):
    print("\n\nHere is the analysis of all your working habit through your keyboard activities we ever recorded.")
    print("You:")
    print(f"Switches Tab once every {actionStatistics["switchTab"]["onceInAWhile"]} seconds in average")
    print(f"Copies stuff once every {actionStatistics["copy"]["onceInAWhile"]} seconds in average")
    print(f"Pastes stuff once every {actionStatistics["paste"]["onceInAWhile"]} seconds in average")
    print(f"Spends {int(actionStatistics["type"]["timePercentage"] * 100)}% of the time actaully typing stuff")
    print(f"How long do you actually stay active on your work:")
    barGraph(sorted(list(zip(*active))[-1]))
    print(f"How long do you stay unactive everytime you stop:")
    barGraph(sorted(list(zip(*stops))[-1]))
    print(f"You stay active for {int(activeTotle / (activeTotle + stopTotle) * 100)}% of the time")
    print(f"And you stay unactive for {int(stopTotle / (activeTotle + stopTotle) * 100)}% of the time.")
    if timeline:
        print("The timeline of your productivity during this session: ")
        timelineBarGraph(timeline)
    else:
        print("Because you are analysis all sessions avalible its meaningless to analysis your timeline, try analysis a certain session!")
    input("Enter to continue: ")
