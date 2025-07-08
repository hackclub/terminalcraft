# Meet-Zone User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Managing Participants](#managing-participants)
3. [Finding Meeting Times](#finding-meeting-times)
4. [Understanding Results](#understanding-results)
5. [Tips and Best Practices](#tips-and-best-practices)
6. [Troubleshooting](#troubleshooting)

## Getting Started

### Installation

1. Download the appropriate executable for your operating system from the [Releases page](https://github.com/yourusername/meet-zone/releases)
2. Make the file executable (macOS/Linux only):
   ```bash
   chmod +x meet-zone-macos-1.0.2
   ```
3. Run the application:
   ```bash
   # Windows
   .\meet-zone-windows-1.0.2.exe
   
   # macOS
   ./meet-zone-macos-1.0.2
   
   # Linux
   ./meet-zone-linux-1.0.2
   ```

### First Launch

When you first launch Meet-Zone, you'll see a tabbed interface with two main sections:
- **Participants**: Manage team members and their availability
- **Meeting Times**: Configure search parameters and view results

## Managing Participants

### Adding Participants

1. Go to the **Participants** tab
2. Fill in the participant details:
   - **Name**: The person's name or identifier
   - **Time Zone**: Select from the comprehensive timezone list
   - **Start Time**: When they typically start work (24-hour format, e.g., 09:00)
   - **End Time**: When they typically end work (24-hour format, e.g., 17:00)
3. Click **Add Participant**

### Importing from CSV

You can also load participants from a CSV file:

```bash
# Command line usage
./meet-zone-macos-1.0.2 roster.csv
```

CSV format:
```csv
name,timezone,start_time,end_time
Alice,America/New_York,09:00,17:00
Bob,Europe/London,08:30,16:30
Charlie,Asia/Tokyo,10:00,18:00
```

### Managing Participants

- **Remove Selected**: Click on a participant in the table, then click "Remove Selected"
- **Clear All**: Remove all participants at once

## Finding Meeting Times

### Basic Configuration

1. Go to the **Meeting Times** tab
2. Configure your search parameters:
   - **Min Duration**: Minimum meeting length in minutes (default: 30)
   - **Top Results**: How many options to show (default: 3)
   - **Show Full Week**: Search entire week vs. just today
   - **Prioritize By**: Focus on maximizing participants or meeting duration
   - **Start Date**: When to begin the search (default: today)

3. Click **Find Meeting Times**

### Advanced Options

#### Prioritization Strategies

- **Participants**: Prioritizes slots with more people available
- **Duration**: Prioritizes longer available time slots

#### Time Range Options

- **Today Only**: Find slots for today only
- **Full Week**: Search across the next 7 days for more options

## Understanding Results

### Result Columns

- **Start (UTC)**: Meeting start time in UTC
- **End (UTC)**: Meeting end time in UTC  
- **Duration**: How long the meeting slot is
- **Count**: Number of participants available (e.g., "3/5" means 3 out of 5 total)
- **Score**: Quality score as a percentage (higher is better)
- **Names**: List of available participants

### Interpreting Scores

The score considers multiple factors:
- **Participant availability**: More people = higher score
- **Meeting duration**: Longer slots = higher score (up to a point)
- **Day preference**: Earlier days in the week = slightly higher score

A score of 80%+ indicates an excellent meeting slot.

## Tips and Best Practices

### Getting Better Results

1. **Add more participants**: More data points lead to better optimization
2. **Use realistic working hours**: Don't extend hours beyond what's practical
3. **Consider time zones carefully**: Double-check timezone selections
4. **Try different prioritization**: Switch between "participants" and "duration" modes

### Working with Global Teams

1. **Use full week search**: Gives more flexibility across time zones
2. **Consider rotating meeting times**: Fair for all time zones over time
3. **Account for daylight saving**: Be aware of DST transitions
4. **Plan ahead**: Some combinations work better on certain days

### CSV File Tips

1. **Use standard timezone names**: Like "America/New_York", not "EST"
2. **24-hour format**: Use 09:00, not 9:00 AM
3. **Consistent formatting**: Keep the same format throughout
4. **Test with small files**: Verify format before adding many participants

## Troubleshooting

### Common Issues

#### "No slots found"
- **Cause**: No overlapping availability
- **Solution**: Try longer time range, adjust working hours, or reduce minimum duration

#### Application won't start
- **Check**: Look for `meet-zone-debug.log` in the same directory
- **Run from terminal**: See error messages directly
- **Verify permissions**: Ensure executable permissions on macOS/Linux

#### Incorrect time zones
- **Use standard names**: Like "Europe/London", not "GMT"
- **Check spelling**: Timezone names are case-sensitive
- **Refer to list**: Use the dropdown in the app for valid options

#### CSV import fails
- **Check format**: Ensure exactly 4 columns: name,timezone,start_time,end_time
- **Verify times**: Use HH:MM format (e.g., 09:00, not 9:00)
- **Check encoding**: Save CSV as UTF-8

### Getting Help

1. **Check debug logs**: `meet-zone-debug.log` contains detailed information
2. **Run from command line**: Shows real-time error messages
3. **Open an issue**: Report bugs on GitHub with:
   - Your operating system
   - Contents of debug log
   - Steps to reproduce the problem

### Performance Tips

- **Limit participants**: 20+ participants may slow down calculations
- **Reduce time range**: Full week searches take longer than single day
- **Close other apps**: Free up system resources for better performance

## Command Line Usage

Meet-Zone also supports command-line usage for automation:

```bash
# Basic usage with CSV file
./meet-zone roster.csv

# Specify minimum duration
./meet-zone roster.csv --duration 45

# Show top 5 results
./meet-zone roster.csv --top 5

# Search full week
./meet-zone roster.csv --week

# Prioritize by duration instead of participants
./meet-zone roster.csv --prioritize duration

# Specify start date
./meet-zone roster.csv --date 2023-12-01

# Combine options
./meet-zone roster.csv --duration 60 --top 10 --week --prioritize duration
```

---

For more information, see the [README.md](README.md) or visit the [GitHub repository](https://github.com/yourusername/meet-zone).