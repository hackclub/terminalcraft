from time import sleep
from typing import Any, Dict
from scanner import scan_all
from display import animate_ghost_logo, logo, MultiSelectList, ScrollableList, display_results, display_options, interactive_display_options, clear, center_print, error_print, show_details, show_scan_summary, show_thank_you_message, success_print, note_print, cyberbunk_display_options, console
from colorama import Fore
from rich.prompt import Prompt
import os
import sys
import argparse
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.console import Group
import time
import shutil

from utils import export_results, results_to_list

orig_cwd          = str(os.getcwd())
working_directory = os.getcwd()

def print_cwd():
    console.print(f"[dim]Current directory: {working_directory}[/dim]")

def change_working_directory():
    global working_directory

    clear()
    center_print("Changing Working directory")
    
    while True:
        print_cwd()
        new_path = Prompt.ask("[green]Enter the new path (or 'q' to go back)[/green]")
        new_path = os.path.expanduser(new_path)
        if new_path.lower() == 'q':
            main()
        
        if not os.path.exists(new_path) and not os.path.isdir(new_path):
            error_print("You should enter an existing directory path!")
        else:
            break
    
    try:
        os.chdir(new_path)
        working_directory = new_path
        success_print(f"=> Working directory changed to: {new_path}")
    except PermissionError:
        error_print("Permission denied for this directory!")
    except Exception as e:
        error_print(f"Error changing directory: {str(e)}")

    main()

def scan_all_tab():
    scan_result = scan_all(working_directory, live_ui=True)
    clear()
    show_scan_summary(scan_result, working_directory)
    while True:
        print("\nWhat would you like to do next?\n")
        cyberbunk_display_options(title="", options=[("[1]", "View Details"),
                                                    ("[2]", "Delete All"),
                                                    ("[3]", "Selectively Delete"),
                                                    ("[4]", "Export Report"),
                                                    ("[5]", "Back to Main Menu")])
        choice = Prompt.ask("Select an option", choices=[
                            "1", "2", "3", "4", "5"])
        if choice == "1":
            show_details(scan_result, 'all')
        elif choice == "2":
            ScrollableList(
                results_to_list(scan_result),
                "Are you sure you want to delete these files?",
                6,
                on_select=lambda item: console.log(f"[yellow]Selected:[/] {item}"),
                on_enter=lambda item: console.log(f"[green]Enter pressed on:[/] {item}"),
                input_prompt="Please, Enter Yes to confirm: ",
                input_handler=lambda res: handle_confirm_deletion(scan_result, res)
            ).show()
        elif choice == "3":
            MultiSelectList(
                items=results_to_list(scan_result, show_both_duplicates=True),
                title="Selectively Delete",
                window_size=8,

            ).show()
        elif choice == "4":
            show_export_options_tab(scan_result)
        elif choice == "5":
            main()
            break

def scan_large_files_tab():
    clear()
    center_print("Scan for Large Files 💾")
    print_cwd()
    while True:
        size = Prompt.ask("[green]Enter file size threshold in MB (default: 50MB): (or 'q' to go back)[/green]", default=f"{50}")
        if size == 'q':
            main()
            return
        try:
            size = int(size)
            break
        except:
            error_print("File size should be a number!")
    
    scan_result = scan_all(
        working_directory, 
        live_ui=True,
        scan_ghosts=False,
        scan_large=True,
        scan_old=False,
        scan_duplicates=False,
        large_threshold=size * 1024 * 1024
    )
    
    clear()
    show_scan_summary(scan_result, working_directory)
    while True:
        print("\nWhat would you like to do next?\n")
        cyberbunk_display_options(title="", options=[("[1]", "View Details"),
                                                    ("[2]", "Delete All"),
                                                    ("[3]", "Selectively Delete"),
                                                    ("[4]", "Export Report"),
                                                    ("[5]", "Back to Main Menu")])
        choice = Prompt.ask("Select an option", choices=[
                            "1", "2", "3", "4", "5"])
        if choice == "1":
            show_details(scan_result, 'large')
        elif choice == "2":
            ScrollableList(
                results_to_list(scan_result),
                "Are you sure you want to delete these files?",
                6,
                on_select=lambda item: console.log(f"[yellow]Selected:[/] {item}"),
                on_enter=lambda item: console.log(f"[green]Enter pressed on:[/] {item}"),
                input_prompt="Please, Enter Yes to confirm: ",
                input_handler=lambda res: handle_confirm_deletion(scan_result, res)
            ).show()
        elif choice == "3":
            MultiSelectList(
                items=results_to_list(scan_result, show_both_duplicates=True),
                title="Selectively Delete",
                window_size=8,
            ).show()
        elif choice == "4":
            show_export_options_tab(scan_result)
        elif choice == "5":
            main()
            break

