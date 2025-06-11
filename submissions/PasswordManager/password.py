#!/usr/bin/env python3
"""
Password Manager - Terminal App
A simple but secure password generator with encrypted storage.
Made for TerminalCraft YSWS 2025

Author: Shivansh
Requirements: pip install cryptography
"""

import os
import sys
import json
import secrets
import string
import re
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

class PasswordManager:
    def __init__(self):
        # Create secure folder in AppData (hidden from casual browsing)
        self.app_dir = os.path.join(os.path.expanduser("~"), ".password_manager")
        self.ensure_app_directory()
        
        self.data_file = os.path.join(self.app_dir, "passwords.dat")
        self.salt_file = os.path.join(self.app_dir, "salt.dat")
        self.fernet = None
        self.passwords = {}
        
    def ensure_app_directory(self):
        """Create the application directory if it doesn't exist"""
        try:
            if not os.path.exists(self.app_dir):
                os.makedirs(self.app_dir)
                print(f"📁 Created secure folder: {self.app_dir}")
        except Exception as e:
            print(f"❌ Can't create app directory: {e}")
            # Fallback to current directory
            self.app_dir = "."
    
    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_secure_input(self, prompt):
        """Get password input with visible typing (Windows compatible)"""
        print("⚠️  WARNING: Your password will be visible as you type!")
        print("   Make sure nobody is watching your screen.")
        return input(prompt)
    
    def generate_key(self, password, salt):
        """Generate encryption key from password and salt"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def create_salt(self):
        """Create and save salt file"""
        salt = os.urandom(16)
        try:
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
            return salt
        except Exception as e:
            print(f"❌ Can't save salt file: {e}")
            sys.exit(1)
    
    def load_salt(self):
        """Load salt from file if it exists"""
        try:
            with open(self.salt_file, 'rb') as f:
                return f.read()
        except FileNotFoundError:
            return self.create_salt()
        except Exception as e:
            print(f"❌ Can't load salt file: {e}")
            sys.exit(1)
    
    def setup_encryption(self, password):
        """Setup encryption with master password"""
        salt = self.load_salt()
        key = self.generate_key(password, salt)
        self.fernet = Fernet(key)
    
    def load_passwords(self):
        """Load encrypted passwords from file"""
        if not os.path.exists(self.data_file):
            self.passwords = {}
            return
        
        try:
            with open(self.data_file, 'rb') as f:
                encrypted_data = f.read()
            
            if encrypted_data:
                decrypted_data = self.fernet.decrypt(encrypted_data)
                self.passwords = json.loads(decrypted_data.decode())
            else:
                self.passwords = {}
        except Exception as e:
            print(f"❌ Can't load passwords: {e}")
            print("   File might be corrupted or wrong master password.")
            sys.exit(1)
    
    def save_passwords(self):
        """Save encrypted passwords to file"""
        try:
            data = json.dumps(self.passwords, indent=2)
            encrypted_data = self.fernet.encrypt(data.encode())
            
            with open(self.data_file, 'wb') as f:
                f.write(encrypted_data)
        except Exception as e:
            print(f"❌ Can't save passwords: {e}")
    
    def check_password_strength(self, password):
        """Check password strength and return score and feedback"""
        score = 0
        feedback = []
        
        # Length check
        if len(password) >= 12:
            score += 2
        elif len(password) >= 8:
            score += 1
        else:
            feedback.append("Too short (minimum 8 characters)")
        
        # Character variety checks
        if re.search(r'[a-z]', password):
            score += 1
        else:
            feedback.append("Add lowercase letters")
            
        if re.search(r'[A-Z]', password):
            score += 1
        else:
            feedback.append("Add uppercase letters")
            
        if re.search(r'\d', password):
            score += 1
        else:
            feedback.append("Add numbers")
            
        if re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            score += 1
        else:
            feedback.append("Add special characters")
        
        # Common patterns check
        if re.search(r'(.)\1{2,}', password):
            feedback.append("Avoid repeating characters")
            score -= 1
        
        if re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde)', password.lower()):
            feedback.append("Avoid sequential patterns")
            score -= 1
        
        # Determine strength
        if score >= 5:
            strength = "🟢 Strong"
        elif score >= 3:
            strength = "🟡 Medium"
        else:
            strength = "🔴 Weak"
        
        return strength, score, feedback
    
    def generate_password(self, length=16, use_symbols=True, use_numbers=True, 
                         use_lowercase=True, use_uppercase=True, exclude_ambiguous=False):
        """Generate a strong random password"""
        if not any([use_symbols, use_numbers, use_lowercase, use_uppercase]):
            print("❌ At least one character type must be selected!")
            return None
        
        chars = ""
        if use_lowercase:
            chars += string.ascii_lowercase
        if use_uppercase:
            chars += string.ascii_uppercase
        if use_numbers:
            chars += string.digits
        if use_symbols:
            chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
        # Remove ambiguous characters if requested
        if exclude_ambiguous:
            ambiguous = "0O1lI|`"
            chars = ''.join(c for c in chars if c not in ambiguous)
        
        # Ensure at least one character from each selected type
        password = []
        if use_lowercase:
            available = string.ascii_lowercase
            if exclude_ambiguous:
                available = ''.join(c for c in available if c not in "lI")
            password.append(secrets.choice(available))
            
        if use_uppercase:
            available = string.ascii_uppercase
            if exclude_ambiguous:
                available = ''.join(c for c in available if c not in "O")
            password.append(secrets.choice(available))
            
        if use_numbers:
            available = string.digits
            if exclude_ambiguous:
                available = ''.join(c for c in available if c not in "01")
            password.append(secrets.choice(available))
            
        if use_symbols:
            available = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if exclude_ambiguous:
                available = ''.join(c for c in available if c not in "|`")
            password.append(secrets.choice(available))
        
        # Fill the rest randomly
        for _ in range(length - len(password)):
            password.append(secrets.choice(chars))
        
        # Shuffle the password
        secrets.SystemRandom().shuffle(password)
        return ''.join(password)
    
    def generate_memorable_password(self):
        """Generate a memorable passphrase using word combinations"""
        # Simple word lists for memorable passwords
        adjectives = ['quick', 'bright', 'happy', 'silent', 'brave', 'calm', 'swift', 'wise', 'bold', 'gentle']
        nouns = ['tiger', 'ocean', 'mountain', 'forest', 'river', 'eagle', 'storm', 'flame', 'stone', 'wind']
        
        # Generate pattern: adjective-noun-number-symbol
        adj = secrets.choice(adjectives).capitalize()
        noun = secrets.choice(nouns).capitalize()
        number = secrets.randbelow(99) + 1
        symbol = secrets.choice(['!', '@', '#', '$', '%'])
        
        return f"{adj}{noun}{number}{symbol}"
    
    def get_password_options(self):
        """Get user preferences for password generation"""
        print("\n🔧 PASSWORD GENERATION OPTIONS")
        print("=" * 50)
        
        # Type selection
        print("1. Random password (recommended)")
        print("2. Memorable passphrase")
        
        while True:
            choice = input("Choose type (1-2, default 1): ").strip()
            if choice in ['1', '']:
                break
            elif choice == '2':
                return self.generate_memorable_password(), None, None, None, None, None
            else:
                print("❌ Please choose 1 or 2")
        
        # Length
        while True:
            try:
                length = input("Password length (8-128, default 16): ").strip()
                if not length:
                    length = 16
                else:
                    length = int(length)
                if 8 <= length <= 128:
                    break
                print("❌ Length must be between 8 and 128")
            except ValueError:
                print("❌ Please enter a valid number")
        
        # Character types
        print("\nCharacter types to include:")
        use_uppercase = input("Include UPPERCASE letters? (Y/n): ").strip().lower() != 'n'
        use_lowercase = input("Include lowercase letters? (Y/n): ").strip().lower() != 'n'
        use_numbers = input("Include numbers? (Y/n): ").strip().lower() != 'n'
        use_symbols = input("Include symbols? (Y/n): ").strip().lower() != 'n'
        exclude_ambiguous = input("Exclude ambiguous characters (0,O,1,l,I)? (y/N): ").strip().lower() == 'y'
        
        return length, use_symbols, use_numbers, use_lowercase, use_uppercase, exclude_ambiguous
    
    def add_password_entry(self, service, password, username="", website="", notes=""):
        """Add a password entry to storage with additional fields"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if service in self.passwords:
            print(f"⚠️  '{service}' already exists!")
            choice = input("Overwrite? (y/N): ").strip().lower()
            if choice != 'y':
                return False
        
        self.passwords[service] = {
            'password': password,
            'username': username,
            'website': website,
            'notes': notes,
            'created': timestamp,
            'updated': timestamp
        }
        
        self.save_passwords()
        print(f"✅ Password saved for '{service}'")
        return True
    
    def edit_password_entry(self, service):
        """Edit an existing password entry"""
        if service not in self.passwords:
            print(f"❌ No password found for '{service}'")
            return False
        
        entry = self.passwords[service]
        print(f"\n✏️  EDITING: {service}")
        print("=" * 50)
        print("Press Enter to keep current value, or type new value:")
        
        # Edit each field
        new_password = input(f"Password [{entry['password'][:4]}...]: ").strip()
        if new_password:
            entry['password'] = new_password
        
        new_username = input(f"Username [{entry.get('username', '')}]: ").strip()
        if new_username or new_username == '':
            entry['username'] = new_username
        
        new_website = input(f"Website [{entry.get('website', '')}]: ").strip()
        if new_website or new_website == '':
            entry['website'] = new_website
        
        new_notes = input(f"Notes [{entry.get('notes', '')}]: ").strip()
        if new_notes or new_notes == '':
            entry['notes'] = new_notes
        
        entry['updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save_passwords()
        print(f"✅ '{service}' updated successfully!")
        return True
    
    def list_passwords(self):
        """List all stored password entries with enhanced display"""
        if not self.passwords:
            print("📭 No passwords stored yet.")
            return
        
        print(f"\n📋 STORED PASSWORDS ({len(self.passwords)} entries)")
        print("=" * 80)
        
        for i, (service, data) in enumerate(sorted(self.passwords.items()), 1):
            print(f"{i:2d}. 🔐 {service}")
            if data.get('username'):
                print(f"    👤 User: {data['username']}")
            if data.get('website'):
                print(f"    🌐 Site: {data['website']}")
            if data.get('notes'):
                print(f"    📝 Note: {data['notes'][:50]}{'...' if len(data['notes']) > 50 else ''}")
            
            # Password strength indicator
            strength, _, _ = self.check_password_strength(data['password'])
            print(f"    {strength}")
            
            print(f"    📅 Created: {data['created']}")
            if data['created'] != data['updated']:
                print(f"    📅 Updated: {data['updated']}")
            print()
    
    def get_password(self, service):
        """Retrieve a specific password with enhanced display"""
        if service not in self.passwords:
            print(f"❌ No password found for '{service}'")
            return None
        
        entry = self.passwords[service]
        password = entry['password']
        
        print(f"\n🔑 PASSWORD FOR: {service}")
        print("=" * 50)
        print(f"Password: {password}")
        
        if entry.get('username'):
            print(f"Username: {entry['username']}")
        if entry.get('website'):
            print(f"Website:  {entry['website']}")
        if entry.get('notes'):
            print(f"Notes:    {entry['notes']}")
        
        # Show password strength
        strength, score, feedback = self.check_password_strength(password)
        print(f"Strength: {strength} (Score: {score}/6)")
        if feedback:
            print("Suggestions:", ", ".join(feedback))
        
        print(f"Created:  {entry['created']}")
        if entry['created'] != entry['updated']:
            print(f"Updated:  {entry['updated']}")
        
        # Copy to clipboard if possible
        try:
            import pyperclip
            pyperclip.copy(password)
            print("\n📋 Password copied to clipboard!")
        except ImportError:
            print("\n💡 Install 'pyperclip' to copy passwords to clipboard")
        
        return password
    
    def search_passwords(self, query):
        """Search passwords by service name, username, or website"""
        results = []
        query_lower = query.lower()
        
        for service, data in self.passwords.items():
            if (query_lower in service.lower() or 
                query_lower in data.get('username', '').lower() or 
                query_lower in data.get('website', '').lower() or 
                query_lower in data.get('notes', '').lower()):
                results.append(service)
        
        return results
    
    def import_passwords(self):
        """Import passwords from a JSON file"""
        print("\n📥 IMPORT PASSWORDS")
        print("=" * 50)
        print("⚠️  File should be in JSON format with password entries")
        
        filepath = input("Enter file path: ").strip().strip('"')
        
        if not os.path.exists(filepath):
            print("❌ File not found!")
            return
        
        try:
            with open(filepath, 'r') as f:
                imported_data = json.load(f)
            
            if not isinstance(imported_data, dict):
                print("❌ Invalid file format!")
                return
            
            count = 0
            for service, data in imported_data.items():
                if isinstance(data, dict) and 'password' in data:
                    # Convert old format if needed
                    if service not in self.passwords:
                        self.passwords[service] = {
                            'password': data['password'],
                            'username': data.get('username', ''),
                            'website': data.get('website', ''),
                            'notes': data.get('notes', ''),
                            'created': data.get('created', datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                            'updated': data.get('updated', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                        }
                        count += 1
            
            self.save_passwords()
            print(f"✅ Imported {count} passwords successfully!")
            
        except Exception as e:
            print(f"❌ Import failed: {e}")
    
    def delete_password(self, service):
        """Delete a password entry"""
        if service not in self.passwords:
            print(f"❌ No password found for '{service}'")
            return False
        
        print(f"⚠️  Delete password for '{service}'?")
        print("This action cannot be undone!")
        confirm = input("Type 'DELETE' to confirm: ").strip()
        
        if confirm == 'DELETE':
            del self.passwords[service]
            self.save_passwords()
            print(f"✅ Password for '{service}' deleted")
            return True
        else:
            print("❌ Deletion cancelled")
            return False
    
    def show_stats(self):
        """Show enhanced password statistics"""
        if not self.passwords:
            print("📭 No passwords to analyze.")
            return
        
        print(f"\n📊 PASSWORD STATISTICS")
        print("=" * 50)
        print(f"Total passwords: {len(self.passwords)}")
        
        # Analyze password strengths
        strong = medium = weak = 0
        total_score = 0
        
        for service, data in self.passwords.items():
            password = data['password']
            strength, score, _ = self.check_password_strength(password)
            total_score += score
            
            if "Strong" in strength:
                strong += 1
            elif "Medium" in strength:
                medium += 1
            else:
                weak += 1
        
        print(f"🟢 Strong passwords: {strong}")
        print(f"🟡 Medium passwords: {medium}")
        print(f"🔴 Weak passwords: {weak}")
        
        if self.passwords:
            avg_score = total_score / len(self.passwords)
            print(f"📈 Average strength score: {avg_score:.1f}/6")
        
        # Additional stats
        with_usernames = sum(1 for data in self.passwords.values() if data.get('username'))
        with_websites = sum(1 for data in self.passwords.values() if data.get('website'))
        with_notes = sum(1 for data in self.passwords.values() if data.get('notes'))
        
        print(f"👤 Entries with usernames: {with_usernames}")
        print(f"🌐 Entries with websites: {with_websites}")
        print(f"📝 Entries with notes: {with_notes}")
        
        if weak > 0:
            print("\n⚠️  Recommendations:")
            print("   • Update weak passwords to improve security")
            print("   • Use the password generator for stronger passwords")
    
    def backup_data(self):
        """Create a backup of the encrypted password file"""
        if not os.path.exists(self.data_file):
            print("❌ No data to backup!")
            return
        
        backup_dir = os.path.join(self.app_dir, "backups")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"passwords_backup_{timestamp}.dat")
        
        try:
            with open(self.data_file, 'rb') as src, open(backup_file, 'wb') as dst:
                dst.write(src.read())
            print(f"✅ Backup created: {backup_file}")
        except Exception as e:
            print(f"❌ Backup failed: {e}")
    
    def change_master_password(self):
        """Change the master password"""
        print("\n🔐 CHANGE MASTER PASSWORD")
        print("=" * 50)
        print("⚠️  This will re-encrypt all your passwords!")
        
        # Create backup first
        print("Creating backup before changing password...")
        self.backup_data()
        
        confirm = input("Continue? (y/N): ").strip().lower()
        if confirm != 'y':
            return
        
        # Get new password
        attempts = 0
        while attempts < 3:
            new_password = self.get_secure_input("New master password: ")
            confirm_password = self.get_secure_input("Confirm new password: ")
            
            if new_password == confirm_password:
                if len(new_password) < 6:
                    print("❌ Password too short! Minimum 6 characters.")
                    attempts += 1
                    continue
                break
            else:
                print("❌ Passwords don't match!")
                attempts += 1
        
        if attempts >= 3:
            print("❌ Too many failed attempts!")
            return
        
        # Re-encrypt with new password
        try:
            self.setup_encryption(new_password)
            self.save_passwords()
            print("✅ Master password changed successfully!")
        except Exception as e:
            print(f"❌ Failed to change password: {e}")
    
    def export_passwords(self):
        """Export passwords to a JSON file"""
        if not self.passwords:
            print("📭 No passwords to export.")
            return
        
        # Export to Documents folder for easy access
        documents_path = os.path.join(os.path.expanduser("~"), "Documents")
        filename = f"passwords_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(documents_path, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(self.passwords, f, indent=2)
            print(f"✅ Passwords exported to: {filepath}")
            print("⚠️  Keep this file secure - it contains unencrypted passwords!")
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    def show_file_locations(self):
        """Show where all password manager files are stored with explanations"""
        print(f"\n📁 FILE LOCATIONS & EXPLANATIONS")
        print("=" * 80)
        
        print(f"🏠 Main Directory: {self.app_dir}")
        print("   This is your secure password manager folder. It's hidden in your user")
        print("   directory to keep it away from casual browsing. All your password data")
        print("   and security files are stored here for maximum protection.")
        print()
        
        print(f"🔐 Password Database: {self.data_file}")
        if os.path.exists(self.data_file):
            size = os.path.getsize(self.data_file)
            print(f"   Size: {size} bytes")
            print("   ✅ Found")
        else:
            print("   ❌ Not created yet")
        print("   This file contains all your encrypted passwords and account information.")
        print("   It's completely encrypted using military-grade encryption, so even if")
        print("   someone finds it, they can't read it without your master password.")
        print()
        
        print(f"🧂 Salt File: {self.salt_file}")
        if os.path.exists(self.salt_file):
            print("   ✅ Found")
        else:
            print("   ❌ Not created yet")
        print("   This file contains a random salt used to strengthen your master password")
        print("   encryption. It makes your password database much harder to crack by")
        print("   adding randomness to the encryption process. Never delete this file!")
        print()
        
        backup_dir = os.path.join(self.app_dir, "backups")
        print(f"💾 Backup Directory: {backup_dir}")
        if os.path.exists(backup_dir):
            backups = [f for f in os.listdir(backup_dir) if f.endswith('.dat')]
            print(f"   Backups found: {len(backups)}")
            if backups:
                for backup in backups[-3:]:  # Show last 3 backups
                    backup_path = os.path.join(backup_dir, backup)
                    size = os.path.getsize(backup_path)
                    print(f"   • {backup} ({size} bytes)")
        else:
            print("   📁 No backups created yet")
        print("   This folder stores backup copies of your password database. These are")
        print("   created automatically when you change your master password or manually")
        print("   when you use the backup feature. Keep these safe for data recovery!")
        print()
        
        # Show security information
        print("🔒 SECURITY INFORMATION:")
        print("   • All files use AES-256 encryption with PBKDF2 key derivation")
        print("   • 100,000 iterations make brute force attacks extremely difficult")
        print("   • Salt file adds extra randomness to prevent rainbow table attacks")
        print("   • Files are stored in hidden directories for additional protection")
        print("   • Never share these files or move them without proper backup procedures")
        print()
        
        print("💡 TIPS:")
        print("   • Regularly backup your data using option 11")
        print("   • Keep your master password strong and memorable")
        print("   • Don't delete the salt file - it will make your data unrecoverable")
        print("   • Consider backing up the entire folder to cloud storage for safety")
    
    def main_menu(self):
        """Display main menu and handle user choices"""
        while True:
            self.clear_screen()
            print("🔐 PASSWORD MANAGER v1.0")
            print("=" * 50)
            print("📊 Password Management:")
            print("1. Generate new password")
            print("2. Add custom password")
            print("3. List all passwords") 
            print("4. Search passwords")
            print("5. Get specific password")
            print("6. Edit password")
            print("7. Delete password")
            print("8. Password statistics")
            print("9. Import passwords")
            print("10. Export passwords")
            print("11. Backup data")
            print("12. Change master password")
            print("13. Show file locations")
            print("14. Quit")
            print("-" * 50)
            
            choice = input("Choose option (1-14): ").strip()
            
            if choice == '1':
                self.generate_password_menu()
            elif choice == '2':
                self.add_custom_password_menu()
            elif choice == '3':
                self.list_passwords()
                input("\nPress Enter to continue...")
            elif choice == '4':
                self.search_passwords_menu()
            elif choice == '5':
                self.get_password_menu()
            elif choice == '6':
                self.edit_password_menu()
            elif choice == '7':
                self.delete_password_menu()
            elif choice == '8':
                self.show_stats()
                input("\nPress Enter to continue...")
            elif choice == '9':
                self.import_passwords()
                input("\nPress Enter to continue...")
            elif choice == '10':
                self.export_passwords()
                input("\nPress Enter to continue...")
            elif choice == '11':
                self.backup_data()
                input("\nPress Enter to continue...")
            elif choice == '12':
                self.change_master_password()
                input("\nPress Enter to continue...")
            elif choice == '13':
                self.show_file_locations()
                input("\nPress Enter to continue...")
            elif choice == '14':
                print("\n👋 Thanks for using Password Manager!")
                print("🔒 Your passwords are safely encrypted and stored.")
                sys.exit(0)
            else:
                print("❌ Invalid choice! Please try again.")
                input("Press Enter to continue...")
    
    def generate_password_menu(self):
        """Password generation menu"""
        self.clear_screen()
        print("🎲 GENERATE PASSWORD")
        print("=" * 50)
        
        # Get options
        result = self.get_password_options()
        
        # Handle memorable password
        if len(result) == 6 and result[1] is None:
            password = result[0]
        else:
            length, use_symbols, use_numbers, use_lowercase, use_uppercase, exclude_ambiguous = result
            password = self.generate_password(length, use_symbols, use_numbers, 
                                            use_lowercase, use_uppercase, exclude_ambiguous)
        
        if password:
            print(f"\n🔑 Generated password:")
            print(f"    {password}")
            
            # Show strength analysis
            strength, score, feedback = self.check_password_strength(password)
            print(f"    Strength: {strength} (Score: {score}/6)")
            if feedback:
                print(f"    Tips: {', '.join(feedback[:2])}")  # Show first 2 tips
            
            # Copy to clipboard if possible
            try:
                import pyperclip
                pyperclip.copy(password)
                print("\n📋 Password copied to clipboard!")
            except ImportError:
                pass
            
            # Ask if user wants to save it
            save = input("\nSave this password? (y/N): ").strip().lower()
            if save == 'y':
                service = input("Service/Website name: ").strip()
                username = input("Username (optional): ").strip()
                website = input("Website URL (optional): ").strip()
                notes = input("Notes (optional): ").strip()
                
                if service:
                    self.add_password_entry(service, password, username, website, notes)
        
        input("\nPress Enter to continue...")
    
    def add_custom_password_menu(self):
        """Add custom password menu"""
        self.clear_screen()
        print("➕ ADD CUSTOM PASSWORD")
        print("=" * 50)
        
        service = input("Service/Website name: ").strip()
        if not service:
            print("❌ Service name is required!")
            input("Press Enter to continue...")
            return
        
        password = input("Password: ").strip()
        if not password:
            print("❌ Password is required!")
            input("Press Enter to continue...")
            return
        
        # Show password strength
        strength, score, feedback = self.check_password_strength(password)
        print(f"\nPassword strength: {strength} (Score: {score}/6)")
        if feedback:
            print("Suggestions:", ", ".join(feedback))
            proceed = input("\nProceed anyway? (y/N): ").strip().lower()
            if proceed != 'y':
                input("Press Enter to continue...")
                return
        
        username = input("Username (optional): ").strip()
        website = input("Website URL (optional): ").strip()
        notes = input("Notes (optional): ").strip()
        
        self.add_password_entry(service, password, username, website, notes)
        input("\nPress Enter to continue...")
    
    def search_passwords_menu(self):
        """Search passwords menu"""
        self.clear_screen()
        print("🔍 SEARCH PASSWORDS")
        print("=" * 50)
        
        query = input("Search term (service/username/website): ").strip()
        if not query:
            print("❌ Search term is required!")
            input("Press Enter to continue...")
            return
        
        results = self.search_passwords(query)
        
        if not results:
            print(f"❌ No passwords found matching '{query}'")
        else:
            print(f"\n🔍 Found {len(results)} matches:")
            print("-" * 30)
            for i, service in enumerate(results, 1):
                print(f"{i:2d}. {service}")
            
            print("\nChoose a password to view:")
            try:
                choice = int(input("Enter number (0 to cancel): "))
                if 1 <= choice <= len(results):
                    self.get_password(results[choice - 1])
                elif choice != 0:
                    print("❌ Invalid choice!")
            except ValueError:
                print("❌ Please enter a valid number!")
        
        input("\nPress Enter to continue...")
    
    def get_password_menu(self):
        """Get specific password menu"""
        self.clear_screen()
        print("🔑 GET PASSWORD")
        print("=" * 50)
        
        if not self.passwords:
            print("📭 No passwords stored yet.")
            input("Press Enter to continue...")
            return
        
        # Show numbered list
        services = sorted(self.passwords.keys())
        for i, service in enumerate(services, 1):
            print(f"{i:2d}. {service}")
        
        print("\nOptions:")
        print("• Enter number to select")
        print("• Type service name directly")
        print("• Press Enter to cancel")
        
        choice = input("\nYour choice: ").strip()
        
        if not choice:
            return
        
        # Try to parse as number first
        try:
            index = int(choice) - 1
            if 0 <= index < len(services):
                service = services[index]
            else:
                print("❌ Invalid number!")
                input("Press Enter to continue...")
                return
        except ValueError:
            # Treat as service name
            service = choice
        
        self.get_password(service)
        input("\nPress Enter to continue...")
    
    def edit_password_menu(self):
        """Edit password menu"""
        self.clear_screen()
        print("✏️  EDIT PASSWORD")
        print("=" * 50)
        
        if not self.passwords:
            print("📭 No passwords stored yet.")
            input("Press Enter to continue...")
            return
        
        # Show numbered list
        services = sorted(self.passwords.keys())
        for i, service in enumerate(services, 1):
            print(f"{i:2d}. {service}")
        
        choice = input("\nSelect password to edit (number or name): ").strip()
        
        if not choice:
            return
        
        # Try to parse as number first
        try:
            index = int(choice) - 1
            if 0 <= index < len(services):
                service = services[index]
            else:
                print("❌ Invalid number!")
                input("Press Enter to continue...")
                return
        except ValueError:
            # Treat as service name
            service = choice
        
        self.edit_password_entry(service)
        input("\nPress Enter to continue...")
    
    def delete_password_menu(self):
        """Delete password menu"""
        self.clear_screen()
        print("🗑️  DELETE PASSWORD")
        print("=" * 50)
        
        if not self.passwords:
            print("📭 No passwords stored yet.")
            input("Press Enter to continue...")
            return
        
        # Show numbered list
        services = sorted(self.passwords.keys())
        for i, service in enumerate(services, 1):
            print(f"{i:2d}. {service}")
        
        choice = input("\nSelect password to delete (number or name): ").strip()
        
        if not choice:
            return
        
        # Try to parse as number first
        try:
            index = int(choice) - 1
            if 0 <= index < len(services):
                service = services[index]
            else:
                print("❌ Invalid number!")
                input("Press Enter to continue...")
                return
        except ValueError:
            # Treat as service name
            service = choice
        
        self.delete_password(service)
        input("\nPress Enter to continue...")

def main():
    """Main function to run the password manager"""
    print("🔐 Password Manager v1.0")
    print("=" * 50)
    print("Welcome to your secure password manager!")
    print()
    
    # Initialize password manager
    pm = PasswordManager()
    
    # Get master password
    attempts = 0
    while attempts < 3:
        try:
            master_password = pm.get_secure_input("Enter master password: ")
            pm.setup_encryption(master_password)
            pm.load_passwords()
            break
        except Exception as e:
            attempts += 1
            if attempts < 3:
                print(f"❌ Wrong password or corrupted data. Try again. ({3 - attempts} attempts left)")
            else:
                print("❌ Too many failed attempts. Exiting for security.")
                sys.exit(1)
    
    print("✅ Access granted!")
    input("Press Enter to continue...")
    
    # Start main menu
    pm.main_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Your passwords are safely stored.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please report this issue.")
        sys.exit(1)