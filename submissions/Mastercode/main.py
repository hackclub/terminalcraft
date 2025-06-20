import urwid # main framework this time, curses = bad
import datetime
import os
import json
from cryptography.fernet import Fernet #ez peazy lemon squeazy reliable, first thing that came up when i searched for encrypting
import csv
import cowsay
import io
import contextlib
import re
import random
import string

data_file = 'data/passwords.json'
key_file = 'data/key.key'
master_password_file = 'data/master_password.key'
settings_file = 'data/settings.json'
diary_file = 'data/diary.json'
# Ensure the data directory exists, Credits to josias for talking about the issue.
if not os.path.exists("data"):
    os.makedirs("data")
def load_diary():
    if os.path.exists(diary_file):
        with open(diary_file, 'r') as f:
            return json.load(f)
    else:
        return {}
def save_diary_entry(date, entry):
    settings = load_settings()
    diary = load_diary()
    encrypted_entry = cipher.encrypt(entry.encode()).decode()
    
    if settings.get('allow_duplicate_entries', True):
        if date in diary:
            # using unique identifier, like some random unicode because what if some bloke tryna slip a name by accident like XxGamerBoy2011DiaryEntryXx!!!!
            counter = 1
            new_date = f"{date}{counter}"
            while new_date in diary:
                counter += 1
                new_date = f"{date}{counter}"
            diary[new_date] = encrypted_entry
        else:
            diary[date] = encrypted_entry
    else:
        diary[date] = encrypted_entry
    
    save_diary(diary)
    diary_menu()

def delete_diary_entry(date):
    diary = load_diary()
    if date in diary:
        del diary[date]
        save_diary(diary)
    diary_menu()

def load_settings(): # default settings incase file don't exist, otherwise load it
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            return json.load(f)
    else:
        return {'password_length': 20, 'allow_duplicate_entries': True}
def save_diary(diary):
    with open(diary_file, 'w') as f:
        json.dump(diary, f)
def save_settings(settings):
    with open(settings_file, 'w') as f:
        json.dump(settings, f)
        main_menu() #Hopefully you're not using this somewhere else

def load_key():
    if os.path.exists(key_file):
        with open(key_file, 'rb') as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, 'wb') as f:
            f.write(key)
        return key

def load_passwords(): #if it exists, it loads, but if not? no
    if os.path.exists(data_file):
        with open(data_file, 'r') as f:
            return json.load(f)
    else:
        return {}

def save_passwords(passwords): #it says it in the function!!!
    with open(data_file, 'w') as f:
        json.dump(passwords, f)

def load_master_password(): 
    if os.path.exists(master_password_file):
        with open(master_password_file, 'rb') as f:
            encrypted_master_password = f.read()
            return cipher.decrypt(encrypted_master_password).decode()
    else:
        return None

def save_master_password(password): # first time use, after that, never again
    encrypted_master_password = cipher.encrypt(password.encode())
    with open(master_password_file, 'wb') as f:
        f.write(encrypted_master_password)

#the backbone
key = load_key()
cipher = Fernet(key)
passwords = load_passwords()
master_password = load_master_password()

def show_or_exit(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

def styled_button(caption, callback):
    button = urwid.Button(caption)
    urwid.connect_signal(button, 'click', callback)
    button = urwid.AttrMap(button, None, focus_map='focus')
    return urwid.Padding(urwid.LineBox(button, title=""), left=1, right=1)

def simple_button(caption, callback):
    button = urwid.Button(caption)
    urwid.connect_signal(button, 'click', callback)
    return urwid.Padding(button, left=1, right=1)

def submenu(title): # relic, do not touch
    update_header(f"{title} Submenu")
    text = urwid.Text(f"This is the {title} submenu.")
    back_button = styled_button("Back", main_menu)
    layout.body = urwid.AttrMap(urwid.Filler(urwid.Pile([text, back_button])), 'body')

def main_menu(button=None):
    update_header("Main Menu")
    button1 = styled_button("Add Password", add_password)
    button2 = styled_button("View Passwords", view_passwords)
    button3 = styled_button("Export Passwords", export_passwords)
    button4 = styled_button("Import Passwords", import_passwords)
    button5 = styled_button("Check on Passy", check_passy)
    button7 = styled_button("Settings", settings_menu) # when you add feature but gotta stuff it in somewhere
    button8 = styled_button("Exit", exit_program)
    button6 = styled_button("Diary", diary_menu)
    layout.body = urwid.AttrMap(urwid.ListBox(urwid.SimpleFocusListWalker([button1, button2, button3, button4, button5, button6, button7, button8])), 'body')

def settings_menu(button=None):
    update_header("Settings")
    settings = load_settings()
    password_length_edit = urwid.Edit("Generated Password Length: ", str(settings.get('password_length', 20)))
    allow_duplicates_checkbox = urwid.CheckBox("Allow Duplicate Entries", state=settings.get('allow_duplicate_entries', True))
    
    save_button = styled_button("Save", lambda button: save_settings({
        'password_length': int(password_length_edit.get_edit_text()),
        'allow_duplicate_entries': allow_duplicates_checkbox.get_state()
    }))
    back_button = styled_button("Back", main_menu)
    
    layout.body = urwid.AttrMap(urwid.Filler(urwid.Pile([
        password_length_edit,
        allow_duplicates_checkbox,
        save_button,
        back_button
    ])), 'body')

def generate_password():
    settings = load_settings()
    length = settings.get('password_length', 20)
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(characters) for i in range(length))

