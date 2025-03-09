from expense_tracker.screens import MainScreen
from textual.app import App

class ExpenseTrackerApp(App):
    CSS = """
    Screen {
        layout: horizontal;
    }
    #left_pane {
        width: 50%;
        height: 100%;
        layout: vertical;
        padding: 1;
    }
    #right_pane {
        width: 50%;
        height: 100%;
        layout: vertical;
        border: solid green;
        padding: 1;
    }
    .hidden {
        display: none;
    }
    #expense_form {
        height: 30%;
        layout: vertical;
    }
    #edit_form {
        height: 20%;
        layout: vertical;
    }
    #report_area {
        height: 90%;
        overflow-y: auto;
    }
    #right_pane_header {
        height: 5%;
        layout: horizontal;
        align: center middle;
    }
    #close_report {
        width: 10%;
        height: 100%;
        align: right middle;
    }
    #global_currency {
        width: 90%;
        height: 100%;
        margin-right: 1;
    }
    #control_buttons {
        height: 10%;
        layout: horizontal;
    }
    """

    def on_mount(self):
        self.push_screen(MainScreen())

def run_expense_tracker():
    """Entry point function to run the ExpenseTrackerApp."""
    app = ExpenseTrackerApp()
    app.run()

if __name__ == "__main__":
    run_expense_tracker()