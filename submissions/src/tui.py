from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Input, Button, Static, Label
from .utils import check_port, validate_port, traceroute, whois

class SocketPeekApp(App):
    CSS = """
    Screen {
        background: #1f1f1f;
    }

    #main-container {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }
    
    #input-form {
        margin-bottom: 1;
        border: solid $background-lighten-2;
        padding: 1;
        background: $panel;
        height: auto;
    }
    
    #form-title {
        text-align: center;
        background: $boost;
        padding: 1;
        width: 100%;
        margin-bottom: 1;
    }
    
    .input-container {
        width: 100%;
        margin-bottom: 1;
        height: auto;
        layout: grid;
        grid-size: 2;
        grid-columns: 30% 70%;
        padding: 0 1;
    }
    
    .input-label {
        padding-top: 1;
    }
    
    #button-container {
        margin-top: 1;
        align: center middle;
        width: 100%;
        height: auto;
        layout: grid;
        grid-size: 3;
        grid-gutter: 1 2;
        padding: 0 1;
    }
    
    #result-area {
        border: solid $background-lighten-2;
        padding: 1;
        height: 1fr;
        background: $panel;
    }
    
    #result-title {
        text-align: center;
        background: $boost;
        padding: 1;
        width: 100%;
        margin-bottom: 1;
    }
    
    #result-content {
        margin: 1;
        padding: 1;
        height: 1fr;
        overflow-y: auto;
        min-height: 20;
    }
    
    #result-container {
        height: 1fr;
        overflow: auto;
    }
    
    .success {
        color: #0f0;
    }
    
    .error {
        color: #f00;
    }
    
    .info {
        color: #0ff;
    }
    
    .action-button {
        width: 100%;
        min-width: 10;
    }

    .action-button:hover {
        background: $accent;
    }

    Screen > Container {
        height: 100%;
        overflow: hidden;
    }

    #port-input, #host-input, #timeout-input {
        width: 100%;
    }

    Vertical > Static {
        height: auto;
    }

    .mode-indicator {
        text-align: right;
        color: #0ff;
        margin-right: 1;
    }
    """

    def compose(self) -> ComposeResult:
        
        yield Header(show_clock=True)
        
        with Container(id="main-container"):
            with Vertical(id="input-form"):
                yield Label("Socket Connection Checker", id="form-title")
                
                with Container(id="host-row", classes="input-container"):
                    yield Label("Host:", classes="input-label")
                    yield Input(placeholder="Enter hostname or IP", id="host-input", classes="input-field")
                
                with Container(id="port-row", classes="input-container"):
                    yield Label("Port:", classes="input-label")
                    yield Input(placeholder="Enter port number (1-65535)", id="port-input", classes="input-field")
                
                with Container(id="timeout-row", classes="input-container"):
                    yield Label("Timeout:", classes="input-label")
                    yield Input(placeholder="Seconds", value="3.0", id="timeout-input", classes="input-field")
                
                with Container(id="button-container"):
                    yield Button("Check Port", variant="primary", id="check-button", classes="action-button")
                    yield Button("Traceroute", variant="default", id="trace-button", classes="action-button")
                    yield Button("WHOIS", variant="default", id="whois-button", classes="action-button")
            
            with Container(id="result-area"):
                yield Label("Results", id="result-title")
                with ScrollableContainer(id="result-container"):
                    yield Static("Enter connection details and press a button", id="result-content", classes="info")
        
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "check-button":
            self.check_connection()
        elif event.button.id == "trace-button":
            self.run_traceroute()
        elif event.button.id == "whois-button":
            self.run_whois()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.check_connection()

    def check_connection(self) -> None:
        host = self.query_one("#host-input").value
        port = self.query_one("#port-input").value
        timeout_str = self.query_one("#timeout-input").value
        result_display = self.query_one("#result-content")
        
        if not host:
            result_display.update("ERROR: Please enter a hostname or IP address")
            result_display.styles.color = "red"
            return
        
        if not port:
            result_display.update("ERROR: Please enter a port number")
            result_display.styles.color = "red"
            return
        
        try:
            timeout = float(timeout_str) if timeout_str else 3.0
        except ValueError:
            result_display.update(f"ERROR: Invalid timeout value: {timeout_str}. Please enter a valid number.")
            result_display.styles.color = "red"
            return
        
        try:
            port_num = validate_port(port)
        except ValueError as e:
            result_display.update(f"ERROR: {str(e)}")
            result_display.styles.color = "red"
            return
        
        result_display.update(f"Checking {host}:{port_num} (timeout: {timeout}s)...")
        result_display.styles.color = "blue"
        
        check_result = check_port(host, port_num, timeout)
        
        if isinstance(check_result, tuple):
            _, error_msg = check_result
            result_display.update(f"CLOSED: Port {port_num} on {host} is closed\nReason: {error_msg}")
            result_display.styles.color = "red"
        elif check_result:
            result_display.update(f"OPEN: Port {port_num} on {host} is open and accepting connections")
            result_display.styles.color = "green"
        else:
            result_display.update(f"CLOSED: Port {port_num} on {host} is closed")
            result_display.styles.color = "red"
    
    def run_traceroute(self) -> None:
        host = self.query_one("#host-input").value
        timeout_str = self.query_one("#timeout-input").value
        result_display = self.query_one("#result-content")
        
        result_display.update("")
        
        if not host:
            result_display.update("ERROR: Please enter a hostname or IP address")
            result_display.styles.color = "red"
            return
        
        try:
            timeout = float(timeout_str) if timeout_str else 3.0
        except ValueError:
            result_display.update(f"ERROR: Invalid timeout value: {timeout_str}. Please enter a valid number.")
            result_display.styles.color = "red"
            return
        
        result_display.update(f"Running traceroute to {host}...\nThis may take some time, please wait...")
        result_display.styles.color = "blue"
        
        trace_result = traceroute(host, max_hops=30, timeout=timeout)
        
        if not trace_result:
            result_display.update(f"ERROR: Traceroute to {host} failed.")
            result_display.styles.color = "red"
            return
            
        if trace_result and "error" in trace_result[0] and trace_result[0]["error"] and trace_result[0]["hop"] == 0:
            error_msg = trace_result[0]["error"]
            result_display.update(f"ERROR: {error_msg}")
            result_display.styles.color = "red"
            return
        
        output = []
        output.append(f"Traceroute to {host}:")
        output.append("-" * 50)
        output.append(f"{'Hop':<5} {'IP Address':<16} {'Time':<10} {'Status'}")
        output.append("-" * 50)
        
        for hop in trace_result:
            hop_num = hop["hop"]
            ip = hop["ip"] or "*"
            hostname = hop["hostname"] or ""
            
            if hop["time"] is not None:
                time_ms = f"{hop['time']:.2f} ms"
            else:
                time_ms = "---"
            
            if hop["error"]:
                status = f"[{hop['error']}]"
                hop_class = "hop-timeout"
            elif not hop["ip"]:
                status = "[No response]"
                hop_class = "hop-timeout"
            else:
                status = "[OK]"
                hop_class = "hop-success"
            
            if hop_class == "hop-timeout":
                output.append(f"{hop_num:<5} {ip:<16} {time_ms:<10} {status}")
            else:
                output.append(f"{hop_num:<5} {ip:<16} {time_ms:<10} {status}")
                
                if hostname and hostname != ip:
                    output.append(f"      {hostname}")
        
        output.append("-" * 50)
        output.append(f"Trace complete. {len(trace_result)} hops traversed.")
        
        result_display.update("\n".join(output))
        result_display.styles.color = "white"

    def run_whois(self) -> None:
        host = self.query_one("#host-input").value
        result_display = self.query_one("#result-content")
        
        result_display.update("")
        
        if not host:
            result_display.update("ERROR: Please enter a hostname or IP address")
            result_display.styles.color = "red"
            return
        
        result_display.update(f"Running WHOIS lookup for {host}...\nThis may take some time, please wait...")
        result_display.styles.color = "blue"
        
        whois_result = whois(host)
        
        if not whois_result or "Error" in whois_result:
            result_display.update(f"ERROR: WHOIS lookup for {host} failed.\n\n{whois_result}")
            result_display.styles.color = "red"
            return
        
        output = []
        output.append(f"WHOIS Information for {host}:")
        output.append("-" * 50)
        output.append(whois_result)
        
        result_display.update("\n".join(output))
        result_display.styles.color = "white"

def main():
    app = SocketPeekApp()
    app.run()

if __name__ == "__main__":
    main()
