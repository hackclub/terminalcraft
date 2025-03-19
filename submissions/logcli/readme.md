# logcli - Flight Data Logger CLI

`logcli` is a command-line interface (CLI) tool for managing flight log data. It provides an easy way to upload, retrieve, and manage flight logs through a simple command-line interface.

## 🚀 Features

- **User Authentication**: Login and logout functionality.
- **Log Uploading**: Upload flight log files with optional metadata.
- **Log Management**: View and download flight logs.

## 📥 Installation

You can install `logcli` from PyPI using pip:

```sh
pip install logcli
```

## 📌 Commands & Usage

### 🔐 Authentication

#### Login
Authenticate a user into the system.
```sh
logcli login <email> <password>
```

#### Logout
Sign out the current user.
```sh
logcli logout
```

### 📤 Uploading Logs

#### Upload Flight Log
Upload a flight log file to the system with optional metadata.
```sh
logcli upload <file_path> [--metadata <metadata>]
```

### 📁 Managing Logs

#### View All Logs
Retrieve and display all flight logs associated with the user.
```sh
logcli logs
```

#### View Specific Log
Display detailed information about a specific flight log.
```sh
logcli view-log <log_id>
```

#### Download Log
Download a specific flight log file to a designated location.
```sh
logcli download-log <log_id> <output_path>
```

## 🎯 Example Usage

```sh
# Login
logcli login user@example.com password123

# Upload a flight log
logcli upload flight1.bin --metadata "Test Flight"

# List all logs
logcli logs

# View a specific log
logcli view-log 12345

# Download a log
logcli download-log 12345 ./downloads/

# Logout
logcli logout
```

## 📂 Sample Binary File

For testing, you can use the following sample binary flight log file:
[Download Sample Flight Log](https://hc-cdn.hel1.your-objectstorage.com/s/v3/b6a3656cae558c78201570a9edcc97646c7bfc19_sample.bin)

## 🛠 Contributing
Feel free to contribute! Fork the repository, make changes, and submit a pull request.
