#!/usr/bin/env python3

import argparse
import sys
from colorama import init, Fore, Style
from .utils import check_port, validate_port, traceroute, whois

init()

def main():
    if len(sys.argv) == 1:
        from .tui import main as tui_main
        tui_main()
        return

    parser = argparse.ArgumentParser(description='Network utility tools for checking ports, traceroute and WHOIS lookups.')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    port_parser = subparsers.add_parser('port', help='Check if a port is open')
    port_parser.add_argument('host', help='Host address (IP or domain name)')
    port_parser.add_argument('port', help='Port number (1-65535)')
    port_parser.add_argument('-t', '--timeout', type=float, default=3.0, 
                        help='Connection timeout in seconds (default: 3.0)')

    trace_parser = subparsers.add_parser('trace', help='Run a traceroute to a host')
    trace_parser.add_argument('host', help='Host address (IP or domain name)')
    trace_parser.add_argument('-m', '--max-hops', type=int, default=30,
                          help='Maximum number of hops (default: 30)')
    trace_parser.add_argument('-t', '--timeout', type=float, default=1.0,
                          help='Timeout for each hop in seconds (default: 1.0)')
    
    whois_parser = subparsers.add_parser('whois', help='Perform WHOIS lookup')
    whois_parser.add_argument('domain', help='Domain name or IP address')

    args = parser.parse_args()
    
    if not hasattr(args, 'command') or args.command is None:
        if len(sys.argv) >= 3:
            args.command = 'port'
            args.host = sys.argv[1]
            args.port = sys.argv[2]
            args.timeout = 3.0
            if len(sys.argv) > 3 and sys.argv[3] == '--timeout' and len(sys.argv) > 4:
                try:
                    args.timeout = float(sys.argv[4])
                except ValueError:
                    pass
    
    if args.command == 'port' or args.command is None:
        run_port_check(args)
    elif args.command == 'trace':
        run_traceroute(args)
    elif args.command == 'whois':
        run_whois(args)
    else:
        parser.print_help()
        sys.exit(1)

def run_port_check(args):
    try:
        port = validate_port(args.port)
    except ValueError as e:
        print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        sys.exit(1)
    
    result = check_port(args.host, port, args.timeout)
    
    if isinstance(result, tuple):
        is_open, error_msg = False, result[1]
        print(f"{Fore.RED}Port {port} on {args.host} is CLOSED: {error_msg}.{Style.RESET_ALL}")
    elif result:
        print(f"{Fore.GREEN}Port {port} on {args.host} is OPEN.{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Port {port} on {args.host} is CLOSED.{Style.RESET_ALL}")

def run_traceroute(args):
    print(f"Running traceroute to {args.host} (max hops: {args.max_hops}, timeout: {args.timeout}s)...")
    
    results = traceroute(args.host, args.max_hops, args.timeout)
    
    if results and "error" in results[0] and results[0]["error"] and results[0]["hop"] == 0:
        print(f"{Fore.RED}Error: {results[0]['error']}{Style.RESET_ALL}")
        sys.exit(1)
    
    print(f"\nTraceroute to {args.host}:\n")
    
    for hop in results:
        hop_num = hop["hop"]
        ip = hop["ip"] or "*"
        hostname = hop["hostname"] or ip
        time_ms = f"{hop['time']:.2f} ms" if hop["time"] is not None else "*"
        
        if hop["error"]:
            status_color = Fore.RED
            status_text = f" ({hop['error']})"
        else:
            status_color = Fore.GREEN
            status_text = ""
        
        if ip == hostname:
            print(f"{hop_num}. {status_color}{ip} - {time_ms}{status_text}{Style.RESET_ALL}")
        else:
            print(f"{hop_num}. {status_color}{ip} ({hostname}) - {time_ms}{status_text}{Style.RESET_ALL}")

def run_whois(args):
    print(f"Looking up WHOIS information for {args.domain}...")
    
    result = whois(args.domain)
    
    if "Error" in result:
        print(f"{Fore.RED}{result}{Style.RESET_ALL}")
        sys.exit(1)
    
    print(f"\nWHOIS information for {args.domain}:\n")
    print(result)

if __name__ == "__main__":
    main()