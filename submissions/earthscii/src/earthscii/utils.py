"""Utility functions."""
import datetime


def log(msg):
    """Log a message to debug.log."""
    with open("debug.log", "a") as f:
        f.write(f"{datetime.datetime.now()} | {msg}\n")
