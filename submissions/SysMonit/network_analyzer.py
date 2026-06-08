import socket
import subprocess
import platform
import psutil
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress
import threading

class NetworkAnalyzer:
    def __init__(self):
        self.console = Console()
        self.system = platform.system()

    def get_network_interfaces(self):
        interfaces = []
        net_if_addrs = psutil.net_if_addrs()
        net_if_stats = psutil.net_if_stats()
        
        for interface, addresses in net_if_addrs.items():
            stats = net_if_stats.get(interface)
            interface_info = {
                'name': interface,
                'is_up': stats.isup if stats else False,
                'addresses': []
            }
            
            for addr in addresses:
                if addr.family == socket.AF_INET:
                    interface_info['addresses'].append(f"IPv4: {addr.address}")
                elif addr.family == socket.AF_INET6:
                    interface_info['addresses'].append(f"IPv6: {addr.address}")
                elif hasattr(socket, 'AF_PACKET') and addr.family == socket.AF_PACKET:
                    interface_info['addresses'].append(f"MAC: {addr.address}")
                elif self.system == "Windows" and addr.family == -1:
                    interface_info['addresses'].append(f"MAC: {addr.address}")
            
            interfaces.append(interface_info)
        
        return interfaces

    def show_network_info(self):
        self.console.print("\n[bold cyan]Network Interfaces[/bold cyan]")
        
        interfaces = self.get_network_interfaces()
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Interface", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Addresses", style="dim")

        for interface in interfaces:
            status = "🟢 UP" if interface['is_up'] else "🔴 DOWN"
            addresses = "\n".join(interface['addresses']) if interface['addresses'] else "No addresses"
            
            table.add_row(
                interface['name'],
                status,
                addresses
            )

        self.console.print(table)

    def scan_ports(self, host, start_port=1, end_port=1000):
        open_ports = []
        
        def scan_port(port):
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((host, port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except:
                pass

        threads = []
        for port in range(start_port, end_port + 1):
            thread = threading.Thread(target=scan_port, args=(port,))
            threads.append(thread)
            thread.start()
            
            if len(threads) > 50:
                for t in threads:
                    t.join()
                threads = []

        for t in threads:
            t.join()

        return sorted(open_ports)

    def show_port_scan(self):
        host = Prompt.ask("\n[bold]Enter host to scan[/bold]", default="127.0.0.1")
        start_port = Prompt.ask("[bold]Start port[/bold]", default="1")
        end_port = Prompt.ask("[bold]End port[/bold]", default="1000")
        
        try:
            start_port = int(start_port)
            end_port = int(end_port)
        except ValueError:
            self.console.print("[red]Invalid port numbers![/red]")
            return

        self.console.print(f"\n[bold yellow]Scanning {host} ports {start_port}-{end_port}...[/bold yellow]")
        
        with self.console.status("[bold green]Scanning ports..."):
            open_ports = self.scan_ports(host, start_port, end_port)

        if not open_ports:
            self.console.print("[green]No open ports found[/green]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Port", justify="center", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Service", style="dim")

        common_ports = {
            21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
            80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 993: "IMAPS",
            995: "POP3S", 3389: "RDP", 5432: "PostgreSQL", 3306: "MySQL"
        }

        for port in open_ports:
            service = common_ports.get(port, "Unknown")
            table.add_row(str(port), "🟢 OPEN", service)

        panel = Panel(table, title=f"[bold]Open Ports on {host}[/bold]", border_style="green")
        self.console.print(panel)

    def ping_host(self, host, count=4):
        results = []
        
        if self.system == "Windows":
            cmd = ["ping", "-n", str(count), host]
        else:
            cmd = ["ping", "-c", str(count), host]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                lines = stdout.split('\n')
                for line in lines:
                    if 'time=' in line.lower() or 'zeit=' in line.lower():
                        results.append(line.strip())
                return True, results
            else:
                return False, [stderr.strip()]
                
        except Exception as e:
            return False, [str(e)]

    def show_ping_test(self):
        host = Prompt.ask("\n[bold]Enter host to ping[/bold]", default="google.com")
        count = Prompt.ask("[bold]Number of pings[/bold]", default="4")
        
        try:
            count = int(count)
        except ValueError:
            count = 4

        self.console.print(f"\n[bold yellow]Pinging {host}...[/bold yellow]")
        
        success, results = self.ping_host(host, count)
        
        if success:
            self.console.print(f"[green]✓ {host} is reachable[/green]")
            for result in results:
                self.console.print(f"  {result}")
        else:
            self.console.print(f"[red]✗ {host} is unreachable[/red]")
            for result in results:
                self.console.print(f"  {result}")

    def get_active_connections(self):
        connections = []
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'ESTABLISHED':
                    local_addr = f"{conn.laddr.ip}:{conn.laddr.port}"
                    remote_addr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                    
                    try:
                        process = psutil.Process(conn.pid) if conn.pid else None
                        process_name = process.name() if process else "Unknown"
                    except:
                        process_name = "Unknown"
                    
                    connections.append({
                        'local': local_addr,
                        'remote': remote_addr,
                        'status': conn.status,
                        'process': process_name,
                        'pid': conn.pid or 0
                    })
        except:
            pass
        
        return connections

    def show_active_connections(self):
        self.console.print("\n[bold cyan]Active Network Connections[/bold cyan]")
        
        with self.console.status("[bold green]Getting connections..."):
            connections = self.get_active_connections()

        if not connections:
            self.console.print("[yellow]No active connections found[/yellow]")
            return

        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Local Address", style="cyan")
        table.add_column("Remote Address", style="yellow")
        table.add_column("Status", justify="center")
        table.add_column("Process", style="dim")
        table.add_column("PID", justify="right")

        for conn in connections[:20]:
            table.add_row(
                conn['local'],
                conn['remote'],
                "🟢 " + conn['status'],
                conn['process'],
                str(conn['pid'])
            )

        self.console.print(table)

    def show_network_menu(self):
        menu_text = """
[bold green]1.[/bold green] Network Interfaces
[bold green]2.[/bold green] Port Scanner
[bold green]3.[/bold green] Ping Test
[bold green]4.[/bold green] Active Connections
[bold red]0.[/bold red] Back to Main Menu
        """
        
        panel = Panel(
            menu_text.strip(),
            title="[bold]Network Analyzer[/bold]",
            border_style="cyan"
        )
        self.console.print(panel)

    def run(self):
        while True:
            self.console.clear()
            self.show_network_menu()
            
            choice = Prompt.ask(
                "\n[bold]Select option[/bold]",
                choices=["0", "1", "2", "3", "4"],
                default="0"
            )
            
            if choice == "0":
                break
            elif choice == "1":
                self.show_network_info()
            elif choice == "2":
                self.show_port_scan()
            elif choice == "3":
                self.show_ping_test()
            elif choice == "4":
                self.show_active_connections()
            
            if choice != "0":
                input("\nPress Enter to continue...")