import psutil
import socket
import time
import subprocess
import threading
import platform
import json
import requests
import argparse
import curses
from datetime import datetime

LOG_FILE = "netpeek_log.json"
COMMON_PORTS = [20, 21, 22, 80, 443, 5900, 8000, 8080, 25565]

def get_net_stats():
    old = psutil.net_io_counters(pernic=True)
    time.sleep(1)
    new = psutil.net_io_counters(pernic=True)

    stats = []
    for iface in old:
        down = new[iface].bytes_recv - old[iface].bytes_recv
        up = new[iface].bytes_sent - old[iface].bytes_sent
        stats.append({
            "interface": iface,
            "download_kbps": down / 1024,
            "upload_kbps": up / 1024
        })
    return stats

#might work on linux, ill test later
def get_open_ports():
    if platform.system() == "Windows":
        result = subprocess.check_output("netstat -ano", shell=True).decode()
    else:
        result = subprocess.check_output("netstat -tuln", shell=True).decode()
    return result

def ping_host(ip, results):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    result = subprocess.run(["ping", param, "1", ip],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if result.returncode == 0:
        geo = get_geo_info(ip)
        results.append({"ip": ip, "geo": geo})

def scan_network():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    subnet = ".".join(local_ip.split(".")[:3]) + "."

    threads = []
    results = []
    for i in range(1, 255):
        ip = subnet + str(i)
        t = threading.Thread(target=ping_host, args=(ip, results))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
    return results

def get_geo_info(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=2)
        data = r.json()
        return {
            "country": data.get("country"),
            "city": data.get("city"),
            "org": data.get("org")
        }
    except:
        return {}

def get_about_me():
    try:
        r = requests.get("https://clean.wtfismyip.com/json", timeout=5)
        data = r.json()
        print("Public Network Info")
        print("-----------------------------------------")
        print(f"IP Address  : {data.get('YourIPAddress')}")
        print(f"Hostname    : {data.get('YourHostname')}")
        print(f"Location    : {data.get('YourLocation')}")
        print(f"City        : {data.get('YourCity')}")
        print(f"Country     : {data.get('YourCountry')} ({data.get('YourCountryCode')})")
        print(f"ISP         : {data.get('YourISP')}")
        print(f"Tor Exit    : {'Yes' if data.get('YourTorExit') else 'No'}")
        return data
    except Exception as e:
        print("Error retrieving info from clean.wtfismyip.com:", e)
        return None

def save_to_file(data):
    with open(LOG_FILE, "a") as f:
        json.dump({"timestamp": str(datetime.now()), "data": data}, f, indent=2)
        f.write("\n")

def tui_interface(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "NetPeek TUI - Press Q to exit")
        stats = get_net_stats()
        for i, entry in enumerate(stats):
            line = f"{entry['interface']:<10} ↓ {entry['download_kbps']:.1f} KB/s ↑ {entry['upload_kbps']:.1f} KB/s"
            stdscr.addstr(i + 2, 0, line)
        stdscr.refresh()
        key = stdscr.getch()
        if key in [ord('q'), ord('Q')]:
            break

#include start and end port
def scan_ports_custom(host, start_port, end_port):
    open_ports = []
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            try:
                if s.connect_ex((host, port)) == 0:
                    open_ports.append(port)
            except Exception:
                pass
    return open_ports

def main():
    parser = argparse.ArgumentParser(
        description="netpeek — All in One Terminal Network Toolkit",
        epilog="""
Examples:
  python netpeek.py stats
  python netpeek.py scan --export
  python netpeek.py ports
  python netpeek.py tui
  python netpeek.py aboutme
  python netpeek.py ports_custom --host 192.168.1.10 --start-port 20 --end-port 100
  python netpeek.py ports_common --host 192.168.1.10

Notes:
  - For port scans, specify --host to target a specific IP (default 127.0.0.1)
  - ports_custom scans ports in the specified range
  - ports_common scans a list of common ports
""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "mode",
        choices=["stats", "ports", "scan", "tui", "aboutme", "ports_custom", "ports_common"],
    )

    parser.add_argument("--export", action="store_true", help="Export output to netpeek_log.json")

    parser.add_argument("--host", type=str, default="127.0.0.1", help="Target host IP for port scanning")
    parser.add_argument("--start-port", type=int, default=1, help="Start port (for ports_custom)")
    parser.add_argument("--end-port", type=int, default=1024, help="End port (for ports_custom)")

    args = parser.parse_args()

    if args.mode == "stats":
        data = get_net_stats()
        for entry in data:
            print(f"{entry['interface']:<10} ↓ {entry['download_kbps']:.1f} KB/s ↑ {entry['upload_kbps']:.1f} KB/s")
        if args.export:
            save_to_file(data)

    elif args.mode == "ports":
        result = get_open_ports()
        print(result)
        if args.export:
            save_to_file({"ports": result})

    elif args.mode == "scan":
        results = scan_network()
        for r in results:
            geo = r['geo']
            print(f"[+] {r['ip']} - {geo.get('city', 'Unknown')}, {geo.get('country', '')} ({geo.get('org', '')})")
        if args.export:
            save_to_file({"hosts": results})

    elif args.mode == "tui":
        try:
            curses.wrapper(tui_interface)
        except Exception as e:
            print("Error: TUI mode requires a normal terminal (not the Python terminal).")
            print(e)

    elif args.mode == "aboutme":
        data = get_about_me()
        if args.export and data:
            save_to_file({"aboutme": data})

    elif args.mode == "ports_custom":
        print(f"Scanning ports {args.start_port} to {args.end_port} on {args.host} ...")
        open_ports = scan_ports_custom(args.host, args.start_port, args.end_port)
        if open_ports:
            for port in open_ports:
                print(f"Port {port} is open")
        else:
            print("No open ports found in specified range.")
        if args.export:
            save_to_file({"ports_custom": {"host": args.host, "open_ports": open_ports}})

    elif args.mode == "ports_common":
        print(f"Scanning common ports on {args.host} ...")
        open_ports = scan_ports_custom(args.host, min(COMMON_PORTS), max(COMMON_PORTS))
        open_common = [p for p in COMMON_PORTS if p in open_ports]
        if open_common:
            for port in open_common:
                print(f"Port {port} is open")
        else:
            print("No common ports open.")
        if args.export:
            save_to_file({"ports_common": {"host": args.host, "open_ports": open_common}})

if __name__ == "__main__":
    main()
