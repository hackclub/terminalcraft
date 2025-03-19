from textual.app import ComposeResult, RenderResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widget import Widget
from textual.widgets import Button, Collapsible, Input, Label, Select, TextArea
import requests

from postperson import Binding
from postperson.modals import DeleteConfirmation, ErrorModal
from postperson.validators import url_validator

from pathlib import Path
import mimetypes


class ErrorWidget(Widget):
    DEFAULT_CSS = """
    ErrorWidget {
        border: $secondary tall;
        height: 3;
        padding: 0 2;
        display: none;
    }
    """

    def __init__(self, error: str = ""):
        super().__init__()

        self.error = error

    def render(self) -> RenderResult:
        if self.error:
            return f"[red]Error:[/red] {self.error}"
        return ""

    def update(self, error: str) -> None:
        self.error = error
        self.styles.display = "block" if error else "none"
        self.refresh()


class HeaderHolder(VerticalScroll):
    DEFAULT_CSS = """
    HeaderHolder {
        overflow-y: scroll;
        min-height: 10;
        max-height: 20;
        border: $secondary wide;
    }
    """
    def __init__(self, data: dict) -> None:
        self.data = data

        super().__init__(id="header-scroll")

    def on_mount(self) -> None:
        self.build()

    def build(self):
        self.remove_children()
        for i, (key, value) in enumerate(self.data.items()):
            self.mount(HeaderRow(key, value, i))

    def update_data(self, data: dict) -> None:
        self.data = data
        self.build()
        self.refresh()


class HeaderRow(Horizontal):
    def __init__(self, key: str, value: str, index: int) -> None:
        self.key = key
        self.value = value
        self.index = index

        super().__init__(classes="header-row" + ("-first" if self.index == 0 else ""))

    def compose(self) -> ComposeResult:
        yield Label(f"[b]{self.key}[/]: {self.value}")
        yield Button("Delete", id="header-delete")

    def update(self, key, value) -> None:
        self.key = key
        self.value = value
        self.refresh()