def scan_old_files_tab():
    clear()
    center_print("Scan for Old Files ⌛")
    print_cwd()
    while True:
        age = Prompt.ask("[green]Enter age threshold in days (default: 180): (or 'q' to go back)[/green]", default=f"{180}")
        if age == 'q':
            main()
            return
        try:
            age = int(age)
            break
        except:
            error_print("File age should be a number!")
    
    date_type = interactive_display_options(title="Use which date type?", options=[('1', 'Last Modified'), ('2', 'Last Accessed'), ('3', 'Created (if available)')])
    
    scan_result = scan_all(
        working_directory, 
        live_ui=True,
        scan_ghosts=False,
        scan_large=False,
        scan_old=True,
        scan_duplicates=False,
        old_threshold=age * 24 * 3600
    )
    
    clear()
    show_scan_summary(scan_result, working_directory)
    while True:
        print("\nWhat would you like to do next?\n")
        cyberbunk_display_options(title="", options=[("[1]", "View Details"),
                                                    ("[2]", "Delete All"),
                                                    ("[3]", "Selectively Delete"),
                                                    ("[4]", "Export Report"),
                                                    ("[5]", "Back to Main Menu")])
        choice = Prompt.ask("Select an option", choices=[
                            "1", "2", "3", "4", "5"])
        if choice == "1":
            show_details(scan_result, 'old')
        elif choice == "2":
            ScrollableList(
                results_to_list(scan_result),
                "Are you sure you want to delete these files?",
                6,
                on_select=lambda item: console.log(f"[yellow]Selected:[/] {item}"),
                on_enter=lambda item: console.log(f"[green]Enter pressed on:[/] {item}"),
                input_prompt="Please, Enter Yes to confirm: ",
                input_handler=lambda res: handle_confirm_deletion(scan_result, res)
            ).show()
        elif choice == "3":
            MultiSelectList(
                items=results_to_list(scan_result, show_both_duplicates=True),
                title="Selectively Delete",
                window_size=8,
            ).show()
        elif choice == "4":
            show_export_options_tab(scan_result)
        elif choice == "5":
            main()
            break

def scan_ghost_files_tab():
    clear()
    center_print("Scan for Ghost Files 👻")
    print_cwd()
    
    scan_result = scan_all(
        working_directory, 
        live_ui=True,
        scan_ghosts=True,
        scan_large=False,
        scan_old=False,
        scan_duplicates=False
    )
    
    clear()
    show_scan_summary(scan_result, working_directory)
    while True:
        print("\nWhat would you like to do next?\n")
        cyberbunk_display_options(title="", options=[("[1]", "View Details"),
                                                    ("[2]", "Delete All"),
                                                    ("[3]", "Selectively Delete"),
                                                    ("[4]", "Export Report"),
                                                    ("[5]", "Back to Main Menu")])
        choice = Prompt.ask("Select an option", choices=[
                            "1", "2", "3", "4", "5"])
        if choice == "1":
            show_details(scan_result, 'ghosts')
        elif choice == "2":
            ScrollableList(
                results_to_list(scan_result),
                "Are you sure you want to delete these files?",
                6,
                on_select=lambda item: console.log(f"[yellow]Selected:[/] {item}"),
                on_enter=lambda item: console.log(f"[green]Enter pressed on:[/] {item}"),
                input_prompt="Please, Enter Yes to confirm: ",
                input_handler=lambda res: handle_confirm_deletion(scan_result, res)
            ).show()
        elif choice == "3":
            MultiSelectList(
                items=results_to_list(scan_result, show_both_duplicates=True),
                title="Selectively Delete",
                window_size=8,
            ).show()
        elif choice == "4":
            show_export_options_tab(scan_result)
        elif choice == "5":
            main()
            break