def add_password(button=None):
    update_header("Add Password")
    site_edit = urwid.Edit("Site: ")
    username_edit = urwid.Edit("Username: ")
    password_edit = urwid.Edit("Password: ", mask='●')
    note_edit = urwid.Edit("Note: ")
    strength_text = urwid.Text("Password Strength: ")
    strength_bar = urwid.Text("▁▁▁▁▁▁▁▁▁▁") # initial, i counted it, 10 underscores
    urwid.connect_signal(password_edit, 'change', lambda edit, new_edit_text: update_strength_bar(new_edit_text, strength_bar, strength_text))
    
    generate_button = styled_button("Generate Password", lambda button: password_edit.set_edit_text(generate_password()))
    save_button = styled_button("Save", lambda button: save_password(site_edit.get_edit_text(), username_edit.get_edit_text(), password_edit.get_edit_text(), note_edit.get_edit_text()))
    back_button = styled_button("Back", main_menu)
    
    layout.body = urwid.AttrMap(urwid.Filler(urwid.Pile([ # just wing it
        site_edit,
        username_edit,
        password_edit,
        
        strength_text,
        strength_bar,
        note_edit,
        generate_button,
        save_button,
        back_button
    ])), 'body')
def calculate_password_strength(password): # next update, we're turning it into a nodejs module
    length = len(password)
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'\W', password))
    
    strength = 0
    if length >= 8:
        strength += 1
    if has_upper:
        strength += 1
    if has_lower:
        strength += 1
    if has_digit:
        strength += 1
    if has_special:
        strength += 1
    
    return strength

def update_strength_bar(password, strength_bar, strength_text):
    strength = calculate_password_strength(password)
    if strength == 0:
        strength_text.set_text("Password Strength: Very Weak")
        strength_bar.set_text(('very_weak', "▁▁▁▁▁▁▁▁▁▁"))
    elif strength == 1:
        strength_text.set_text("Password Strength: Weak")
        strength_bar.set_text(('weak', "▆▆▁▁▁▁▁▁▁▁"))
    elif strength == 2:
        strength_text.set_text("Password Strength: Fair")
        strength_bar.set_text(('fair', "▆▆▆▁▁▁▁▁▁▁"))
    elif strength == 3:
        strength_text.set_text("Password Strength: Good")
        strength_bar.set_text(('good', "▆▆▆▆▁▁▁▁▁▁"))
    elif strength == 4:
        strength_text.set_text("Password Strength: Strong")
        strength_bar.set_text(('strong', "▆▆▆▆▆▆▆▆▁▁"))
    elif strength == 5:
        strength_text.set_text("Password Strength: Very Strong")
        strength_bar.set_text(('verystrong', "▆▆▆▆▆▆▆▆▆▆"))

def save_password(site, username, password, note):
    encrypted_password = cipher.encrypt(password.encode()).decode()
    encrypted_note = cipher.encrypt(note.encode()).decode()
    passwords[site] = {'username': username, 'password': encrypted_password, 'note': encrypted_note}
    save_passwords(passwords)
    main_menu()

