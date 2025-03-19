from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Label, Button

class MyScroll(VerticalScroll):
    DEFAULT_CSS = """
    MyScroll {
        overflow-y: scroll;
        max-height: 10;
    }
        """
    def __init__(self, data):
        super().__init__()
        self.data = data

    def on_mount(self):
        self.build()

    def build(self):
        self.remove_children()  # Remove existing content
        for key, value in self.data.items():
            self.mount(Label(f"{key}: {value}"))  # Add new content

    def update_data(self, key, value):
        self.data[key] = value
        self.build()
        self.refresh()  # Force a re-render

class MyApp(App):
    def compose(self) -> ComposeResult:
        self.data = {"Item 1": "Value 1", "Item 2": "Value 2"}
        self.scroll = MyScroll(self.data)
        yield self.scroll
        yield Button("Update Data", id="update")

    def on_button_pressed(self, event):
        if event.button.id == "update":
            count = len(self.data) + 1
            self.scroll.update_data(f"Item {count}", f"Value {count}")

app = MyApp()
app.run()
