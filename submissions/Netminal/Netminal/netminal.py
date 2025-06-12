import os
import re
import socket
import statistics
import subprocess
import threading
import time
import platform
import psutil
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich import box
from rich.text import Text

_cache = {
    'network': {
        'download': "Not measured yet",
        'upload': "Not measured yet",
        'ping': "Not measured yet",
        'jitter': "Not measured yet",
        'packet_loss': "Not measured yet",
        'local_ip': None,
        'public_ip': None,
        'timestamp': 0,
        'in_progress': False,
        'ping_in_progress': False,
        'jitter_in_progress': False
    },
    'wifi_name': {'name': None, 'timestamp': 0},
    'data_usage': {
        'session_start': time.time(),
        'download_start': 0,
        'upload_start': 0,
        'last_check': time.time(),
        'download_current': 0,
        'upload_current': 0
    }
}

try:
    import speedtest
    SPEEDTEST_AVAILABLE = True
except ImportError:
    SPEEDTEST_AVAILABLE = False

console = Console()

def run_cmd(cmd, split_lines=False, timeout=2, shell=False):
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, shell=shell)
        return result.stdout.splitlines() if split_lines and result.returncode == 0 else \
               result.stdout if result.returncode == 0 else None
    except:
        return None

def colorize_value(value, type):
    if type == "percent":
        try:
            num_value = float(value.replace("%", ""))
            if num_value < 30:
                return f"[green]{value}[/green]"
            elif num_value < 70:
                return f"[yellow]{value}[/yellow]"
            else:
                return f"[red]{value}[/red]"
        except:
            return value
    
    elif type == "ping":
        if "No connection" in value or "Measuring" in value or "failed" in value:
            return value
        try:
            num_value = float(value.split()[0])
            if num_value < 20:
                return f"[green]{value}[/green]"
            elif num_value < 80:
                return f"[yellow]{value}[/yellow]"
            else:
                return f"[red]{value}[/red]"
        except:
            return value
    
    elif type == "jitter":
        if "No connection" in value or "Measuring" in value or "failed" in value:
            return value
        try:
            num_value = float(value.split()[0])
            if num_value < 5:
                return f"[green]{value}[/green]"
            elif num_value < 20:
                return f"[yellow]{value}[/yellow]"
            else:
                return f"[red]{value}[/red]"
        except:
            return value
    
    elif type == "packet_loss":
        if "No connection" in value or "Measuring" in value or "failed" in value:
            return value
        try:
            num_value = float(value.replace("%", ""))
            if num_value < 1:
                return f"[green]{value}[/green]"
            elif num_value < 5:
                return f"[yellow]{value}[/yellow]"
            else:
                return f"[red]{value}[/red]"
        except:
            return value
    
    elif type == "speed":
        if "No connection" in value or "Measuring" in value or "failed" in value:
            return value
        try:
            num_value = float(value.split()[0])
            if num_value > 50:
                return f"[green]{value}[/green]"
            elif num_value > 10:
                return f"[yellow]{value}[/yellow]"
            else:
                return f"[red]{value}[/red]"
        except:
            return value
    
    return value

def internet_connected(test_full=False):
    for dns in ["8.8.8.8", "1.1.1.1", "9.9.9.9"]:
        try:
            socket.create_connection((dns, 53), timeout=1)
            return ("✅ Connected", "green") if test_full else True
        except:
            continue
    
    try:
        socket.create_connection(("www.google.com", 80), timeout=1)
        return ("✅ Connected", "green") if test_full else True
    except:
        return ("❌ Disconnected", "red") if test_full else False

def test_internet_connection():
    return internet_connected(test_full=True)

