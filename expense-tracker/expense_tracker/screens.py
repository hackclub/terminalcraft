from textual.screen import Screen
from textual.widgets import Footer, Header, Static, Select, Button, Input
from textual.containers import Container, Vertical
from expense_tracker.widgets import ExpenseForm, ReportView
from expense_tracker.data import ExpenseManager
from expense_tracker.currency import CurrencyConverter
from textual.app import ComposeResult

class MainScreen(Screen):
    def __init__(self):
        super().__init__()
        self.manager = ExpenseManager()
        self.converter = CurrencyConverter()
        self.global_currency = "USD"
        self.editing_index = None
        self.report_visible = False

    def compose(self) -> ComposeResult:
        # Left pane for input and controls
        with Container(id="left_pane"):
            yield Header()
            yield ExpenseForm(id="expense_form")
            with Vertical():
                with Container(id="control_buttons"):
                    yield Button("Monthly Report", id="monthly")
                    yield Button("Yearly Report", id="yearly")
            # Edit form (hidden by default)
            with Vertical(id="edit_form", classes="hidden"):
                yield Input(id="edit_amount", placeholder="Edit Amount")
                yield Input(id="edit_description", placeholder="Edit Description")
                yield Select(id="edit_category", options=[(c, c) for c in self.manager.categories], value="Miscellaneous")
                yield Button("Save Edit", id="save_edit")
            yield Footer()

        # Right pane for reports (hidden by default)
        with Container(id="right_pane", classes="hidden"):
            with Container(id="right_pane_header"):
                yield Select(id="global_currency", options=[("USD", "USD"), ("INR", "INR")], value="USD", allow_blank=False)
                yield Button("X", id="close_report")
            yield Static(id="report_area")

    def on_button_pressed(self, event):
        if event.button.id == "add_expense":
            amount = self.query_one("#amount").value
            currency = self.query_one("#currency").value
            desc = self.query_one("#description").value
            cat = self.query_one("#category").value
            if amount and desc and currency in ["USD", "INR"]:  # Ensure currency is selected
                self.manager.add_expense(currency, amount, desc, cat)
                self.query_one("#amount").value = ""
                self.query_one("#description").value = ""
            else:
                print("Error: All fields (including a valid currency) are required.")
            self.show_report()
        elif event.button.id.startswith("delete_"):
            index = int(event.button.id.split("_")[1])
            self.manager.delete_expense(index)
            self.show_report()
        elif event.button.id.startswith("edit_"):
            index = int(event.button.id.split("_")[1])
            self.start_editing(index)
        elif event.button.id == "save_edit":
            self.save_editing()
        elif event.button.id == "monthly":
            report = self.manager.get_monthly_report(2025, 3)
            self.show_report(report)
            self.report_visible = True
            self.query_one("#right_pane").remove_class("hidden")
        elif event.button.id == "yearly":
            report = self.manager.get_yearly_report(2025)
            self.show_report(report)
            self.report_visible = True
            self.query_one("#right_pane").remove_class("hidden")
        elif event.button.id == "close_report":
            self.report_visible = False
            self.query_one("#right_pane").add_class("hidden")
            self.show_report()

    def on_select_changed(self, event):
        if event.select.id == "global_currency":
            self.global_currency = event.value
            print(f"Global currency changed to: {self.global_currency}")
            if self.report_visible:
                self.show_report()

    def show_report(self, expenses=None):
        if expenses is None:
            expenses = self.manager.expenses
        report_area = self.query_one("#report_area")
        report_area.remove_children()
        report_area.mount(ReportView(expenses, self.converter, self.global_currency))

    def start_editing(self, index):
        self.editing_index = index
        expense = self.manager.expenses[index]
        self.query_one("#edit_amount").value = str(expense["amount"])
        self.query_one("#edit_description").value = expense["description"]
        self.query_one("#edit_category").value = expense["category"]
        self.query_one("#edit_form").remove_class("hidden")

    def save_editing(self):
        if self.editing_index is not None:
            self.manager.expenses[self.editing_index]["amount"] = float(self.query_one("#edit_amount").value)
            self.manager.expenses[self.editing_index]["description"] = self.query_one("#edit_description").value
            self.manager.expenses[self.editing_index]["category"] = self.query_one("#edit_category").value
            self.manager.save_data()
            self.query_one("#edit_form").add_class("hidden")
            self.editing_index = None
            self.show_report()

    def on_mount(self):
        self.query_one("#global_currency").value = self.global_currency