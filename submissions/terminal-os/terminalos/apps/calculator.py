"""Calculator application."""

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Header, Footer, Button, Static
from textual.containers import Grid, Vertical
from textual.binding import Binding


class CalculatorApp(Screen):
    """Calculator application."""
    
    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("c", "clear", "Clear"),
    ]
    
    def __init__(self):
        super().__init__()
        self.display = "0"
        self.reset_on_next = False
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Static(self.display, id="display", classes="calc-display"),
            Grid(
                Button("C", id="clear", classes="calc-btn"),
                Button("±", id="negate", classes="calc-btn"),
                Button("%", id="percent", classes="calc-btn"),
                Button("÷", id="divide", classes="calc-btn"),
                
                Button("7", id="seven", classes="calc-btn"),
                Button("8", id="eight", classes="calc-btn"),
                Button("9", id="nine", classes="calc-btn"),
                Button("×", id="multiply", classes="calc-btn"),
                
                Button("4", id="four", classes="calc-btn"),
                Button("5", id="five", classes="calc-btn"),
                Button("6", id="six", classes="calc-btn"),
                Button("-", id="subtract", classes="calc-btn"),
                
                Button("1", id="one", classes="calc-btn"),
                Button("2", id="two", classes="calc-btn"),
                Button("3", id="three", classes="calc-btn"),
                Button("+", id="add", classes="calc-btn"),
                
                Button("0", id="zero", classes="calc-btn"),
                Button(".", id="decimal", classes="calc-btn"),
                Button("=", id="equals", classes="calc-btn"),
                Button("⌫", id="backspace", classes="calc-btn"),
                
                classes="calc-grid"
            ),
            classes="calculator"
        )
        yield Footer()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        button_id = event.button.id
        
        if button_id in ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]:
            self.input_digit(button_id)
        elif button_id == "clear":
            self.clear_display()
        elif button_id == "equals":
            self.calculate()
        
        self.update_display()
    
    def input_digit(self, digit_id: str) -> None:
        """Input a digit."""
        digit_map = {
            "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
            "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9"
        }
        
        digit = digit_map[digit_id]
        if self.display == "0" or self.reset_on_next:
            self.display = digit
            self.reset_on_next = False
        else:
            self.display += digit
    
    def clear_display(self) -> None:
        """Clear the display."""
        self.display = "0"
        self.reset_on_next = False
    
    def calculate(self) -> None:
        """Perform calculation."""
        try:
            # Simple calculation (in production, use proper parser)
            result = eval(self.display.replace("×", "*").replace("÷", "/"))
            self.display = str(result)
            self.reset_on_next = True
        except:
            self.display = "Error"
            self.reset_on_next = True
    
    def update_display(self) -> None:
        """Update the display."""
        self.query_one("#display").update(self.display)
    
    def action_close(self) -> None:
        """Close calculator."""
        self.dismiss()
    
    def action_clear(self) -> None:
        """Clear via keyboard."""
        self.clear_display()
        self.update_display()