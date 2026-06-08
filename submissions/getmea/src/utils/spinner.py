# Note: From another not yet public project of mine

import itertools
import threading
import time
import sys


class Spinner:
    """A simple terminal spinner class with start and stop controls."""

    def __init__(self, message="Working...", delay=0.1):
        """Initialize the spinner.

        Args:
            message (str, optional): The message to display next to the spinner. Defaults to "Working...".
            delay (float, optional): The delay between spinner updates in seconds. Defaults to 0.1.
        """
        self.spinner = itertools.cycle(["-", "\\", "|", "/"])
        self.delay = delay
        self.message = message
        self.running = False
        self.spinner_thread = None

    def spin(self):
        """Spin the spinner until self.running is set to False."""
        while self.running:
            sys.stderr.write(f"\r{next(self.spinner)} {self.message}")
            sys.stderr.flush()
            time.sleep(self.delay)
            sys.stderr.write("\r\033[K")  # Clear the line

    def start(self):
        """Start the spinner in a separate thread."""
        if not self.running:
            self.running = True
            self.spinner_thread = threading.Thread(target=self.spin)
            self.spinner_thread.daemon = True
            self.spinner_thread.start()

    def stop(self):
        """Stop the spinner and clear the line."""
        if self.running:
            self.running = False
            self.spinner_thread.join()
            sys.stderr.write("\r\033[K")  # Clear the line
            sys.stderr.flush()


spinner = Spinner(message="Thinking...", delay=0.1)