def view_passwords(button=None): # update, define, layout
    update_header("View Passwords")
    password_list = []
    for site, data in passwords.items():
        decrypted_password = cipher.decrypt(data['password'].encode()).decode()
        decrypted_note = cipher.decrypt(data['note'].encode()).decode() if 'note' in data else ''
        password_text = urwid.Text(f"{site}: {data['username']} - {'●' * len(decrypted_password)} - Note: {decrypted_note}")
        toggle_button = styled_button("Show", lambda button, t=password_text, p=decrypted_password: toggle_password(t, p))
        edit_button = styled_button("Edit", lambda button, s=site: edit_password(s))
        delete_button = styled_button("Delete", lambda button, s=site: confirm_delete_password(s))
        password_list.append(urwid.Columns([password_text, toggle_button, edit_button, delete_button]))
    back_button = styled_button("Back", main_menu)
    layout.body = urwid.AttrMap(urwid.ListBox(urwid.SimpleFocusListWalker(password_list + [back_button])), 'body')

def toggle_password(text_widget, password):
    current_text = text_widget.get_text()[0]
    if '●' in current_text:
        text_widget.set_text(current_text.replace('●' * len(password), password))
    else:
        text_widget.set_text(current_text.replace(password, '●' * len(password)))


def edit_password(site): # simple to decrypt, simple to edit, nothing complciated here.
    update_header("Edit Password")
    data = passwords[site]
    decrypted_password = cipher.decrypt(data['password'].encode()).decode()
    decrypted_note = cipher.decrypt(data['note'].encode()).decode() if 'note' in data else ''
    site_edit = urwid.Edit("Site: ", site)
    username_edit = urwid.Edit("Username: ", data['username'])
    password_edit = urwid.Edit("Password: ", decrypted_password, mask='●')
    note_edit = urwid.Edit("Note: ", decrypted_note)
    
    generate_button = styled_button("Generate Password", lambda button: password_edit.set_edit_text(generate_password()))
    save_button = styled_button("Save", lambda button: save_password(site_edit.get_edit_text(), username_edit.get_edit_text(), password_edit.get_edit_text(), note_edit.get_edit_text()))
    back_button = styled_button("Back", view_passwords)
    
    layout.body = urwid.AttrMap(urwid.Filler(urwid.Pile([
        site_edit,
        username_edit,
        password_edit,
        
        note_edit,
        generate_button,
        save_button,
        back_button
    ])), 'body')
def add_diary_entry(button=None): # its more advanced than some of the password mechanisms (lies)
    update_header("Add Diary Entry")
    date_edit = urwid.Edit("Date (YYYY-MM-DD): ", datetime.datetime.now().strftime("%Y-%m-%d"))
    entry_edit = urwid.Edit("Entry:\n", multiline=True)
    save_button = styled_button("Save", lambda button: save_diary_entry(date_edit.get_edit_text(), entry_edit.get_text()[0]))
    back_button = styled_button("Back", diary_menu)
    layout.body = urwid.AttrMap(urwid.Filler(urwid.Pile([
        date_edit,
        entry_edit,
        save_button,
        back_button
    ])), 'body')

def view_diary_entry(date): 
    update_header("View Diary Entry")
    diary = load_diary()
    decrypted_entry = cipher.decrypt(diary[date].encode()).decode()
    entry_edit = urwid.Edit("Entry:\n", decrypted_entry, multiline=True)
    save_button = styled_button("Save", lambda button: save_diary_entry(date, entry_edit.get_text()[0]))
    back_button = styled_button("Back", diary_menu)
    layout.body = urwid.AttrMap(urwid.Filler(urwid.Pile([
        urwid.Text(f"Date: {date.split('')[0]}"), # display date and use unicode for truncating
        entry_edit,
        save_button,
        back_button
    ])), 'body')

def diary_menu(button=None): # deletion support, viewing, adding
    update_header("Diary")
    diary = load_diary()
    diary_list = []
    for date, entry in diary.items():
        decrypted_entry = cipher.decrypt(entry.encode()).decode()
        display_date = date.split('')[0]
        entry_text = urwid.Text(f"{display_date}: {decrypted_entry[:30]}...")
        view_button = styled_button("View", lambda button, d=date: view_diary_entry(d))
        delete_button = styled_button("Delete", lambda button, d=date: delete_diary_entry(d))
        diary_list.append(urwid.Columns([entry_text, view_button, delete_button]))
    add_button = styled_button("Add Entry", add_diary_entry)
    back_button = styled_button("Back", main_menu)
    layout.body = urwid.AttrMap(urwid.ListBox(urwid.SimpleFocusListWalker(diary_list + [add_button, back_button])), 'body')

def confirm_delete_password(site):
    update_header("Confirm Delete")
    confirm_text = urwid.Text(f"Are you sure you want to delete the password for {site}?")
    yes_button = styled_button("Yes", lambda button: delete_password(site))
    no_button = styled_button("No", view_passwords)
    layout.body = urwid.AttrMap(urwid.Filler(urwid.Pile([confirm_text, yes_button, no_button])), 'body')

