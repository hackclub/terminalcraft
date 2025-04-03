import organizer
import undo
import os
import config

def main():
    while True:
        print("\n📂 File Organizer")
        print("1. Organize Files")
        print("2. Undo Last Organization")
        print("3. Modify File Associations")
        print("4. Auto-Arrange Files")
        print("5. Exit")

        choice = input("\nChoose an option (1/2/3/4/5): ").strip()

        if choice == "1":
            folder = input("\nEnter the folder path to organize: ").strip()
            if os.path.exists(folder):
                organizer.organize_files(folder)
            else:
                print("❌ Error: Folder does not exist!")
        elif choice == "2":
            undo.undo_last_operation()
        elif choice == "3":
            config.modify_categories()
        elif choice == "4":
            folder = input("\nEnter the folder path to auto-arrange: ").strip()
            organizer.auto_arrange(folder)
        elif choice == "5":
            break
        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
