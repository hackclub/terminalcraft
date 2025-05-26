# VoiceConn Documentation

## Overview

VoiceConn is a project that enables communication using voice through socket connections. This trial version, hosted on an Azure Virtual Machine, supports small talks and multiple user IDs.
Tested only on windows 10, python 3.9 client and Windows 10 azure vm pyhton 3.9.

## Prerequisites

- Python 3.9
- Do not use python version below 3.9 . Pyaudio module will not work.

## Setup

### Server Setup

1. Host a virtual machine or create a server.
2. Run `s1.py` on the server.

### Client Setup

1. Copy the public IP of the virtual machine.
2. Paste it in `c1.py` at the host IP.
3. Create a virtual environment.

## Running the Program


1. Execute `c1.py`.

```python c1.py <server_ip>```

For example:

```python c1.py 192.168.1.100```

2. Enter your name when prompted.

Both parties must run the client program to start communication.

## Repository Structure

- `README.md`: Project overview and setup instructions.
- `c1.py`: Client-side script for communication.
- `s1.py`: Server-side script to handle connections.


## Features

- Voice communication via socket connections.
- Supports multiple user IDs.
- Easy setup on an Azure VM.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## Installing Required Modules

Run

### `pip install -r requirements.txt`