def is_ethernet_connected():
    system = platform.system()
    
    if system == "Darwin":
        interfaces = run_cmd(["networksetup", "-listallhardwareports"], split_lines=True)
        if not interfaces:
            return False
            
        ethernet_interfaces = []
        current_port = None
        for line in interfaces:
            if "Hardware Port:" in line:
                current_port = line.split(":", 1)[1].strip()
            elif "Device:" in line and current_port and "Ethernet" in current_port and "Wi-Fi" not in current_port:
                ethernet_interfaces.append(line.split(":", 1)[1].strip())
                
        for interface in ethernet_interfaces:
            ifconfig = run_cmd(["ifconfig", interface], split_lines=True)
            if ifconfig and "status: active" in " ".join(ifconfig).lower() and "inet " in " ".join(ifconfig):
                return True
    
    elif system == "Windows":
        netsh = run_cmd(["netsh", "interface", "show", "interface"], split_lines=True)
        if netsh and any("Connected" in line and "Ethernet" in line for line in netsh):
            return True
    
    elif system == "Linux":
        ip_out = run_cmd(["ip", "addr"], split_lines=True)
        if ip_out:
            current_iface = ""
            for line in ip_out:
                if ":" in line and "<" in line and ">" in line:
                    current_iface = line.strip().split(":")[1].strip()
                if current_iface and (current_iface.startswith(("eth", "en")) and "wl" not in current_iface):
                    if "inet " in line and "UP" in line:
                        return True
    
    return False

def get_wifi_name():
    cache = _cache['wifi_name']
    
    if cache['name'] and time.time() - cache['timestamp'] < 30:
        return cache['name']
    
    if is_ethernet_connected():
        name = "Using Ethernet"
        cache['name'] = name
        cache['timestamp'] = time.time()
        return name
    
    system = platform.system()
    name = None
    
    if system == "Darwin":
        airport_path = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"
        if os.path.exists(airport_path):
            try:
                airport_out = run_cmd([airport_path, "--getinfo"], split_lines=True, timeout=3)
                if airport_out:
                    for line in airport_out:
                        if " SSID:" in line:
                            name = line.split("SSID:")[1].strip()
                            break
            except:
                pass
    
    elif system == "Windows":
        try:
            netsh_out = run_cmd(["netsh", "wlan", "show", "interfaces"], split_lines=True, timeout=3)
            if netsh_out:
                for line in netsh_out:
                    if "SSID" in line and "BSSID" not in line:
                        name = line.split(":", 1)[1].strip()
                        if name:
                            break
        except:
            pass
    
    elif system == "Linux":
        try:
            ssid = run_cmd(["iwgetid", "-r"], timeout=3)
            if ssid and ssid.strip():
                name = ssid.strip()
        except:
            pass
    
    name = name or ("Connected Network" if internet_connected() else "No connection")
    
    cache['name'] = name
    cache['timestamp'] = time.time()
    return name

def get_local_ip():
    cache = _cache['network']
    
    if cache['local_ip'] and time.time() - cache['timestamp'] < 300:
        return cache['local_ip']
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            cache['local_ip'] = local_ip
            return local_ip
    except:
        try:
            hostname = socket.gethostname()
            addresses = socket.getaddrinfo(hostname, None)
            for addr in addresses:
                ip = addr[4][0]
                if not ip.startswith('127.') and ':' not in ip:
                    cache['local_ip'] = ip
                    return ip
        except:
            pass
        
    return "Not detected"

def get_public_ip():
    cache = _cache['network']
    
    if cache['public_ip'] and time.time() - cache['timestamp'] < 300:
        return cache['public_ip']
    
    for service in ["https://api.ipify.org", "https://ifconfig.me/ip", "https://icanhazip.com"]:
        try:
            result = run_cmd(f"curl -s {service}", shell=True, timeout=3)
            if result and re.match(r'\d+\.\d+\.\d+\.\d+', result.strip()):
                cache['public_ip'] = result.strip()
                return cache['public_ip']
        except:
            continue
    
    return "Not detected"

def get_wifi_details():
    system = platform.system()
    ssid = get_wifi_name()
    
    details = {"security": "Unknown", "band": "Unknown", "signal": "unknown"}
    
    if ssid == "No connection" or not internet_connected():
        return ("No connection", "No connection", "____ No signal")
    
    if ssid == "Using Ethernet":
        return ("Wired connection (secure)", "Not applicable", "Wired (stable)")
    
    details["security"] = details["security"] if details["security"] != "Unknown" else "WPA2/WPA3 (typical)"
    details["band"] = details["band"] if details["band"] != "Unknown" else "2.4/5 GHz"
    
    if details["signal"] == "unknown":
        if internet_connected():
            details["signal"] = "good"
        else:
            details["signal"] = "none"
    
    signal_map = {
        "excellent": "▂▄▆█ Excellent",
        "good": "▂▄▆_ Good",
        "fair": "▂▄__ Fair",
        "poor": "▂___ Poor",
        "none": "____ None"
    }
    signal_display = signal_map.get(details["signal"], "_▆▄█▂ Unknown")
    
    return details["security"], details["band"], signal_display

