from textual.app import App
from textual.widgets import Button, Static
from textual.containers import Vertical, Horizontal
from MandelbrotWindow import Mandelbrot

class Main(App):
    CSS_PATH = "Styling.tcss"

    def compose(self):
        yield Vertical(
            Static("Mandelbrot Synthesizer", id="header"),
            Horizontal(
                Vertical(
                    Button("🌌", classes="sidebar"),
                    id="sidecontainer"
                ),
                Mandelbrot(),
            )
        )

    def on_mount(self):
        header = self.query_one(Static)
        header.styles.content_align_horizontal = "center"
        header.styles.content_align_vertical = "top"