def scan_duplicates_tab():
    clear()
    center_print("Scan for Duplicates 🌀")
    print_cwd()
    
    hash_algo = interactive_display_options(title="Hash algorithm to use:", options=[('1', 'MD5 (faster)'), ('2', 'SHA1 (more secure)')])
    hash_algorithm = 'sha1' if hash_algo == '2' else 'md5'
    
    scan_result = scan_all(
        working_directory, 
        live_ui=True,
        scan_ghosts=False,
        scan_large=False,
        scan_old=False,
        scan_duplicates=True,
        hash_algo=hash_algorithm
    )
    
    clear()
    show_scan_summary(scan_result, working_directory)
    while True:
        print("\nWhat would you like to do next?\n")
        cyberbunk_display_options(title="", options=[("[1]", "View Details"),
                                                    ("[2]", "Delete All"),
                                                    ("[3]", "Selectively Delete"),
                                                    ("[4]", "Export Report"),
                                                    ("[5]", "Back to Main Menu")])
        choice = Prompt.ask("Select an option", choices=[
                            "1", "2", "3", "4", "5"])
        if choice == "1":
            show_details(scan_result, 'duplicates')
        elif choice == "2":
            ScrollableList(
                results_to_list(scan_result),
                "Are you sure you want to delete these files?",
                6,
                on_select=lambda item: console.log(f"[yellow]Selected:[/] {item}"),
                on_enter=lambda item: console.log(f"[green]Enter pressed on:[/] {item}"),
                input_prompt="Please, Enter Yes to confirm: ",
                input_handler=lambda res: handle_confirm_deletion(scan_result, res)
            ).show()
        elif choice == "3":
            MultiSelectList(
                items=results_to_list(scan_result, show_both_duplicates=True),
                title="Selectively Delete",
                window_size=8,
            ).show()
        elif choice == "4":
            show_export_options_tab(scan_result)
        elif choice == "5":
            main()
            break

def show_export_options_tab(results: Dict[str, Any]):
    options = [
        ("1", "Plain Text (.txt)"),
        ("2", "JSON (.json)"),
        ("3", "Markdown (.md)"),
        ("4", "Back")
    ]
    
    while True:
        console.clear()
        cyberbunk_display_options(options, title="Export as:")
        choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4"])
        
        if choice == "4":
            break
            
        format_map = {
            "1": "txt",
            "2": "json",
            "3": "md"
        }
        
        try:
            output_path = Prompt.ask("Enter output path (or press Enter for default)")
            if not output_path:
                output_path = None
                
            output_file = export_results(results, format_map[choice], output_path)
            success_print(f"\nResults exported successfully to: {output_file}")
            sleep(2)
        except Exception as e:
            error_print(f"\nError exporting results: {str(e)}")
            sleep(2)

def show_progress(message: str, total: int, process_func):
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="progress", size=3),
        Layout(name="status", size=3)
    )
    
    with Live(layout, refresh_per_second=10) as live:
        # Update header
        layout["header"].update(Panel(message, style="bold blue"))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Processing...", total=total)
            
            success_count = 0
            failed_items = []
            
            while not progress.finished:
                success, item_name = process_func()
                if success:
                    success_count += 1
                    layout["status"].update(
                        Panel(f"[green]✓ Successfully processed: {item_name}", style="green")
                    )
                else:
                    failed_items.append(item_name)
                    layout["status"].update(
                        Panel(f"[red]✗ Failed to process: {item_name}", style="red")
                    )
                progress.update(task, advance=1)
                time.sleep(0.1)  # Small delay for visual feedback
    
    # Show final summary
    if failed_items:
        console.print("\n[red]Failed items:[/red]")
        for item in failed_items:
            console.print(f"[red]  - {item}[/red]")
    
    console.print(f"\n[green]Successfully processed: {success_count}/{total} items[/green]")
    return success_count, failed_items

def handle_confirm_deletion(scan_result, res):
    if res.lower() != 'yes':
        return
    
    items_to_delete = results_to_list(scan_result, kind=True)
    
    if not items_to_delete:
        note_print("No files to delete!")
        return
    
    def delete_process():
        if not items_to_delete:
            return False, ""
        
        item_type, path = items_to_delete.pop(0)
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            return True, f"{item_type}: {path}"
        except Exception as e:
            return False, f"{item_type}: {path} ({str(e)})"
    
    success_count, failed_items = show_progress(
        "🗑️  Deleting files...",
        len(items_to_delete),
        delete_process
    )
    
    if success_count > 0:
        success_print(f"\nSuccessfully deleted {success_count} items!")
    if failed_items:
        error_print(f"\nFailed to delete {len(failed_items)} items.")
    
    time.sleep(2)
    sys.exit()