def format_network_name(name):
    if not name:
        return "No connection"
        
    if "ethernet" in name.lower() or name == "Using Ethernet":
        return "[bold green]Wired Connection[/bold green]"
        
    if name == "Connected Network":
        return "[italic]Connected (name unknown)[/italic]"
    
    if len(name) > 30:
        return name[:14] + "..." + name[-13:]
        
    return f"[bold]{name}[/bold]"

def measure_ping():
    def ping_measurement():
        system = platform.system()
        
        for host in ["8.8.8.8", "1.1.1.1"]:
            try:
                cmd = ["ping", "-n" if system == "Windows" else "-c", "4", host]
                result = run_cmd(cmd, split_lines=True, timeout=10)
                if not result:
                    continue
                
                for line in result:
                    if system == "Windows" and "Average" in line:
                        try:
                            avg_ping = float(line.split("=")[-1].strip().replace("ms", ""))
                            return f"{avg_ping:.1f} ms"
                        except:
                            pass
                    elif (system != "Windows") and "avg" in line:
                        try:
                            avg_ping = float(line.split("/")[4])
                            return f"{avg_ping:.1f} ms"
                        except:
                            pass
            except:
                continue
        return "Measurement failed"
    
    cache = _cache['network']
    
    if cache['ping'] != "Not measured yet" and time.time() - cache['timestamp'] < 60:
        return cache['ping']
    
    if cache.get('ping_in_progress', False):
        return "Measuring..."
    
    if not internet_connected():
        return "No connection"
    
    cache['ping'] = "Measuring..."
    cache['ping_in_progress'] = True
    
    def run_measurement():
        try:
            result = ping_measurement()
            cache['ping'] = result
        except:
            cache['ping'] = "Measurement failed"
        finally:
            cache['ping_in_progress'] = False
    
    thread = threading.Thread(target=run_measurement, daemon=True)
    thread.start()
    
    return cache['ping']

def measure_jitter_packet_loss():
    cache = _cache['network']
    
    if (cache['jitter'] != "Not measured yet" and 
        cache['packet_loss'] != "Not measured yet" and 
        time.time() - cache['timestamp'] < 120):
        return cache['jitter'], cache['packet_loss']
    
    if cache.get('jitter_in_progress', False):
        return "Measuring...", "Measuring..."
    
    if not internet_connected():
        return "No connection", "No connection"
    
    cache['jitter'] = cache['packet_loss'] = "Measuring..."
    cache['jitter_in_progress'] = True
    
    def run_measurement():
        try:
            system = platform.system()
            cmd = ["ping", "-n" if system == "Windows" else "-c", "10", "8.8.8.8"]
            result = run_cmd(cmd, split_lines=True, timeout=15)
            
            if not result:
                cache['jitter'] = cache['packet_loss'] = "Measurement failed"
                return
            
            times = []
            received = 0
            sent = 10
            
            for line in result:
                if "bytes from" in line or "Reply from" in line:
                    received += 1
                    if "time=" in line or "time<" in line:
                        try:
                            time_str = line.split("time=")[1].split()[0] if "time=" in line else "0.5"
                            time_str = time_str.replace("ms", "")
                            times.append(float(time_str))
                        except:
                            pass
            
            if sent > 0:
                loss_pct = ((sent - received) / sent) * 100
                cache['packet_loss'] = f"{loss_pct:.1f}%"
            else:
                cache['packet_loss'] = "Unknown"
                
            if len(times) >= 2:
                jitter_value = statistics.stdev(times)
                cache['jitter'] = f"{jitter_value:.1f} ms"
            else:
                cache['jitter'] = "Insufficient data"
        except:
            cache['jitter'] = cache['packet_loss'] = "Measurement failed"
        finally:
            cache['jitter_in_progress'] = False
    
    thread = threading.Thread(target=run_measurement, daemon=True)
    thread.start()
    
    return cache['jitter'], cache['packet_loss']

