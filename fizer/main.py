import organizer
import undo
import os

def main():
    print("\n📂 File Organizer")
    print("1. Organize Files")
    print("2. Undo Last Organization")
    
    choice = input("\nChoose an option (1/2): ").strip()
    
    if choice == "1":
        folder = input("\nEnter the folder path to organize: ").strip()
        if os.path.exists(folder):
            organizer.organize_files(folder)
        else:
            print("❌ Error: Folder does not exist!")
    elif choice == "2":
        undo.undo_last_operation()
    else:
        print("❌ Invalid choice. Exiting.")

if __name__ == "__main__":
    main()
