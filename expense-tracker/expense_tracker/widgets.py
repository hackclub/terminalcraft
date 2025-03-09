from textual.widget import Widget
from textual.widgets import Label, Input, Select, Button
from textual.containers import Container
from expense_tracker.data import ExpenseManager

class ExpenseForm(Widget):
    def compose(self):
        with Container():
            yield Label("Add Expense")
            yield Input(id="amount", placeholder="Amount")
            yield Select(id="currency", options=[("USD", "USD"), ("INR", "INR")], value="USD", allow_blank=False)
            yield Input(id="description", placeholder="Description")
            yield Select(id="category", options=[(c, c) for c in ExpenseManager().categories], value="Miscellaneous", allow_blank=False)
            yield Button("Add", id="add_expense")

class ReportView(Widget):
    def __init__(self, expenses, converter, global_currency):
        super().__init__()
        self.expenses = expenses
        self.converter = converter
        self.global_currency = global_currency

    def compose(self):
        for i, exp in enumerate(self.expenses):
            currency = exp.get("currency", "USD")
            amount = self.converter.convert(exp["amount"], currency, self.global_currency)
            yield Label(f"{i}: {exp['date']} - {amount:.2f} {self.global_currency} - {exp['description']} ({exp['category']})")
            yield Button("Edit", id=f"edit_{i}")
            yield Button("Delete", id=f"delete_{i}")