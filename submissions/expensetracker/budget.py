import argparse
import json
import os
import matplotlib.pyplot as plt

def load_data(data_file):
    if not os.path.exists(data_file):
        return {"budget": 0, "expenses": []}
    with open(data_file, "r") as f:
        return json.load(f)

def save_data(data, data_file):
    with open(data_file, "w") as f:
        json.dump(data, f, indent=4)

def set_budget(amount, data_file):
    data = load_data(data_file)
    data["budget"] = amount
    save_data(data, data_file)
    print(f"Monthly budget set to £{amount}.")

def add_expense(category, amount, data_file):
    data = load_data(data_file)
    data["expenses"].append({"category": category, "amount": amount})
    save_data(data, data_file)
    print(f"Added expense: {category} - £{amount}.")

def summarise_expenses(data_file):
    data = load_data(data_file)
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

def visualise_expenses(data_file, export_chart):
    data = load_data(data_file)
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
    plt.savefig(export_chart)
    print("Expense chart saved as", export_chart, ".")

def export_data(output_file, data_file):
    data = load_data(data_file)
    with open(output_file, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Data exported to {output_file}.")

def import_data(input_file, data_file):
    if not os.path.exists(input_file):
        print(f"File {input_file} doesn't exist.")
        return
    with open(input_file, "r") as f:
        imported_data = json.load(f)

    data = load_data(data_file)
    data["expenses"].extend(imported_data.get("expenses", []))
    data["budget"] = imported_data.get("budget", data["budget"])
    save_data(data, data_file)
    print(f"Data imported from {input_file}.")

def main():
    parser = argparse.ArgumentParser(
        description="Python CLI Budget Tracker",
        epilog="""
Examples:
  python budget.py set-budget 500           (Set total budget)
  python budget.py add-expense BLAHAJ 20    (Add your expenses)
  python budget.py summarise                (Show the data in the terminal)
  python budget.py --export-chart=chart.png visualise (Generate a pie chart)
  python budget.py export budget_backup.json (Export data to file)
  python budget.py import budget_backup.json (Import data from file)
""",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("--data-file", type=str, default="budget_data.json", help="File name to store budget data")
    parser.add_argument("--export-chart", type=str, default="chart.png", help="File name for exported pie chart")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("set-budget", help="Set the monthly budget").add_argument("amount", type=float, help="Budget amount in Pounds")
    add_exp = subparsers.add_parser("add-expense", help="Add a new expense")
    add_exp.add_argument("category", type=str, help="Expense category")
    add_exp.add_argument("amount", type=float, help="Expense amount in Pounds")
    subparsers.add_parser("summarise", help="Summarise expenses and budget")
    subparsers.add_parser("visualise", help="Visualise expenses as a pie chart")
    exp = subparsers.add_parser("export", help="Export data to JSON file")
    exp.add_argument("output_file", type=str, help="Output file name")
    imp = subparsers.add_parser("import", help="Import data from JSON file")
    imp.add_argument("input_file", type=str, help="Input file name")
    
    args = parser.parse_args()
    data_file = args.data_file
    export_chart = args.export_chart

    # the great elif chain
    if args.command == "set-budget":
        set_budget(args.amount, data_file)
    elif args.command == "add-expense":
        add_expense(args.category, args.amount, data_file)
    elif args.command == "summarise":
        summarise_expenses(data_file)
    elif args.command == "visualise":
        visualise_expenses(data_file, export_chart)
    elif args.command == "export":
        export_data(args.output_file, data_file)
    elif args.command == "import":
        import_data(args.input_file, data_file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
