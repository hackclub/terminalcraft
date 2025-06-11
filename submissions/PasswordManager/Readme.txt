Terminal Password Manager

A simple yet secure password manager that runs in your terminal. Store, generate, and manage all your passwords locally with strong encryption.

Requirements

Python 3.6 or higher
cryptography library
pyperclip library (optional, for clipboard functionality)

Install dependencies:

pip install cryptography pyperclip

Getting Started

When you first run the program, you'll be asked to create a master password. This master password is used to encrypt and decrypt all your stored passwords.

Important: Remember your master password! Without it, you cannot access any of your stored passwords.

Main Menu Options

Once you're logged in, you'll see the main menu with these options:

1. Generate Password
Creates a new secure password with customizable options:

Choose password length (8-128 characters)
Include/exclude uppercase letters, lowercase letters, numbers, and symbols
Option to exclude confusing characters (0, O, l, 1, I, |, `)
Real-time password strength analysis
Automatically copies password to clipboard
Option to save the generated password directly

2. Generate Passphrase
Creates memorable passphrases using the format: Adjective-Noun-Number-Symbol

Example: "Happy-Mountain-42!"
Easier to remember than random characters
Still cryptographically secure

3. Add Custom Password
Manually add a password entry:

Service/website name (required)
Username
Password (with strength analysis)
Website URL
Notes for additional information
Automatically timestamps when created

4. View Password
Retrieve and display a specific password:

Search by service name or choose from a numbered list
Shows all details including username, website, notes, and timestamps
Displays password strength analysis
Copies password to clipboard automatically

5. List All Passwords
Shows an overview of all stored passwords:

Service names with strength indicators
Quick visual overview of your password collection
Shows creation dates

6. Search Passwords
Find passwords across all fields:

Searches service names, usernames, websites, and notes
Case-insensitive partial matching
Returns numbered list of matches for easy selection

7. Edit Password
Modify existing password entries:

Select which service to edit
Update any field (service name, username, password, website, notes)
Real-time password strength checking for new passwords
Automatically updates timestamp

8. Delete Password
Safely remove password entries:

Confirmation prompt to prevent accidents
Shows password details before deletion
Cannot be undone (unless you have backups)

9. View Statistics
Get insights about your password collection:

Total number of stored passwords
Password strength distribution (strong/medium/weak)
Average strength score
Completeness statistics (entries with usernames, websites, notes)

10. Import Passwords
Import password data from JSON files:

Supports importing from other password managers
Validates file format before importing
Handles legacy format conversion automatically

11. Export Passwords
Export your passwords to an unencrypted JSON file:

Warning: Exported files are NOT encrypted
Useful for backups or transferring to other tools
Creates timestamped export files

12. Create Backup
Manually create a backup of your encrypted password database:

Saves to backups/ folder with timestamp
Backups are also created automatically before major operations
Keeps your data safe in case of corruption

13. Change Master Password
Update your master password:

Must enter current password first
New password must be at least 8 characters
Re-encrypts entire database with new password
Creates automatic backup before changing

14. Show System Info
Displays information about your password manager:

File locations and their purposes
Security architecture details
Current status of all system files

File Storage and Security
Your password manager creates a hidden folder called .password_manager in your home directory. This folder contains:

passwords.dat - Your encrypted password database
salt.dat - Cryptographic salt used for encryption
backups/ - Folder containing backup files

Encryption Details

Uses AES-256 encryption (military-grade security)
Master password is strengthened using PBKDF2 with 100,000 iterations
Each password database has a unique salt for additional security
All data is encrypted before being saved to disk

Critical Security Notes

NEVER delete the salt.dat file - without it, your passwords are permanently lost
NEVER delete the passwords.dat file - this contains all your encrypted passwords
Backup your .password_manager folder regularly - store backups in a safe location
Remember your master password - there's no way to recover it if forgotten
The backup files in the backups/ folder are encrypted and safe to store

Important Warnings

Master Password Recovery: There is no way to recover your master password if you forget it. Your passwords will be permanently lost.
File Protection: The salt.dat and passwords.dat files are critical. Deleting either will result in permanent data loss.
Regular Backups: Use the backup feature regularly. Store backups in multiple locations (external drive, cloud storage, etc.).
Export Security: Exported JSON files are unencrypted. Delete them after use or store them securely.


Author: Shivansh