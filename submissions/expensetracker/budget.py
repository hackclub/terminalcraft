import argparse
import json
import os
import matplotlib.pyplot as plt

DATA_FILE = "budget_data.json" # the name of the data file
EXPORT_CHART = "chart.png" # the name of the pie chat image

def load_data():
    if not os.path.exists(DATA_FILE):
        return {"budget": 0, "expenses": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def set_budget(amount):
    data = load_data()
    data["budget"] = amount
    save_data(data)
    print(f"Monthly budget set to £{amount}.")

def add_expense(category, amount):
    data = load_data()
    data["expenses"].append({"category": category, "amount": amount})
    save_data(data)
    print(f"Added expense: {category} - £{amount}.")

def summarise_expenses():
    data = load_data()
    categories = {}
    for expense in data["expenses"]:
        categories[expense["category"]] = categories.get(expense["category"], 0) + expense["amount"]

    print("\nExpense Summary:")
    for category, total in categories.items():
        print(f"  {category}: £{total:.2f}")

    total_spent = sum(expense["amount"] for expense in data["expenses"])
    remaining_budget = data["budget"] - total_spent

    print(f"\nTotal Spending: £{total_spent:.2f}")
    print(f"Remaining Budget: £{remaining_budget:.2f}")

def visualise_expenses():
    data = load_data()
    categories = {}
    for expense in data["expenses"]:
        categories[expense["category"]] = categories.get(expense["category"], 0) + expense["amount"]

    if not categories:
        print("There is nothing to visualise.")
        return

    labels = list(categories.keys())
    amounts = list(categories.values())

    plt.figure(figsize=(8, 6))
    plt.pie(amounts, labels=labels, autopct="%1.1f%%", startangle=140)
    plt.title("Expenses")
    plt.savefig(EXPORT_CHART)
    print("Expense chart saved as", EXPORT_CHART, ".")

def export_data(output_file):
    data = load_data()
    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Data exported to {output_file}.")

def import_data(input_file):
    if not os.path.exists(input_file):
        print(f"File {input_file} doesn't exist.")
        return
    with open(input_file, "r") as f:
        imported_data = json.load(f)

    data = load_data()
    data["expenses"].extend(imported_data.get("expenses", []))
    data["budget"] = imported_data.get("budget", data["budget"])
    save_data(data)
    print(f"Data imported from {input_file}.")

def main():
    parser = argparse.ArgumentParser(description="Python CLI Budget Tracker")
    subparsers = parser.add_subparsers(dest="command")

    parser_set_budget = subparsers.add_parser("set-budget", help="Set the monthly budget")
    parser_set_budget.add_argument("amount", type=float, help="Budget amount in Pounds")

    parser_add_expense = subparsers.add_parser("add-expense", help="Add a new expense")
    parser_add_expense.add_argument("category", type=str, help="Expense category")
    parser_add_expense.add_argument("amount", type=float, help="Expense amount in Pounds")

    parser_summarise = subparsers.add_parser("summarise", help="Summarise expenses and budget")

    parser_visualise = subparsers.add_parser("visualise", help="Visualise expenses as a pie chart")

    parser_export = subparsers.add_parser("export", help="Export the data to a JSON file")
    parser_export.add_argument("output_file", type=str, help="Output file name")

    parser_import = subparsers.add_parser("import", help="Import the data from a JSON file")
    parser_import.add_argument("input_file", type=str, help="Input file name")

    args = parser.parse_args()

    # the great elif chain
    if args.command == "set-budget":
        set_budget(args.amount)
    elif args.command == "add-expense":
        add_expense(args.category, args.amount)
    elif args.command == "summarise":
        summarise_expenses()
    elif args.command == "visualise":
        visualise_expenses()
    elif args.command == "export":
        export_data(args.output_file)
    elif args.command == "import":
        import_data(args.input_file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
