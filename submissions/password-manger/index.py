import typer
import json
from pathlib import Path
from cryptography.fernet import Fernet
import base64
import hashlib
import getpass
import random
import string
from datetime import datetime

app = typer.Typer()
vault_path = Path("vault.json")


fernet = None


def load_fernet():
    global fernet
    if fernet is None:
        master_password = getpass.getpass("enter your master password:")
        key = get_key(master_password)
        fernet = Fernet(key)


def get_key(password:str):
    return base64.urlsafe_b64encode(
        hashlib.sha256(password.encode()).digest()
    )


@app.command()
def initialize():
    typer.echo("Vault initialized.")


@app.command()
def help():
    typer.echo("""
Password Manager CLI - Commands List:

Commands:
  add <name> <user> <password>     Add a new entry to the password vault.
  get <name>                       Get the username and password for a site.
  delete <name>                    Delete a password entry. (optional)
  list                             List all stored entries. (optional)
  search <query>                   Search entries that contain the query.
  init                             Create a new empty vault. (optional)
  change-master-password           Change the master password for the vault.
  audit                            Check for old passwords.(older than 90 days)
  history <name>                   Show previous passwords for a specific entry.
  help                             Show you this help message

Utilities:
 generate                          Generate a strong password.     
               
Optional Flags for `generate`:
 --length <int>                     Length of the password (default:12)
 --no-digits                        Exclude digits
 --no-uppercase                     Exclude uppercase letters
 --no-symbols                       Exclude symbols                                              


Examples:
  python index.py add github john secret123
  python index.py get github
  python index.py search git
  python index.py delete github
  python index.py list
  python index.py generate --length 16 --no-symbols --no-uppercase
  python index.py change-master-password             
  python index.py audit
  python index.py history github

               
Tips:
- Password are tracked with history . Reusing old ones will show a warning.
- Entry change the last changed date. Use 'audit'to find stale passwords.   
- Use 'history <name>' to view old passwords for account.         
- Use 'audit' to find outdated passwords.
- Use --help after any command to see details.
- Example: python index.py add --help
    """)


@app.command()
def generate(
    length: int = 12,
    digits: bool = typer.Option(True, help = "include digits", show_default = True, is_flag=True),
    uppercase: bool = typer.Option(True, help = "include uppercase", show_default = True, is_flag=True),
    symbols: bool = typer.Option(True, help = "include symbols", show_default = True, is_flag=True) 
):
    chars = string.ascii_lowercase
    if digits:
        chars = chars + string.digits
    if uppercase :
        chars = chars + string.ascii_uppercase   
    if symbols:
        chars = chars + string.punctuation
    if len(chars) == 0:
        typer.echo ("you should allow at least one character.")
        return
    password = ''.join(random.choice(chars) for _ in range(length))         
    typer.echo(f"genrated password:{password}")


@app.command()
def change_master_password():
    global fernet
    old_password = getpass.getpass("enter your current master password:")
    old_key = get_key(old_password)
    old_fernet = Fernet(old_key)
    if not vault_path.exists():
        typer.echo("vault not found")
        return
    try:    
        with open(vault_path,"rb") as f:
            encrypted = f.read()
            decrypted = old_fernet.decrypt(encrypted)
            vault = json.loads(decrypted.decode())
    except Exception:
        typer.echo("Failed to decrypt. the current master password might be wrong")
        return
    new_password = getpass.getpass("enter new master password:")
    confirm_password = getpass.getpass("confirm new master password:")

    if new_password != confirm_password:
        typer.echo("passwords don't match")  
        return

    confirm = input("are you sure you want to change the master password? [y/n]:").lower()

    if confirm != "y":
        typer.echo("operation cancelled.")
        return


    new_key = get_key(new_password)
    new_fernet = Fernet(new_key)
    data = json.dumps(vault).encode()
    new_encrypted = new_fernet.encrypt(data)
    with open(vault_path, "wb") as f:
        f.write(new_encrypted)
    fernet = new_fernet
    typer.echo("master password change successfully.")    


def check_strength(password: str) -> str:
    length = len(password)
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in string.punctuation for c in password )
    score = 0
    if length >= 8 :
        score = score + 1
    if has_upper:
        score = score + 1
    if has_digit:
        score = score + 1
    if has_symbol:
        score = score + 1
    if score == 4:
        return "strength: very strong"
    elif score == 3:
        return "strength: strong"    
    elif score == 2:
        return "strength: medium"
    else:
        return "strength: weak. tips: use at least 8 character, add uppercase, digits, and symbols."                        


@app.command()
def add(name: str, user: str, password: str):

    load_fernet()
    vault = {}

    if  vault_path.exists():
        with open(vault_path, "rb") as f:
            encrypted = f.read()
            try:
                decrypted = fernet.decrypt(encrypted)
                vault = json.loads(decrypted.decode())
            except Exception:
                typer.echo("faild to decrypt. the vault is encrypted or is the master password is wrong")
                return

    entry = vault.get(name)

    if entry:
        history = entry.get("history", [])
        current_password = entry["password"]
        if password == current_password :
            typer.echo("this is the same password already stored.")
            return
        elif password in history:
            typer.echo("you have used this password before.")

        history.append(current_password)

        vault[name] = {
            "username": user,
            "password": password,
            "history": history,
            "last_changed": datetime.now().strftime("%Y-%m-%d") 
        }
        typer.echo(f"updated password for {name}")

    else:
        vault[name] = {
            "username": user,
            "password": password,
            "history": [],
            "last_changed": datetime.now().strftime("%Y-%m-%d") 
        }    

        typer.echo(f"add new entry for {name}")

    typer.echo(check_strength(password))
    data = json.dumps(vault).encode()
    encrypted = fernet.encrypt(data)

    with open(vault_path, "wb") as f:
        f.write(encrypted)

    typer.echo(f"Saved password for {name}")
    typer.echo(f"Username: {user}")
    typer.echo(f"Password: {password}")