def measure_internet_speed():
    cache = _cache['network']
    
    if cache['timestamp'] > 0 and time.time() - cache['timestamp'] < 180:
        return cache['download'], cache['upload']
    
    if cache['in_progress']:
        return cache['download'], cache['upload']
    
    if not SPEEDTEST_AVAILABLE:
        cache['download'] = cache['upload'] = "No connection"
        return cache['download'], cache['upload']
    
    if cache['timestamp'] == 0:
        cache['download'] = cache['upload'] = "Measuring..."
    
    cache['in_progress'] = True
    
    def run_measurement():
        try:
            st = speedtest.Speedtest(secure=True)
            st.get_best_server()
            
            try:
                download_speed = st.download() / 1_000_000 
                cache['download'] = f"{download_speed:.2f} Mbps"
            except:
                cache['download'] = "Measurement failed"
            
            try:
                upload_speed = st.upload() / 1_000_000
                cache['upload'] = f"{upload_speed:.2f} Mbps"
            except:
                cache['upload'] = "Measurement failed"
                
            cache['timestamp'] = time.time()
        except:
            cache['download'] = cache['upload'] = "Test failed"
        finally:
            cache['in_progress'] = False
    
    thread = threading.Thread(target=run_measurement, daemon=True)
    thread.start()
    
    return cache['download'], cache['upload']

def track_data_usage():
    cache = _cache['data_usage']
    
    try:
        if cache['download_start'] == 0:
            counters = psutil.net_io_counters()
            cache['download_start'] = counters.bytes_recv
            cache['upload_start'] = counters.bytes_sent
            return "0 MB", "0 MB"
        
        counters = psutil.net_io_counters()
        download_total = (counters.bytes_recv - cache['download_start']) / (1024 * 1024)
        upload_total = (counters.bytes_sent - cache['upload_start']) / (1024 * 1024)
        
        cache['download_current'] = download_total
        cache['upload_current'] = upload_total
        cache['last_check'] = time.time()
        
        download_str = f"{download_total/1024:.2f} GB" if download_total >= 1024 else f"{download_total:.2f} MB"
        upload_str = f"{upload_total/1024:.2f} GB" if upload_total >= 1024 else f"{upload_total:.2f} MB"
            
        return download_str, upload_str
    except:
        return "No connection", "No connection"