def delete_password(site):
    del passwords[site]
    save_passwords(passwords)
    view_passwords()

def export_passwords(button=None):
    update_header("Export Passwords")
    file_manager(export=True)

def import_passwords(button=None):
    update_header("Import Passwords")
    file_manager(export=False)

def file_manager(export=True, current_dir=None, file_type=None): # display with simple 1 column per entry, don't list files, only .csv
    if current_dir is None:
        current_dir = os.path.expanduser("~")
    dir_list = os.listdir(current_dir)
    dir_list = [d for d in dir_list if os.path.isdir(os.path.join(current_dir, d))]
    file_list = [f for f in os.listdir(current_dir) if os.path.isfile(os.path.join(current_dir, f)) and f.endswith('.csv')] if not export else []
    items = [urwid.Text(f"Current directory: {current_dir}")]
    for d in dir_list:
        items.append(simple_button(d, lambda button, d=d: navigate_directory(os.path.join(current_dir, d), export, file_type)))
    for f in file_list:
        items.append(simple_button(f, lambda button, f=f: select_file(os.path.join(current_dir, f))))
    if export and file_type:
        filename_edit = urwid.Edit("Filename: ")
        save_button = styled_button("Save Here", lambda button: export_to_file(file_type, os.path.join(current_dir, filename_edit.get_edit_text() + '.' + file_type)))
        items.append(urwid.Divider())
        items.append(filename_edit)
        items.append(save_button)
    elif export:
        file_type_buttons = urwid.Columns([
            styled_button("CSV", lambda button: file_manager(export=True, current_dir=current_dir, file_type='csv')),
            styled_button("TXT", lambda button: file_manager(export=True, current_dir=current_dir, file_type='txt'))
        ])
        items.append(urwid.Divider())
        items.append(file_type_buttons)
    back_button = simple_button("Back", lambda button: navigate_directory(os.path.dirname(current_dir), export, file_type))
    items.append(back_button)
    layout.body = urwid.AttrMap(urwid.ListBox(urwid.SimpleFocusListWalker(items)), 'body')

def navigate_directory(directory, export, file_type):
    file_manager(export, current_dir=directory, file_type=file_type)

def select_file(filepath):
    import_from_file(filepath)

def export_to_file(file_type, filename): # chromium compatible, try importing to chromium.
    if file_type == 'txt':
        with open(filename, 'w') as f:
            for site, data in passwords.items():
                decrypted_password = cipher.decrypt(data['password'].encode()).decode()
                decrypted_note = cipher.decrypt(data['note'].encode()).decode() if 'note' in data else ''
                f.write(f"{site}: {data['username']} - {decrypted_password} - {decrypted_note}\n")
    elif file_type == 'csv':
        with open(filename, 'w') as f:
            f.write("name,url,username,password,note\n")
            for site, data in passwords.items():
                decrypted_password = cipher.decrypt(data['password'].encode()).decode()
                decrypted_note = cipher.decrypt(data['note'].encode()).decode() if 'note' in data else ''
                f.write(f"{site},{site},{data['username']},{decrypted_password},{decrypted_note}\n")
    main_menu()