@app.command()
def history(name:str):
    load_fernet()
    if not vault_path.exists:
        typer.echo("vault not found")
        return

    with open(vault_path, "rb") as f:
        encrypted = f.read()


    try:
        decrypted = fernet.decrypt(encrypted)
        vault = json.loads(decrypted.decode())
    except Exception:
        typer.echo("Faild to decrypt vault. wrong master password.")
        return

    entry = vault.get(name)
    if not entry:
        typer.echo(f"no entry found for {name}")   
        return
    typer.echo(f"\nPassword history for {name}")
    typer.echo(f"- Current password: {entry['password']}")
    typer.echo(f"- Last changet: {entry.get('last_changed',"UnKnown")}")

    history = entry.get("history", [])
    if history:
        typer.echo(f"- Previous passwords ({len(history)}):")
        for i, p in enumerate (history, 1):
            typer.echo(f"   {i}. {p}")
    else:
        typer.echo("no previous passwords stored.")             


@app.command()
def audit():
    load_fernet()
    if not vault_path.exists():
        typer.echo("vault not found ")
        return
    with open(vault_path, "rb") as f:
        encrypted = f.read()
    try:
        decrypted = fernet.decrypt(encrypted)
        vault = json.loads(decrypted.decode())
    except Exception:
        typer.echo("faild to decrypt vault. wrong master password?")
        return
    today = datetime.now()
    outdated_count = 0

    typer.echo("auditing stored password:\n")

    for name, entry in vault.items():
        changed_on = entry.get("last_changed")
        if not changed_on:
            typer.echo(f"{name}: no date info available.")
            continue
        last_changed = datetime.strptime(changed_on, "%Y-%m-%d")
        age_days = (today - last_changed).days

        if age_days > 90:
            typer.echo(f"{name}: password is {age_days} days old consider changing it.")
            outdated_count = outdated_count + 1
        else:
            typer.echo(f"{name}: password is {age_days} days old")
    typer.echo(f"\nAudit complete. {outdated_count} password(s) need updating.")        


@app.command()
def search(query:str):
    load_fernet()
    if not vault_path.exists():
        typer.echo("the vault not found")
        return
    with open(vault_path, "rb") as f:
        encrypted = f.read()
    try:
        decrypted = fernet.decrypt(encrypted)
        vault = json.loads(decrypted.decode())
    except Exception:
        typer.echo("faild to decrypt the vault. wrong password?")
        return
    
    found = False
    for name, credential in vault.items():
        if query.lower() in name.lower():
            typer.echo(f"found:{name}")
            typer.echo(f"username:{credential['username']}")
            typer.echo(f"password:{credential['password']}")
            found = True
    if not found:
        typer.echo(f"no entry matching'{query}'found.")    


@app.command()
def get(name:str):
    load_fernet()
    if vault_path.exists():
        with open(vault_path, "rb") as f:
            encrypted = f.read()
            try:
                decrypted = fernet.decrypt(encrypted)
                vault = json.loads(decrypted.decode( ))
            except Exception as e:
                typer.echo("faild to decrypt the vault. wrong password?")
                return

        if name in vault:
            typer.echo(f"username: {vault[name]['username']}")
            typer.echo(f"password: {vault[name]['password']}")
        else:
            typer.echo(f"no entry found for {name}")
    else:
        typer.echo (f"vault not found")                


@app.command()
def delete(name:str):
    load_fernet()
    if vault_path.exists():
        try:
            with open(vault_path, "rb") as f:
                encrypted = f.read()
                decrypted = fernet.decrypt(encrypted)
                vault = json.loads(decrypted.decode())
        except Exception:
            typer.echo("failed to decrypt the vault. wrong master password?")    
            return    
        if name in vault:
            del vault[name]
            data = json.dumps(vault).encode()
            encrypted = fernet.encrypt(data)
            with open (vault_path, "wb") as f:
                f.write(encrypted)
            typer.echo(f"delete entry of {name}")
        else:
            typer.echo(f"no entry found for {name}")
    else:
        typer.echo(f"no vault found")                    


@app.command(name="list")
def list_entries ():
    load_fernet()
    if vault_path.exists():
        with open(vault_path, "rb")as f:
            encrypted =f.read()
            decrypted = fernet.decrypt(encrypted)
            vault = json.loads(decrypted.decode())
        if not vault:
            typer.echo("the vault empty")  
            return
        list_number=1      
        for name in vault:
            typer.echo(f"{list_number}-{name}")
            list_number=list_number+1
    else:            
        typer.echo("the vault is not found")

if __name__ == "__main__":
    app()   
