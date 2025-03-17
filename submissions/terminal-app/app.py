import csv
import os
import datetime
import calendar
from rich.console import Console
from rich.table import Table
from cursesmenu import CursesMenu
from cursesmenu.items import FunctionItem

console = Console()
Exp_file = "expenses.csv"
Inc_file = "income.csv"

BANNER = """
  ______                                 
 |  ____|                                 
 | |__  __  ___ __   ___ _ __  ___  ___  
 |  __| \ \/ / '_ \ / _ \ '_ \/ __|/ _ \ 
 | |____ >  <| |_) |  __/ | | \__ \  __/ 
 |______/_/\_\ .__/ \___|_| |_|___/\___| 
 |__   __|   | |     | |                  
    | |_ __ _|_|  ___| | _____ _ __      
    | | '__/ _` |/ __| |/ / _ \ '__|     
    | | | | (_| | (__|   <  __/ |        
    |_|_|  \__,_|\___|_|\_\___|_|        
""" 

def init_files():
    if not os.path.exists(Exp_file):
        with open(Exp_file, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Category", "Amount", "Description"])

    if not os.path.exists(Inc_file):
        with open(Inc_file, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Date", "Source", "Amount", "Description"])

def get_date():
    use_curr = input("Use current date? (Y/N): ").strip().lower()
    if use_curr == 'y':
        return datetime.datetime.now().strftime("%d/%m/%y")
    else:
        while True:
            date_input = input("Enter date (dd/mm/yy): ")
            try:
                datetime.datetime.strptime(date_input, "%d/%m/%y")
                return date_input
            except ValueError:
                console.print("[red]Invalid date format. Please use dd/mm/yy.[/red]")




def add_exp():
    date = get_date()
    category = input("Enter category (Food, Travel, Shopping, etc.): ")
    amount = input("Enter amount: ")
    desc = input("Enter description: ")

    with open(Exp_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([date, category, amount, desc])
    console.print("[green]Expense added successfully![/green]")
    input("\nPress Enter to continue...")

def add_inc():
    date = get_date()
    source = input("Enter income source (Salary, Freelance, etc.): ")
    amount = input("Enter amount: ")
    desc = input("Enter description: ")

    with open(Inc_file, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([date, source, amount, desc])
    console.print("[green]Income added successfully![/green]")
    input("\nPress Enter to continue...")

def view_exp():
    if not os.path.exists(Exp_file) or os.stat(Exp_file).st_size == 0:
        console.print("[red]No expenses recorded yet.[/red]")
    else:
        tbl = Table(title="Expense Tracker", style="bold cyan")
        tbl.add_column("Date", style="cyan")
        tbl.add_column("Category", style="cyan")
        tbl.add_column("Amount", style="yellow")
        tbl.add_column("Description", style="white")

        with open(Exp_file, mode='r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                tbl.add_row(row[0], row[1], row[2], row[3])

        console.print(tbl)
    input("\nPress Enter to continue...")

def view_inc():
    if not os.path.exists(Inc_file) or os.stat(Inc_file).st_size == 0:
        console.print("[red]No income recorded yet.[/red]")
    else:
        tbl = Table(title="Income Tracker", style="bold cyan")
        tbl.add_column("Date", style="cyan")
        tbl.add_column("Source", style="cyan")
        tbl.add_column("Amount", style="yellow")
        tbl.add_column("Description", style="white")

        with open(Inc_file, mode='r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                tbl.add_row(row[0], row[1], row[2], row[3])

        console.print(tbl)
    input("\nPress Enter to continue...")

def total_spent():
    if not os.path.exists(Exp_file) or os.stat(Exp_file).st_size == 0:
        console.print("[red]No expenses recorded yet.[/red]")
    else:
        cat_totals = {}

        with open(Exp_file, mode='r') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                category = row[1]
                amount = float(row[2])
                cat_totals[category] = cat_totals.get(category, 0) + amount

        tbl = Table(title="Total Spending by Category", style="bold cyan")
        tbl.add_column("Category", style="cyan")
        tbl.add_column("Total Amount", style="yellow")

        for cat, total in cat_totals.items():
            tbl.add_row(cat, f"{total:.2f}")

        console.print(tbl)
    input("\nPress Enter to continue...")

def del_entry(ent_type):
    if ent_type == "expense":
        fname = Exp_file
        ent_name = "expense"
    elif ent_type == "income":
        fname = Inc_file
        ent_name = "income"
    else:
        console.print("[red]Invalid entry type. Please choose 'expense' or 'income'.[/red]")
        input("\nPress Enter to continue...")
        return

    if not os.path.exists(fname) or os.stat(fname).st_size == 0:
        console.print(f"[red]No {ent_name} entries recorded yet.[/red]")
        input("\nPress Enter to continue...")
        return

    tbl = Table(title=f"{ent_name.capitalize()} Entries", style="bold cyan")
    tbl.add_column("Index", style="cyan")
    tbl.add_column("Date", style="cyan")
    tbl.add_column("Category/Source", style="cyan")
    tbl.add_column("Amount", style="yellow")
    tbl.add_column("Description", style="white")

    entries = []
    with open(fname, mode='r') as f:
        reader = csv.reader(f)
        next(reader)
        for idx, row in enumerate(reader):
            entries.append(row)
            tbl.add_row(str(idx + 1), row[0], row[1], row[2], row[3])

    console.print(tbl)

    try:
        idx = int(input(f"Enter the index of the {ent_name} entry to delete: ")) - 1
        if idx < 0 or idx >= len(entries):
            console.print("[red]Invalid index.[/red]")
            input("\nPress Enter to continue...")
            return
    except ValueError:
        console.print("[red]Invalid input. Please enter a valid index.[/red]")
        input("\nPress Enter to continue...")
        return

    confirm = input(f"Are you sure you want to delete this {ent_name} entry? (Y/N): ").strip().lower()
    if confirm != 'y':
        console.print("[yellow]Deletion cancelled.[/yellow]")
        input("\nPress Enter to continue...")
        return

    entries.pop(idx)

    with open(fname, mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Category/Source", "Amount", "Description"])
        writer.writerows(entries)

    console.print("[green]Entry deleted successfully![/green]")
    input("\nPress Enter to continue...")

def del_entry_menu():
    console.print("[bold]Delete Entry[/bold]")
    del_menu = CursesMenu("Delete Menu", "Select an option below:")

    del_menu.items.append(FunctionItem("Delete Expense Entry", lambda: del_entry("expense")))
    del_menu.items.append(FunctionItem("Delete Income Entry", lambda: del_entry("income")))

    del_menu.show()
    main_menu()

def view_curr_cal():
    now = datetime.datetime.now()
    month = now.month
    year = now.year
    cal = calendar.month(year, month)
    console.print(f"[bold]Calendar for {calendar.month_name[month]} {year}:[/bold]")
    console.print(cal)
    input("\nPress Enter to continue...")

def enter_spec_cal():
    while True:
        try:
            date_input = input("Enter month and year (mm/yy): ")
            month, year = map(int, date_input.split('/'))
            if month < 1 or month > 12 or year < 0:
                raise ValueError
            cal = calendar.month(year, month)
            console.print(f"[bold]Calendar for {calendar.month_name[month]} {year}:[/bold]")
            console.print(cal)
            input("\nPress Enter to continue...")
            break
        except ValueError:
            console.print("[red]Invalid input. Please use the format mm/yy.[/red]")

def cal_menu():
    cal_menu = CursesMenu("Calendar Menu", "Select an option below:")
    cal_menu.items.append(FunctionItem("View Current Month's Calendar", view_curr_cal))
    cal_menu.items.append(FunctionItem("Enter Specific Month and Year", enter_spec_cal))

    cal_menu.show()
    main_menu()

def main_menu():
    menu = CursesMenu("Main Menu", "Select an option below(Use arrow keys to navigate):")

    menu.items.append(FunctionItem("Add Expense", add_exp))
    menu.items.append(FunctionItem("Add Income", add_inc))
    menu.items.append(FunctionItem("View Expenses", view_exp))
    menu.items.append(FunctionItem("View Income", view_inc))
    menu.items.append(FunctionItem("Show Total Spent by Category", total_spent))
    menu.items.append(FunctionItem("Delete Entry", del_entry_menu))
    menu.items.append(FunctionItem("View Calendar", cal_menu))

    menu.show()

def main():
    init_files()
    console.print(BANNER)
    input("\nPress Enter to continue to the menu...")
    main_menu()

if __name__ == "__main__":
    main()




