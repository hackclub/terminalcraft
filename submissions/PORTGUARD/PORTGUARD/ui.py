from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static, Input, Button
from textual.reactive import reactive
from textual.containers import Container, Vertical, Horizontal  # Add Horizontal
import asyncio
import csv
from datetime import datetime
from monitor import get_ports, get_process_info, kill_process_by_pid

class PortGuardApp(App):
    CSS_PATH = "style.css"
    BINDINGS = [("q", "quit", "Quit")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield Static("ACTIVE Connections:", id="status")
        yield Button("Export CSV", id="export")
        yield Input(placeholder="Filter (PID/IP/Status)", id="filter")
        yield DataTable(id="table")
        yield Static("Details:", id="details")

    async def on_mount(self) -> None:
        self.status = self.query_one("#status", Static)
        self.filter_input = self.query_one("#filter", Input)
        self.details = self.query_one("#details", Static)
        self.export_button = self.query_one("#export", Button)
        self.table = self.query_one(DataTable)
        self.column_names = ["PID", "Local Address", "Remote Address", "Status"]
        self.column_widths = [8, 22, 22, 12]

        for name, width in zip(self.column_names, self.column_widths):
            self.table.add_column(name, width=width)

        self.table.cursor_type = "row"
        self.sort_column = "PID"
        self.sort_ascending = True
        self.table.add_class("sortable")
        self.connections = []
        await self.refresh_ports()
        self.set_interval(3, self.refresh_ports)

    def _center(self, text: str, width: int) -> str:
        if len(text) >= width:
            return text[:width]
        padding = width - len(text)
        left = padding // 2
        right = padding - left
        return "\u00A0" * left + text + "\u00A0" * right

    async def refresh_ports(self):
        self.table.clear()

        ports = get_ports()
        self.connections = []
        for status, items in ports.items():
            for item in items:
                self.connections.append([
                    str(item["pid"]),
                    item["laddr"],
                    item["raddr"],
                    item["status"]
                ])

        # Filter
        query = self.filter_input.value.strip().lower()
        rows = self.connections
        if query:
            rows = [row for row in rows if any(query in cell.lower() for cell in row)]

        # Sorting
        col_index = {"PID": 0, "Local Address": 1, "Remote Address": 2, "Status": 3}[self.sort_column]

        def sort_key(row):
            if col_index == 0:
                try:
                    return int(row[col_index])
                except ValueError:
                    return 0
            return row[col_index] or ""

        rows.sort(key=sort_key, reverse=not self.sort_ascending)

        for row in rows:
            padded = [self._center(cell, width) for cell, width in zip(row, self.column_widths)]
            self.table.add_row(*padded)

        self.status.update(f"Active Connections: {len(rows)}")

    async def on_data_table_header_selected(self, event: DataTable.HeaderSelected) -> None:
        column_map = {
            0: "PID",
            1: "Local Address",
            2: "Remote Address",
            3: "Status"
        }

        column_index = event.column_index
        column_name = column_map.get(column_index)

        if column_name:
            if self.sort_column == column_name:
                self.sort_ascending = not self.sort_ascending
            else:
                self.sort_column = column_name
                self.sort_ascending = True
            await self.refresh_ports()

    async def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.row_key is None:
            self.details.update("No row selected")
            return

        try:
            row = self.table.get_row(event.row_key)
        except Exception:
            self.details.update("Selected row is invalid")
            return

        pid_str = row[0].strip()
        try:
            pid = int(pid_str)
            info = get_process_info(pid)
            self.details.update(f"PID {pid}: {info}")
        except Exception as e:
            self.details.update(f"Error fetching info: {e}")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "export":
            with open("ports_export.csv", "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(self.column_names)
                for row in self.connections:
                    writer.writerow(row)
            self.status.update("Exported to ports_export.csv")

    async def on_input_changed(self, event: Input.Changed) -> None:
        await self.refresh_ports()