def get_system_info():
    info = {}
    
    try:
        if hasattr(psutil, "boot_time"):
            uptime_seconds = int(time.time() - psutil.boot_time())
            hours, remainder = divmod(uptime_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            info["uptime"] = f"{hours} hours, {minutes} minutes and {seconds} seconds"
        else:
            info["uptime"] = "Not available"
    except:
        info["uptime"] = "Not available"
    
    info["cpu"] = f"{psutil.cpu_percent()}%" if hasattr(psutil, "cpu_percent") else "Not available"
    info["ram"] = f"{psutil.virtual_memory().percent}%" if hasattr(psutil, "virtual_memory") else "Not available"
    info["hostname"] = socket.gethostname() if hasattr(socket, "gethostname") else "Unknown"
    
    try:
        if hasattr(psutil, "net_connections"):
            connections = psutil.net_connections(kind='inet')
            info["connections"] = str(len([c for c in connections if c.status == psutil.CONN_ESTABLISHED]))
        else:
            netstat = run_cmd(["netstat", "-an"], split_lines=True)
            info["connections"] = str(len([l for l in netstat if "ESTABLISHED" in l])) if netstat else "Not available"
    except:
        info["connections"] = "Not available"
    
    return info

def get_connection_count():
    try:
        if platform.system() == "Windows":
            result = run_cmd("netstat -an | findstr ESTABLISHED", shell=True, timeout=3)
            if result:
                return str(result.count('\n') + 1)
            else:
                return "0"
        elif platform.system() == "Darwin":
            result = run_cmd("netstat -an | grep ESTABLISHED | wc -l", shell=True, timeout=3)
            if result:
                return result.strip()
            else:
                return "0"
        elif platform.system() == "Linux":
            result = run_cmd("netstat -an | grep ESTABLISHED | wc -l", shell=True, timeout=3)
            if result:
                return result.strip()
            else:
                return "0"
        else:
            return "0"
    except:
        return "0"

def create_dashboard():
    internet_status, internet_color = test_internet_connection()
    connected = internet_status == "✅ Connected"
    
    ssid = get_wifi_name()
    formatted_ssid = format_network_name(ssid)
    security_type, band, signal_strength = get_wifi_details()
    
    local_ip = get_local_ip()
    public_ip = get_public_ip() if connected else "Not available"
    
    ping = measure_ping() if connected else "No connection"
    jitter, packet_loss = measure_jitter_packet_loss() if connected else ("No connection", "No connection")
    
    download_speed, upload_speed = measure_internet_speed() if connected else ("No connection", "No connection")
    download_usage, upload_usage = track_data_usage()
    
    sys_info = get_system_info()
    connection_count = get_connection_count()
    
    colored_ping = colorize_value(ping, "ping")
    colored_jitter = colorize_value(jitter, "jitter")
    colored_packet_loss = colorize_value(packet_loss, "packet_loss")
    colored_download_speed = colorize_value(download_speed, "speed")
    colored_upload_speed = colorize_value(upload_speed, "speed")
    colored_cpu = colorize_value(sys_info["cpu"], "percent")
    colored_ram = colorize_value(sys_info["ram"], "percent")
    
    dashboard = Table.grid(padding=(0, 2))
    dashboard.add_column(justify="left", style="blue", width=2)
    dashboard.add_column(justify="left", style="cyan", width=20)
    dashboard.add_column(width=5)
    dashboard.add_column(justify="left", style="white", width=110, no_wrap=True)
    
    def add_section(title, items, style="green"):
        dashboard.add_row("", f"[bold {style}]{title}[/bold {style}]", "", "")
        for icon, label, value in items:
            dashboard.add_row(icon, f" - {label}:", "", value)
        dashboard.add_row("", "", "", "")
    
    add_section("CONNECTION STATUS", [
        ("🌐", "Internet", f"[{internet_color}]{internet_status}[/{internet_color}]"),
        ("📶", "Network", formatted_ssid),
        ("🔒", "Security", security_type),
        ("📡", "Band", band),
        ("📶", "Signal", signal_strength)
    ])
    
    add_section("CONNECTION QUALITY", [
        ("⏱️", "Ping", colored_ping),
        ("📊", "Jitter", colored_jitter),
        ("📉", "Packet loss", colored_packet_loss)
    ])
    
    add_section("SPEED & DATA USAGE", [
        ("⬇️", "Download speed", colored_download_speed),
        ("⬆️", "Upload speed", colored_upload_speed),
        ("💾", "Downloaded", download_usage),
        ("📤", "Uploaded", upload_usage)
    ])
    
    add_section("NETWORK ADDRESSES", [
        ("🏠", "Local IP", local_ip),
        ("🌍", "Public IP", public_ip)
    ])
    
    add_section("SYSTEM INFO", [
        ("🖥️", "Host name", sys_info["hostname"]),
        ("⏱️", "System uptime", sys_info["uptime"]),
        ("💻", "CPU usage", colored_cpu),
        ("🧠", "RAM usage", colored_ram),
        ("🔗", "Connections", connection_count)
    ])
    
    console_width = console.width
    panel_width = min(150, console_width - 4)
    
    return Panel(
        dashboard, 
        title="📊 [bold green]Netminal Dashboard[/bold green] 📊",
        title_align="center",
        border_style="magenta",
        box=box.ROUNDED,
        padding=(0, 1),
        width=panel_width
    )

def main():
    console_width = console.width
    welcome_width = min(69, console_width - 4)
    
    os.system('cls' if platform.system() == "Windows" else 'clear')
    
    welcome_panel = Panel(
        "🚀 [bold green]Netminal - Network monitoring app in your terminal? Cool...[/bold green] 🛜",
        title_align="center",
        subtitle="https://github.com/asmagaa", 
        border_style="magenta",
        box=box.ROUNDED,
        width=welcome_width
    )
    
    padding = (console_width - welcome_width) // 2 if console_width > welcome_width else 0
    console.print("\n")
    if padding > 0:
        console.print(" " * padding, welcome_panel, sep="")
    else:
        console.print(welcome_panel)
    console.print("\n")
    
    try:
        with Live(console=console, refresh_per_second=1/5) as live:
            while True:
                live.update(create_dashboard())
                time.sleep(2)
    except KeyboardInterrupt:
        console.print("\n[green]Hope everything works, thanks for testing![/green]")

if __name__ == "__main__":
    main()