def parse_arguments():
    parser = argparse.ArgumentParser(description="GhostyDisk - Terminal Ghost File Hunter")
    parser.add_argument('--path', type=str, help='Custom scan path')
    parser.add_argument('--large', type=int, help='Set large file threshold in MB')
    parser.add_argument('--old', type=int, help='Set "old file" age in days')
    parser.add_argument('--ghost', action='store_true', help='Include ghost file scan')
    parser.add_argument('--no-dupes', action='store_true', help='Exclude duplicate scan')
    parser.add_argument('--dry-run', action='store_true', help='Simulate all actions, no deletion')
    parser.add_argument('--delete', action='store_true', help='Auto-delete without prompting')
    parser.add_argument('--export', type=str, help='Export report to file')
    parser.add_argument('--hash-algo', type=str, choices=['md5', 'sha1'], help='Choose hash algo for duplicates')
    parser.add_argument('--exclude', type=str, help='Read exclude patterns from txt/json')
    return parser.parse_args()

def should_show_ui(args):
    action_args = ['ghost', 'delete', 'dry_run', 'export']
    has_actions = any(getattr(args, arg, False) for arg in action_args)
    
    return not has_actions

def main():
    args = parse_arguments()

    if args.path:
        global working_directory
        working_directory = args.path
        if not os.path.exists(working_directory) or not os.path.isdir(working_directory):
            error_print("Invalid path specified!")
            return

    # If only config args are passed or no args at all, show UI
    if should_show_ui(args):
        clear()
        print(Fore.CYAN + logo + Fore.RESET)
        print(f"\n{Fore.BLUE}👻 Welcome to GhostyDisk — Terminal Ghost File Hunter! 🧹{Fore.RESET}")

        dir_display = f"(CWD: {working_directory})" if working_directory != orig_cwd else ""
        choices = [
            ("[1]", "Full Scan 👁️"),
            ("[2]", "Scan for Large Files 💾"),
            ("[3]", "Scan for Old Files ⌛"),
            ("[4]", "Scan for Ghost Files 👻"),
            ("[5]", "Scan for Duplicates 🌀"),
            ("[6]", f"Custom Directory 📂 {dir_display}"),
            ("[0]", "Exit")
        ]
        
        print_cwd()
        display_options(choices)
        note_print("* You can choose more than one mode using comma (2, 3, 4, 5)")
        while True:
            choice = input("Please, enter a choice: ")
            if len(choice) != 0 and choice[0] == ':':
                break
            try:
                if ',' in choice:
                    modes = [int(mode.strip()) for mode in choice.split(',')]
                    if all(mode in range(1, 6 + 1) for mode in modes):
                        scan_multiple_modes(modes)
                        return
                    else:
                        print("Please, Enter valid choices (1-6)!")
                    continue
                
                choice = int(choice)
                if choice in range(6 + 1):
                    break
                else:
                    print("Please, Enter a valid choice!")
            except:
                print("Choice must be a number or comma-separated numbers!")

        if choice == 1:
            scan_all_tab()
        if choice == 2:
            scan_large_files_tab()
        elif choice == 3:
            scan_old_files_tab()
        elif choice == 4:
            scan_ghost_files_tab()
        elif choice == 5:
            scan_duplicates_tab()
        elif choice == 6:
            change_working_directory()
        elif choice == 0:
            console.print("See you soon!", style="bright_black bold")
            sys.exit()
        elif choice == ':ghost':
            animate_ghost_logo()
        elif choice == ':love':
            show_thank_you_message()
        return

    # Handle action arguments
    if args.ghost or args.large or args.old or not args.no_dupes:
        scan_result = scan_all(
            working_directory,
            live_ui=True,
            large_threshold=args.large * 1024 * 1024 if args.large else None,
            old_threshold=args.old * 24 * 3600 if args.old else None,
            scan_ghosts=args.ghost,
            scan_large=args.large is not None,
            scan_old=args.old is not None,
            scan_duplicates=not args.no_dupes,
            hash_algo=args.hash_algo or 'md5',
            exclude_patterns=args.exclude
        )
        
        if args.dry_run:
            note_print("Dry run: No files will be deleted.")
            show_scan_summary(scan_result, working_directory)
        
        if args.delete:
            handle_confirm_deletion(scan_result, "yes")
        
        if args.export:
            export_results(scan_result, format_type='txt', output_path=args.export)