def import_from_file(filename): # chromium csv format compatible, tested
    if filename.endswith('.csv'):
        with open(filename, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                site = row['url']
                username = row['username']
                password = row['password']
                note = row.get('note', '')
                encrypted_password = cipher.encrypt(password.encode()).decode()
                encrypted_note = cipher.encrypt(note.encode()).decode()
                passwords[site] = {'username': username, 'password': encrypted_password, 'note': encrypted_note}
        save_passwords(passwords)
    main_menu()

def exit_program(button):
    raise urwid.ExitMainLoop()

def update_time(loop=None, data=None): #date takes too much space, time is more needed
    now = datetime.datetime.now().strftime("%H:%M:%S") # hour, minute, second
    time_text.set_text(now)
    main_loop.set_alarm_in(1, update_time)

def check_terminal_size(loop=None, data=None):
    global last_size
    size = main_loop.screen.get_cols_rows()
    if size != last_size:
        if size[0] < 75 or size[1] < 25:
            warning = urwid.Text(
                u'Terminal size is too small!\n'
                u'Resize to a minimum of 75x25.\n'
                u'Current size: {}x{}'.format(size[0], size[1]),
                align='center'
            )
            main_loop.widget = urwid.Filler(warning)
        else:
            main_loop.widget = layout
        last_size = size
    main_loop.set_alarm_in(1, check_terminal_size)

def password_prompt(first_time=False, confirm=False):
    update_header("Password prompt")
    if first_time:
        if confirm:
            prompt_text = "Confirm master password: "
        else:
            prompt_text = "Set master password: "
    else:
        prompt_text = "Enter master password: "
    password_edit = urwid.Edit(prompt_text, mask='●')
    submit_button = styled_button("Submit", lambda button: verify_password(password_edit.get_edit_text(), first_time, confirm))
    layout.body = urwid.AttrMap(urwid.Filler(urwid.Pile([password_edit, submit_button])), 'body')

def verify_password(input_password, first_time=False, confirm=False):
    global master_password
    if first_time:
        if confirm:
            if input_password == master_password:
                save_master_password(input_password)
                main_menu()
            else:
                error_text = urwid.Text("Passwords do not match. Try again.")
                retry_button = styled_button("Retry", lambda button: password_prompt(first_time=True))
                layout.body = urwid.AttrMap(urwid.Filler(urwid.Pile([error_text, retry_button])), 'body')
        else:
            master_password = input_password
            password_prompt(first_time=True, confirm=True)
    else:
        if input_password == master_password:
            main_menu()
        else:
            error_text = urwid.Text("Incorrect password. Try again.")
            retry_button = styled_button("Retry", lambda button: password_prompt())
            layout.body = urwid.AttrMap(urwid.Filler(urwid.Pile([error_text, retry_button])), 'body')

def custom_cow(message, eyes="oo"): # plastic surgery, but for cows
    with io.StringIO() as buf, contextlib.redirect_stdout(buf):
        cowsay.cow(message)
        cow_output = buf.getvalue()
    
    cow_output = cow_output.replace("oo", eyes, 1) # only way to do it fast
    return cow_output

def check_passy(button=None): # passy = password dude, don't mispronounce it
    update_header("Check on Passy")
    num_passwords = len(passwords)
    avg_strength = sum(calculate_password_strength(cipher.decrypt(data['password'].encode()).decode()) for data in passwords.values()) / num_passwords if num_passwords > 0 else 0
    if num_passwords == 0:
        message = "I'm hungry, create or import some passwords!"
        eyes = "oo"
    elif avg_strength < 2:
        message = "Why are your passwords so weak? I'm sad."
        eyes = ";;"
    elif num_passwords > 5:
        message = "You sure do have a bunch of passwords, are you sure you can remember them?"
        eyes = "⸜⸝"
    else:
        message = "Yippie! your passwords are strong!"
        eyes = "^^"
    passy_message = custom_cow(message, eyes=eyes) # customized eyes
    passy_text = urwid.Text(passy_message)
    back_button = styled_button("Back", main_menu)
    layout.body = urwid.AttrMap(urwid.Filler(urwid.Pile([passy_text, back_button])), 'body')

def update_header(menu_name):
    global current_menu
    current_menu = menu_name
    header_text.set_text(f'{current_menu}')


palette = [ # hate this, but its easier to organize, no need to pull colors out of a hat
    ('header', 'white', 'dark red'),
    ('footer', 'white', 'dark blue'),
    ('body', 'light gray', 'black'),
    ('focus', 'black', 'light gray'),

    ('very_weak', 'dark red', ''),
    ('weak', 'light red', ''),
    ('fair', 'yellow', ''),
    ('good', 'light green', ''),
    ('strong', 'dark blue', ''),
    ('verystrong', 'dark magenta', ''), # no purple color so magenta will have to do

    #('color1', 'light red', ''), diary colouring didnt work out.
    #('color2', 'light green', ''),
    #('color3', 'light blue', ''),
    #('color4', 'light magenta', '')
]

header_text = urwid.Text(u'Password Manager', align='left')
time_text = urwid.Text(u'', align='right')
header = urwid.AttrMap(urwid.Columns([
    header_text,
    time_text
]), 'header')

footer = urwid.Text(u'Press (q) to quit', align='center')

layout = urwid.Frame(
    header=header,
    body=urwid.AttrMap(urwid.Text(u'Loading...', align='center'), 'body'),
    footer=urwid.AttrMap(footer, 'footer')
)

main_loop = urwid.MainLoop(layout, palette, unhandled_input=show_or_exit)

last_size = main_loop.screen.get_cols_rows()

main_loop.set_alarm_in(1, check_terminal_size)
main_loop.set_alarm_in(1, update_time)

if master_password is None:
    password_prompt(first_time=True)
else:
    password_prompt()

main_loop.run()
