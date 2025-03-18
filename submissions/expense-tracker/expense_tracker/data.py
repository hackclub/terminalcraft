import json
from datetime import datetime
import os

class ExpenseManager:
    def __init__(self, filename="expenses.json"):
        self.filename = filename
        self.expenses = self.load_data()
        self.categories = ["Food", "Travel", "Miscellaneous", "Rent", "Utilities", "Entertainment"]

    def load_data(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                data = json.load(f)
                # If data is a single dict, wrap it in a list
                if isinstance(data, dict):
                    data = [data]
                # Ensure each expense has a 'currency' field
                for exp in data:
                    if not isinstance(exp, dict):  # Skip if exp isn’t a dict
                        continue
                    if 'currency' not in exp:
                        exp['currency'] = 'USD'  # Default to USD if missing
                return data
        return []

    def save_data(self):
        with open(self.filename, 'w') as f:
            json.dump(self.expenses, f, indent=2)

    def add_expense(self, currency, amount, description, category):
        expense = {
            "date": datetime.now().isoformat(),
            "currency": currency,
            "amount": float(amount),
            "description": description,
            "category": category
        }
        self.expenses.append(expense)
        self.save_data()

    def delete_expense(self, index):
        if 0 <= index < len(self.expenses):
            del self.expenses[index]
            self.save_data()

    def get_monthly_report(self, year, month):
        return [e for e in self.expenses if e["date"].startswith(f"{year}-{month:02d}")]

    def get_yearly_report(self, year):
        return [e for e in self.expenses if e["date"].startswith(str(year))]