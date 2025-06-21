"""
CLI commands implementation for Peeky.

This module defines the Typer commands for the Peeky CLI.
"""

import sys
from typing import Optional, List, Literal

import typer
from rich.console import Console
from rich.style import Style

from peeky.core.network import get_connection_with_process_info, detect_port_conflicts, calculate_network_stats
from peeky.core.process import kill_process, kill_process_by_port, is_risky_process, find_idle_processes, clean_idle_processes
from peeky.core.secure import identify_exposed_ports, get_security_recommendations
from peeky.core.whois import perform_lookup, is_valid_ipv4, is_valid_domain
from peeky.core.config import set_api_key, get_api_key
from peeky.formatters.tables import (
    format_connections_table, 
    format_conflicts_table, 
    format_stats_table, 
    format_idle_processes_table,
    print_table,
    COLORS
)
from peeky.formatters.export import write_export
from peeky.formatters.security import print_security_results
from peeky.formatters.whois import print_whois_result


app = typer.Typer(
    help="Peeky - A Minimal Port & Process Inspector",
    add_completion=False,
)

console = Console()


def print_message(
    message: str, 
    message_type: Literal["success", "error", "warning", "info"] = "info",
    bold: bool = False
):
    """
    Print a styled message to the console.
    
    Args:
        message: The message to print
        message_type: The type of message (success, error, warning, info)
        bold: Whether to make the text bold
    """
    style = COLORS[message_type]
    if bold:
        style = f"{style} bold"
    
    console.print(f"[{style}]{message}[/{style}]")


@app.command()
def config(
    api_key: Optional[str] = typer.Argument(None, help="API key to set (if provided, will be used for WHOIS)"),
    set_whois_key: bool = typer.Option(False, "--set-whois-key", help="Set the WHOIS API key (will prompt for input)"),
    whois_key_value: Optional[str] = typer.Option(None, "--key", "-k", help="The WHOIS API key value (alternative to being prompted)"),
    show_keys: bool = typer.Option(False, "--show-keys", help="Show available API keys (masked)"),
):
    """
    Configure Peeky settings and API keys.
    """
    if api_key is not None:
        set_api_key("whois", api_key)
        print_message("WHOIS API key stored successfully.", message_type="success", bold=True)
        print_message("You can now use the 'whois' command with real data.", message_type="info")
        return
        
    if set_whois_key:
        api_key = whois_key_value
        
        if api_key is None:
            current_key = get_api_key("whois")
            if current_key:
                print_message(f"Current WHOIS API key: {current_key[:4]}...{current_key[-4:]}", message_type="info")
                
                if not typer.confirm("Do you want to update the WHOIS API key?"):
                    print_message("API key update canceled.", message_type="warning")
                    return
            
            api_key = typer.prompt("Enter your APILayer WHOIS API key", hide_input=True)
        
        if not api_key:
            print_message("API key cannot be empty.", message_type="error")
            return
        
        set_api_key("whois", api_key)
        print_message("WHOIS API key stored successfully.", message_type="success", bold=True)
        print_message("You can now use the 'whois' command with real data.", message_type="info")
    
    elif show_keys:
        whois_key = get_api_key("whois")
        
        if whois_key:
            masked_key = f"{whois_key[:4]}...{whois_key[-4:]}"
            print_message(f"WHOIS API key: {masked_key}", message_type="info")
        else:
            print_message("No WHOIS API key set. Use --set-whois-key to set it.", message_type="warning")
    
    else:
        print_message("Use --set-whois-key to set the WHOIS API key", message_type="info")
        print_message("Use --key to provide the API key directly", message_type="info")
        print_message("Use --show-keys to view available API keys", message_type="info")


@app.command()
def scan(
    port: Optional[int] = typer.Option(None, "--port", "-p", help="Filter by port number"),
    tcp: bool = typer.Option(False, "--tcp", help="Show TCP connections only"),
    udp: bool = typer.Option(False, "--udp", help="Show UDP connections only"),
    filter: Optional[str] = typer.Option(None, "--filter", "-f", help="Filter by process name"),
    show_command: bool = typer.Option(False, "--command", "-c", help="Show command that started the process"),
):
    """
    Scan and list all open ports with process information.
    """
    connections = get_connection_with_process_info(
        port=port,
        tcp_only=tcp,
        udp_only=udp,
        process_filter=filter
    )
    
    if not connections:
        print_message("No connections found matching the criteria.", message_type="warning")
        return
    
    table = format_connections_table(connections, show_command)
    print_table(table)


