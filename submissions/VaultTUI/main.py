from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Button, Static, Input, Label
from textual.message import Message
from textual.events import Key
import getpass
from vault import delete_entry, search_entries
from utils import (
    load_vault,
    save_vault,
    generate_key,
    validate_master_password,
    get_entry,
    delete_entry_manual,
    search_entries_manual,
    export_vault_to_csv  # Added export
)


class Sidebar(Vertical):
    def compose(self) -> ComposeResult:
        yield Static("\U0001F510 VaultTUI", classes="title")
        yield Button("\u2795 Add", id="add")
        yield Button("\U0001F441\uFE0F View", id="view")
        yield Button("\U0001F5D1\uFE0F Delete", id="delete")
        yield Button("\U0001F50D Search", id="search")
        yield Button("\U0001F4BE Export", id="export")
        yield Button("\U0001F3E0 Home", id="home")


class AddEntryForm(Container):
    class Submit(Message):
        def __init__(self, sender, name, url, username, password) -> None:
            super().__init__()
            self.sender = sender
            self.name = name
            self.url = url
            self.username = username
            self.password = password

    def compose(self) -> ComposeResult:
        self.password_input = Input(placeholder="Password", password=True, id="entry-password")
        yield Label("\U0001F510 Add New Entry", id="form-title")
        yield Input(placeholder="Entry name", id="entry-name")
        yield Input(placeholder="Website URL (optional)", id="entry-url")
        yield Input(placeholder="Username", id="entry-username")
        yield self.password_input
        yield Button("\U0001F441 Show", id="toggle-password")
        yield Horizontal(
            Button("\u2705 Save", id="submit"),
            Button("\U0001F3E0 Home", id="home")
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "submit":
            name = self.query_one("#entry-name", Input).value
            url = self.query_one("#entry-url", Input).value
            username = self.query_one("#entry-username", Input).value
            password = self.query_one("#entry-password", Input).value
            self.post_message(self.Submit(self, name, url, username, password))
        elif event.button.id == "toggle-password":
            self.password_input.password = not self.password_input.password


class VaultApp(App):
    CSS_PATH = "tui.css"

    def __init__(self, key: bytes):
        super().__init__()
        self.key = key

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Sidebar(id="sidebar"),
            Container(id="main-content"),
            id="main"
        )
        yield Footer()

    def on_mount(self):
        self.show_welcome()

    def on_key(self, event: Key):
        if event.key == "escape":
            self.exit()
        elif event.key == "/":
            self.show_search_form()
        elif event.key == "enter":
            try:
                view_input = self.query_one("#view-name", Input)
                if view_input.has_focus:
                    self.on_button_pressed(Button.Pressed(Button(id="view-submit")))
            except:
                pass

    def show_welcome(self):
        self.query_one("#main-content", Container).remove_children()
        self.query_one("#main-content", Container).mount(
            Vertical(
                Static("\U0001F44B Welcome to VaultTUI!", id="welcome-msg"),
                Button("\u2795 Add Entry", id="add"),
                Button("\U0001F441\uFE0F View Entry", id="view"),
                Button("\U0001F5D1\uFE0F Delete Entry", id="delete"),
                Button("\U0001F50D Search Entry", id="search"),
                Button("\U0001F4BE Export Vault", id="export")
            )
        )

    def show_add_form(self):
        self.query_one("#main-content", Container).remove_children()
        self.query_one("#main-content", Container).mount(AddEntryForm())

    def show_view_form(self):
        self.query_one("#main-content", Container).remove_children()
        self.query_one("#main-content", Container).mount(
            Vertical(
                Input(placeholder="Enter entry name", id="view-name"),
                Horizontal(
                    Button("\U0001F441 View", id="view-submit"),
                    Button("\U0001F3E0 Home", id="home")
                )
            )
        )

    def show_delete_form(self):
        self.query_one("#main-content", Container).remove_children()
        self.query_one("#main-content", Container).mount(
            Vertical(
                Input(placeholder="Enter entry name", id="delete-name"),
                Horizontal(
                    Button("\U0001F5D1\uFE0F Delete", id="delete-submit"),
                    Button("\U0001F3E0 Home", id="home")
                )
            )
        )

    def show_search_form(self):
        self.query_one("#main-content", Container).remove_children()
        self.query_one("#main-content", Container).mount(
            Vertical(
                Input(placeholder="Search keyword", id="search-keyword"),
                Horizontal(
                    Button("\U0001F50D Search", id="search-submit"),
                    Button("\U0001F3E0 Home", id="home")
                )
            )
        )

    def on_button_pressed(self, event: Button.Pressed):
        btn_id = event.button.id
        if btn_id == "add":
            self.show_add_form()
        elif btn_id == "view":
            self.show_view_form()
        elif btn_id == "delete":
            self.show_delete_form()
        elif btn_id == "search":
            self.show_search_form()
        elif btn_id == "export":
            vault = load_vault(self.key)
            export_vault_to_csv(vault)
            self.query_one("#main-content", Container).remove_children()
            self.query_one("#main-content", Container).mount(
                Vertical(
                    Static("\U0001F4BE Vault exported to vault_export.csv."),
                    Button("\U0001F3E0 Home", id="home")
                )
            )
        elif btn_id == "home":
            self.show_welcome()
        elif btn_id == "view-submit":
            name = self.query_one("#view-name", Input).value
            vault = load_vault(self.key)
            entry = vault.get(name)
            self.query_one("#main-content", Container).remove_children()
            if entry:
                self.query_one("#main-content", Container).mount(
                    Vertical(
                        Static(f"\U0001F510 {name}:\nURL: {entry.get('url', '')}\nUsername: {entry['username']}\nPassword: {entry['password']}"),
                        Button("\U0001F3E0 Home", id="home")
                    )
                )
            else:
                self.query_one("#main-content", Container).mount(
                    Vertical(
                        Static(f"\u274C Entry '{name}' not found."),
                        Button("\U0001F3E0 Home", id="home")
                    )
                )
        elif btn_id == "delete-submit":
            name = self.query_one("#delete-name", Input).value
            vault = load_vault(self.key)
            success = delete_entry_manual(name, vault)
            self.query_one("#main-content", Container).remove_children()
            if success:
                save_vault(vault, self.key)
                self.query_one("#main-content", Container).mount(
                    Vertical(
                        Static(f"\U0001F5D1\uFE0F Entry '{name}' deleted."),
                        Button("\U0001F3E0 Home", id="home")
                    )
                )
            else:
                self.query_one("#main-content", Container).mount(
                    Vertical(
                        Static(f"\u274C Entry '{name}' not found."),
                        Button("\U0001F3E0 Home", id="home")
                    )
                )
        elif btn_id == "search-submit":
            keyword = self.query_one("#search-keyword", Input).value
            vault = load_vault(self.key)
            results = search_entries_manual(keyword, vault)
            self.query_one("#main-content", Container).remove_children()
            if results:
                output = "\n".join(f"\U0001F539 {k}: {v['username']}" for k, v in results.items())
                self.query_one("#main-content", Container).mount(
                    Vertical(
                        Static(f"\U0001F50D Search results:\n{output}"),
                        Button("\U0001F3E0 Home", id="home")
                    )
                )
            else:
                self.query_one("#main-content", Container).mount(
                    Vertical(
                        Static("\u274C No matching entries found."),
                        Button("\U0001F3E0 Home", id="home")
                    )
                )

    def on_add_entry_form_submit(self, msg: AddEntryForm.Submit):
        vault = load_vault(self.key)
        if msg.name in vault:
            self.query_one("#main-content", Container).mount(
                Vertical(
                    Static(f"\u26A0\uFE0F Entry '{msg.name}' already exists."),
                    Button("\U0001F3E0 Home", id="home")
                )
            )
        else:
            vault[msg.name] = {
                "url": msg.url,
                "username": msg.username,
                "password": msg.password
            }
            save_vault(vault, self.key)
            self.query_one("#main-content", Container).remove_children()
            self.query_one("#main-content", Container).mount(
                Vertical(
                    Static(f"\u2705 Entry '{msg.name}' added!"),
                    Button("\U0001F3E0 Home", id="home")
                )
            )


def main():
    pw = getpass.getpass("Enter master password: ")
    if not validate_master_password(pw):
        print("\u274C Incorrect master password.")
        return
    key = generate_key(pw)
    app = VaultApp(key)
    app.run()


if __name__ == "__main__":
    main()