def scan_multiple_modes(modes):
    clear()
    center_print("Multiple Scan Modes")
    print_cwd()
    
    scan_ghosts = 4 in modes
    scan_large = 2 in modes
    scan_old = 3 in modes
    scan_duplicates = 5 in modes
    
    if 1 in modes:
        scan_ghosts = scan_large = scan_old = scan_duplicates = True
    
    large_threshold = 50 * 1024 * 1024  # Default 50MB
    old_threshold = 180 * 24 * 3600     # Default 180 days
    hash_algorithm = 'md5'              # Default hash algorithm
    
    if scan_large:
        try:
            size = Prompt.ask("[green]Enter file size threshold in MB (default: 50MB):[/green]", default=f"{50}")
            large_threshold = int(size) * 1024 * 1024
        except:
            error_print("Using default file size threshold (50MB)")
    
    if scan_old:
        try:
            age = Prompt.ask("[green]Enter age threshold in days (default: 180):[/green]", default=f"{180}")
            old_threshold = int(age) * 24 * 3600
        except:
            error_print("Using default age threshold (180 days)")
    
    if scan_duplicates:
        hash_algo = interactive_display_options(title="Hash algorithm to use:", 
                                              options=[('1', 'MD5 (faster)'), ('2', 'SHA1 (more secure)')])
        hash_algorithm = 'sha1' if hash_algo == '2' else 'md5'
    
    scan_result = scan_all(
        working_directory, 
        live_ui=True,
        scan_ghosts=scan_ghosts,
        scan_large=scan_large,
        scan_old=scan_old,
        scan_duplicates=scan_duplicates,
        large_threshold=large_threshold,
        old_threshold=old_threshold,
        hash_algo=hash_algorithm
    )
    
    clear()
    show_scan_summary(scan_result, working_directory)
    while True:
        print("\nWhat would you like to do next?\n")
        cyberbunk_display_options(title="", options=[("[1]", "View Details"),
                                                   ("[2]", "Delete All"),
                                                   ("[3]", "Selectively Delete"),
                                                   ("[4]", "Export Report"),
                                                   ("[5]", "Back to Main Menu")])
        choice = Prompt.ask("Select an option", choices=[
                          "1", "2", "3", "4", "5"])
        if choice == "1":
            scan_types = []
            if scan_ghosts:
                scan_types.append('ghosts')
            if scan_large:
                scan_types.append('large')
            if scan_old:
                scan_types.append('old')
            if scan_duplicates:
                scan_types.append('duplicates')
            
            if len(scan_types) > 1:
                options = []
                for i, scan_type in enumerate(scan_types, 1):
                    icon = {
                        'ghosts': '👻',
                        'large': '💾',
                        'old': '⌛',
                        'duplicates': '🌀'
                    }.get(scan_type, '')
                    options.append((str(i), f"{icon} {scan_type.capitalize()}"))
                
                type_choice = interactive_display_options(title="View details for:", options=options)
                if type_choice.isdigit() and 1 <= int(type_choice) <= len(scan_types):
                    show_details(scan_result, scan_types[int(type_choice) - 1])
            else:
                show_details(scan_result, scan_types[0] if scan_types else 'all')
        elif choice == "2":
            ScrollableList(
                results_to_list(scan_result),
                "Are you sure you want to delete these files?",
                6,
                on_select=lambda item: console.log(f"[yellow]Selected:[/] {item}"),
                on_enter=lambda item: console.log(f"[green]Enter pressed on:[/] {item}"),
                input_prompt="Please, Enter Yes to confirm: ",
                input_handler=lambda res: handle_confirm_deletion(scan_result, res)
            ).show()
        elif choice == "3":
            MultiSelectList(
                items=results_to_list(scan_result, show_both_duplicates=True),
                title="Selectively Delete",
                window_size=8,
            ).show()
        elif choice == "4":
            show_export_options_tab(scan_result)
        elif choice == "5":
            main()
            break

if __name__ == "__main__":
    main()