@app.command()
def conflicts():
    """
    Detect and display port conflicts (multiple processes using the same port).
    """
    conflicts_data = detect_port_conflicts()
    
    if not conflicts_data:
        print_message("No port conflicts detected.", message_type="success", bold=True)
        return
    
    table = format_conflicts_table(conflicts_data)
    print_table(table)
    
    console.print()
    print_message("To resolve conflicts, you can kill one of the processes:", message_type="warning")
    print_message("peeky kill <PID> - Kill a specific process by PID", message_type="info")
    print_message("peeky kill <PORT> - Kill all processes using a specific port", message_type="info")
    console.print()


@app.command()
def stats():
    """
    Display network statistics and summary information.
    """
    stats_data = calculate_network_stats()
    
    if stats_data["total_ports"] == 0:
        print_message("No open ports found. Network statistics unavailable.", message_type="warning")
        return
    
    tables = format_stats_table(stats_data)
    print_table(tables)
    
    console.print()
    print_message("Tip: Use peeky scan to see detailed port information", message_type="info")
    print_message("Tip: Use peeky conflicts to check for port conflicts", message_type="info")
    console.print()


@app.command()
def clean(
    force: bool = typer.Option(False, "--force", "-f", help="Force kill (SIGKILL instead of SIGTERM)"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts"),
    list_only: bool = typer.Option(False, "--list", "-l", help="Only list processes, don't clean"),
):
    """
    Clean up idle or zombie port-bound processes like hanging dev servers.
    """
    idle_processes = find_idle_processes()
    
    if not idle_processes:
        print_message("No idle processes found that could be cleaned up.", message_type="success", bold=True)
        return
    
    tables = format_idle_processes_table(idle_processes)
    print_table(tables)
    
    if list_only:
        print_message("List-only mode. No processes were cleaned up.", message_type="warning")
        print_message("To clean these processes, run peeky clean without the --list flag.", message_type="info")
        return
    
    if not yes:
        process_count = len(idle_processes)
        confirm = typer.confirm(
            f"\n[{COLORS['warning']}]Do you want to clean up {process_count} idle process(es)?[/{COLORS['warning']}]",
            default=False
        )
        if not confirm:
            print_message("Clean operation canceled.", message_type="warning")
            return
    
    killed_processes = clean_idle_processes(force)
    
    if killed_processes:
        print_message(f"Successfully cleaned up {len(killed_processes)} process(es).", message_type="success", bold=True)
        
        for process in killed_processes:
            name = process.get("name", "Unknown")
            pid = process.get("pid", "N/A")
            ports = ", ".join(str(port) for port in process.get("ports", []))
            console.print(f"  [{COLORS['process']}]{name}[/{COLORS['process']}] " +
                          f"(PID: [{COLORS['pid']}]{pid}[/{COLORS['pid']}]) " +
                          f"on port(s): [{COLORS['port']}]{ports}[/{COLORS['port']}]")
    else:
        print_message("No processes were cleaned up. They might be protected or require elevated permissions.", message_type="warning")


@app.command()
def kill(
    target: str = typer.Argument(..., help="PID or port number to kill"),
    force: bool = typer.Option(False, "--force", "-f", help="Force kill (SIGKILL instead of SIGTERM)"),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompts"),
):
    """
    Kill a process by PID or port number.
    """
    try:
        target_int = int(target)
    except ValueError:
        print_message(f"Error: '{target}' is not a valid PID or port number", message_type="error")
        sys.exit(1)
    
    success = False
    if target_int < 65536:
        from peeky.core.network import get_connections
        connections = get_connections(port=target_int)
        pids = [conn.get("pid") for conn in connections if conn.get("pid")]
        
        if not yes:
            for pid in pids:
                is_risky, reason = is_risky_process(pid)
                if is_risky:
                    confirm = typer.confirm(
                        f"[{COLORS['warning']}]Warning: {reason}. Continue with kill?[/{COLORS['warning']}]",
                        default=False
                    )
                    if not confirm:
                        print_message("Kill operation canceled.", message_type="warning")
                        sys.exit(0)
        
        success = kill_process_by_port(target_int, force)
        
        if success:
            print_message(f"Successfully killed process using port {target_int}", message_type="success", bold=True)
        else:
            if not yes:
                is_risky, reason = is_risky_process(target_int)
                if is_risky:
                    confirm = typer.confirm(
                        f"[{COLORS['warning']}]Warning: {reason}. Continue with kill?[/{COLORS['warning']}]",
                        default=False
                    )
                    if not confirm:
                        print_message("Kill operation canceled.", message_type="warning")
                        sys.exit(0)
                        
            success = kill_process(target_int, force)
            if success:
                print_message(f"Successfully killed process with PID {target_int}", message_type="success", bold=True)
            else:
                print_message(f"Failed to kill: No process using port {target_int} or with PID {target_int}", message_type="error")
    else:
        if not yes:
            is_risky, reason = is_risky_process(target_int)
            if is_risky:
                confirm = typer.confirm(
                    f"[{COLORS['warning']}]Warning: {reason}. Continue with kill?[/{COLORS['warning']}]",
                    default=False
                )
                if not confirm:
                    print_message("Kill operation canceled.", message_type="warning")
                    sys.exit(0)
                    
        success = kill_process(target_int, force)
        if success:
            print_message(f"Successfully killed process with PID {target_int}", message_type="success", bold=True)
        else:
            print_message(f"Failed to kill process with PID {target_int}", message_type="error")
            print_message("Hint: You might need elevated permissions or the process might be protected", message_type="warning")
    
    sys.exit(0 if success else 1)


@app.command()
def export(
    output: Optional[str] = typer.Option(None, "--out", "-o", help="Output file path (stdout if not specified)"),
    json_format: bool = typer.Option(False, "--json", "-j", help="Export as JSON instead of plain text"),
    port: Optional[int] = typer.Option(None, "--port", "-p", help="Filter by port number"),
    tcp: bool = typer.Option(False, "--tcp", help="Show TCP connections only"),
    udp: bool = typer.Option(False, "--udp", help="Show UDP connections only"),
    filter: Optional[str] = typer.Option(None, "--filter", "-f", help="Filter by process name"),
):
    """
    Export connection data to JSON or plain text format.
    """
    connections = get_connection_with_process_info(
        port=port,
        tcp_only=tcp,
        udp_only=udp,
        process_filter=filter
    )
    
    if not connections:
        print_message("No connections found matching the criteria.", message_type="warning")
        return
    
    format_type = "json" if json_format else "text"
    write_export(connections, output, format_type)


@app.command()
def secure():
    """
    Identify and display potential security risks in network configuration.
    """
    exposed_services = identify_exposed_ports()
    
    recommendations = get_security_recommendations(exposed_services)
    
    print_security_results(exposed_services, recommendations)


@app.command()
def whois(
    target: str = typer.Argument(..., help="IP address or domain name to look up"),
    local: bool = typer.Option(False, "--local", "-l", help="Use local connections only (no external API calls)"),
):
    """
    Look up information about an IP address or domain name.
    
    This command performs a WHOIS-like lookup to provide information about the target.
    """
    if not is_valid_ipv4(target) and not is_valid_domain(target):
        print_message(f"Invalid input: '{target}' is not a valid IP address or domain name", message_type="error")
        sys.exit(1)
    
    is_ip = is_valid_ipv4(target)
    
    if not local and not is_ip:
        has_api_key = get_api_key("whois") is not None
        if has_api_key:
            console.print(
                "[blue]Note:[/blue] Using API to retrieve detailed WHOIS information. "
                "Use [bold]--local[/bold] flag to use only local resolution.\n"
            )
        else:
            console.print(
                "[yellow]Note:[/yellow] Running in demo mode with limited data. "
                "Set an API key with [bold]peeky config --set-whois-key[/bold] for full features.\n"
            )
    
    data, error, lookup_type = perform_lookup(target, use_api=not local)
    
    if error:
        print_message(error, message_type="error")
        sys.exit(1)
    
    print_whois_result(data, error, lookup_type) 