class RequestWidget(Widget):
    BINDINGS = [
        Binding(";", "send_request", "Send"),
    ]

    with open(Path(__file__).parent / "css/request_widget.tcss") as f:
        DEFAULT_CSS = f.read()

    def __init__(self, request_data, id) -> None:
        super().__init__()
        self.request_data = request_data
        self.req_id = id

    def _set_unsaved_edit(self):
        if isinstance(self.parent, RequestHolder):
            setattr(self.parent.parent, "unsaved_edit", True)

    def _delete_req(self, result: int) -> None:
        if result:
            if isinstance(self.parent, RequestHolder):
                self.parent.requests.pop(self.req_id)
                self.parent.update(self.parent.requests)

                # doing self.parent.parent.unsaved_edit made pyright complain
                # "waa waa its not a known attribute :(" yeah shut up
                self._set_unsaved_edit()


    def compose(self) -> ComposeResult:
        self.scroller = HeaderHolder(self.request_data.get("headers", {}));
        with Horizontal(id="request-container"):
            with Collapsible(title=self.request_data.get("name", "Name"), id="collapsible"):
                yield Input(self.request_data.get("name", "Name"), id="name")
                yield Label("Request", id="request")
                with Horizontal(id="request-row"):
                    yield Select(
                        [(method, method) for method in ["GET", "POST", "PUT", "DELETE"]],
                        id="method",
                        value=self.request_data.get("method", "GET")
                    )

                    yield Input(self.request_data.get("url", ""), placeholder="URL", id="url")

                with Collapsible(id="headers", title="Headers", classes="gapped-collapse"):
                    with Horizontal(id="header-inp"):
                        yield Input(placeholder="Key", id="header-key")
                        yield Input(placeholder="Value", id="header-value")
                        yield Button("Add", id="add-header")

                    yield self.scroller

                yield Label("Body")
                yield TextArea.code_editor(
                    self.request_data.get("body", ""), 
                    id="body",
                    language="json",
                    tab_behavior="indent",
                    show_line_numbers=True,
                    theme="vscode_dark"
                )

                with Collapsible(id="response", title="Response", classes="gapped-collapse"):
                    yield Label(id="response-status")
                    with Collapsible(title="Body", id="body-container", classes="gapped-collapse"):
                        yield TextArea.code_editor(
                            id="response-body",
                            language="json",
                            read_only=True,
                            theme="vscode_dark"
                        )

            with Vertical(id="button-col"):
                yield Button("Delete", id="delete")
                yield Button("Send", id="send")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "delete":
            # I have no idea why pyright doesn't fw this
            self.app.push_screen(DeleteConfirmation(), callback=self._delete_req)  # pyright: ignore
        elif event.button.id == "send":
            self.action_send_request()
        elif event.button.id == "add-header":
            self.action_add_header()
        elif event.button.id == "header-delete":
            headers = self.request_data.get("headers", {})

            if isinstance(event.button.parent, HeaderRow):
                key = event.button.parent.key
                headers.pop(key)

                self.request_data["headers"] = headers
                self.scroller.update_data(headers)
                self._set_unsaved_edit()

    def action_add_header(self):
        key = self.query_one("#header-key", Input).value
        value = self.query_one("#header-value", Input).value

        if not key or not value:
            self.app.push_screen(ErrorModal("Key and Value must not be empty"))
            return

        headers = self.request_data.get("headers", {})
        headers[key] = value
        self.request_data["headers"] = headers

        self.scroller.update_data(headers)
        self._set_unsaved_edit()

    def action_send_request(self):
        method = self.request_data.get("method", "GET")
        url = self.request_data.get("url", "URL")
        if not url_validator(url):
            self.app.push_screen(ErrorModal("Invalid URL"))
            return

        headers = self.request_data.get("headers", {})
        body = self.request_data.get("body", "")

        response = requests.request(method, url, headers=headers, data=body)
        response_block = self.query_one("#response", Collapsible)
        response_block.styles.display = "block"
        
        response_text = response.text

        response_block.query_one("#response-status", Label).update(f"Status: {response.status_code}")

        text_area = response_block.query_one("#response-body", TextArea)

        with open('abc.txt', 'w') as f:
            f.write(str(dict(response.headers)))

        mime_type = response.headers.get("Content-Type", "text/plain").split(';')[0].strip() # cuz charset fricks this up sometimes
        extension = mimetypes.guess_extension(mime_type)

        text_area.language = extension[1:] if extension else "text"
        text_area.load_text(response_text)

    def on_input_changed(self, event: Input.Changed) -> None:
         self.request_data[event.input.id] = event.input.value
         self.update()
         self._set_unsaved_edit()

    def on_text_area_changed(self, event: TextArea.Changed) -> None:
        self.request_data["body"] = event.text_area.text
        self._set_unsaved_edit()

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "method":
            self.request_data["method"] = event.select.value
            self.update()
            self._set_unsaved_edit()

    def update(self) -> None:
        collapsible = self.query_one("#collapsible", Collapsible)
        if collapsible:
            collapsible.title = self.request_data.get("name", "Name")

        self.refresh()

    def compile(self) -> dict:
        return {
            "name": self.query_one("#name", Input).value,
            "method": self.query_one("#method", Select).value,
            "url": self.query_one("#url", Input).value,
            "headers": self.request_data.get("headers", {}),
            "body": self.query_one("#body", TextArea).text
        }


class RequestHolder(Widget):
    DEFAULT_CSS = """
    RequestHolder {
        overflow-y: scroll;
    }
    """

    def __init__(self, requests: list | None = None) -> None:
        self.requests = requests or []

        super().__init__()

    def compose(self) -> ComposeResult:
        for i, request in enumerate(self.requests):
            yield RequestWidget(request, i)

    def update(self, requests: list) -> None:
        self.requests = requests
        self.remove_children()
        for i, request in enumerate(self.requests):
            self.mount(RequestWidget(request, i))

        self.refresh()

    def compile(self) -> list:
        return [child.compile() for child in self.children if isinstance(child, RequestWidget)]

