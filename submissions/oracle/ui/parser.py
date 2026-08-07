"""
This module is responsible for parsing commands entered by the user.
"""
class Parser:
    """Handles parsing user input."""
    def __init__(self):
        self.command_map = {
            'quit': 'quit', 'exit': 'quit', 'q': 'quit',
            'advance': 'advance', 'adv': 'advance', 'next': 'advance',
            'view': 'view', 'v': 'view', 'status': 'view', 'see': 'view', 'show': 'view',
            'predict': 'predict', 'p': 'predict', 'ask': 'predict',
            'influence': 'influence', 'i': 'influence', 'exert': 'influence',
            'rewrite': 'rewrite', 'r': 'rewrite', 'change': 'rewrite',
            'save': 'save',
            'load': 'load',
            'ally': 'ally',
            'rival': 'rival',
            'wonder': 'wonder',
            'recruit': 'recruit'
        }
    def parse_command(self, input_str):
        """Parses a complex command with arguments from the user."""
        parts = input_str.strip().lower().split()
        if not parts:
            return None, []
        command = parts[0]
        args = parts[1:]
        command = self.command_map.get(command, command)
        return command, args