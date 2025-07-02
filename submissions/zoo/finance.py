from collections import defaultdict
class Finance:
    """Manages the zoo's finances with detailed tracking."""
    def __init__(self, initial_money):
        self.money = initial_money
        self.daily_income = defaultdict(float)
        self.daily_expenses = defaultdict(float)
        self.history = []
    def add_income(self, amount, category='Tickets'):
        """Adds income to the zoo under a specific category."""
        self.money += amount
        self.daily_income[category] += amount
    def add_expense(self, amount, category='General'):
        """Adds an expense to the zoo under a specific category."""
        self.money -= amount
        self.daily_expenses[category] += amount
    def process_day(self, date):
        """Processes and prints the daily financial summary."""
        total_income = sum(self.daily_income.values())
        total_expenses = sum(self.daily_expenses.values())
        net_profit = total_income - total_expenses
        self.history.append({
            'date': date.isoformat(),
            'income': dict(self.daily_income),
            'expenses': dict(self.daily_expenses),
            'net_profit': net_profit
        })
        print("\n--- Daily Financial Report ---")
        print(f"  Total Income: ${total_income:.2f}")
        for category, amount in self.daily_income.items():
            print(f"    - {category}: ${amount:.2f}")
        print(f"  Total Expenses: ${total_expenses:.2f}")
        for category, amount in self.daily_expenses.items():
            print(f"    - {category}: ${amount:.2f}")
        print(f"  Net Profit: ${net_profit:.2f}")
        print(f"  Current Balance: ${self.money:.2f}")
        self.daily_income.clear()
        self.daily_expenses.clear()
    def to_dict(self):
        """Converts the finance state to a dictionary for saving."""
        return {
            'money': self.money,
            'daily_income': dict(self.daily_income),  
            'daily_expenses': dict(self.daily_expenses),  
            'history': self.history
        }