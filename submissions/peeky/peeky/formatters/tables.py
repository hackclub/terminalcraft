"""
Table formatting for Peeky.

This module provides functions for formatting data into tables for display.
"""

import socket
from typing import Dict, List, Any, Union
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

COLORS = {
    "port": "cyan",
    "pid": "magenta",
    "process": "bright_blue",
    "status": "green",
    "address": "yellow",
    "protocol": "blue",
    "command": "dim",
    "header": "bold bright_white on blue",
    "success": "green",
    "error": "red",
    "warning": "yellow",
    "info": "blue",
    "high_risk": "red",
    "medium_risk": "yellow",
    "low_risk": "green",
    "section_title": "bold cyan",
}

console = Console()


def format_connections_table(connections: List[Dict[str, Any]], show_command: bool = False) -> Table:
    """
    Format connections data into a table.
    
    Args:
        connections: List of connection dictionaries
        show_command: Whether to show the command that started the process
        
    Returns:
        Rich Table object
    """
    table = Table(title="Open Ports and Processes", show_header=True, header_style=COLORS["header"])
    
    table.add_column("Protocol", style=COLORS["protocol"])
    table.add_column("Local Address", style=COLORS["address"])
    table.add_column("Port", style=COLORS["port"])
    table.add_column("Status", style=COLORS["status"])
    table.add_column("PID", style=COLORS["pid"])
    table.add_column("Process", style=COLORS["process"])
    
    if show_command:
        table.add_column("Command", style=COLORS["command"])
    
    protocol_map = {
        socket.SOCK_STREAM: "TCP",
        socket.SOCK_DGRAM: "UDP"
    }
    
    for conn in connections:
        protocol = protocol_map.get(conn["protocol"], str(conn["protocol"]))
        local_addr = conn["local_address"] or "*"
        local_port = str(conn["local_port"]) if conn["local_port"] else "*"
        status = conn["status"] or "-"
        pid = str(conn["pid"]) if conn["pid"] else "-"
        process = conn.get("name", "-")
        
        if show_command:
            command = " ".join(conn.get("cmdline", [])) if conn.get("cmdline") else "-"
            if len(command) > 60:
                command = command[:57] + "..."
            table.add_row(protocol, local_addr, local_port, status, pid, process, command)
        else:
            table.add_row(protocol, local_addr, local_port, status, pid, process)
    
    return table


def format_conflicts_table(conflicts: Dict[int, List[Dict[str, Any]]]) -> Table:
    """
    Format port conflicts data into a table.
    
    Args:
        conflicts: Dictionary mapping ports to lists of conflicting processes
        
    Returns:
        Rich Table object
    """
    table = Table(title="Port Conflicts", show_header=True, header_style=COLORS["header"])
    
    table.add_column("Port", style=COLORS["port"])
    table.add_column("Protocol", style=COLORS["protocol"])
    table.add_column("PIDs", style=COLORS["pid"])
    table.add_column("Processes", style=COLORS["process"])
    
    protocol_map = {
        socket.SOCK_STREAM: "TCP",
        socket.SOCK_DGRAM: "UDP"
    }
    
    for port, processes in conflicts.items():
        by_protocol = {}
        for proc in processes:
            protocol = proc["protocol"]
            if protocol not in by_protocol:
                by_protocol[protocol] = []
            by_protocol[protocol].append(proc)
        
        for protocol, procs in by_protocol.items():
            protocol_name = protocol_map.get(protocol, str(protocol))
            pids = ", ".join(str(p["pid"]) for p in procs)
            proc_names = ", ".join(p["name"] for p in procs)
            
            table.add_row(str(port), protocol_name, pids, proc_names)
    
    return table


def format_stats_table(stats: Dict[str, Any]) -> List[Table]:
    """
    Format network statistics into tables.
    
    Args:
        stats: Dictionary with network statistics
        
    Returns:
        List of Rich Table objects
    """
    tables = []
    
    summary_table = Table(title="Network Summary", show_header=True, header_style=COLORS["header"])
    summary_table.add_column("Metric", style=COLORS["info"])
    summary_table.add_column("Value", style=COLORS["process"])
    
    summary_table.add_row("Total Open Ports", str(stats["total_ports"]))
    summary_table.add_row("Listening Ports", str(stats["listening_ports"]))
    summary_table.add_row("Total Connections", str(stats["total_connections"]))
    summary_table.add_row("TCP Connections", str(stats["tcp_connections"]))
    summary_table.add_row("UDP Connections", str(stats["udp_connections"]))
    summary_table.add_row("Unique Processes", str(stats["unique_processes"]))
    
    tables.append(summary_table)
    
    if stats["status_counts"]:
        status_table = Table(title="Connection Status", show_header=True, header_style=COLORS["header"])
        status_table.add_column("Status", style=COLORS["status"])
        status_table.add_column("Count", style=COLORS["process"])
        
        for status, count in stats["status_counts"].items():
            status_table.add_row(status, str(count))
        
        tables.append(status_table)
    
    throughput_table = Table(title="Network Throughput", show_header=True, header_style=COLORS["header"])
    throughput_table.add_column("Metric", style=COLORS["info"])
    throughput_table.add_column("Value", style=COLORS["process"])
    
    def format_bytes(bytes_value: int) -> str:
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if bytes_value < 1024.0 or unit == "TB":
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
    
    throughput_table.add_row("Bytes Sent", format_bytes(stats["bytes_sent"]))
    throughput_table.add_row("Bytes Received", format_bytes(stats["bytes_received"]))
    throughput_table.add_row("Packets Sent", str(stats["packets_sent"]))
    throughput_table.add_row("Packets Received", str(stats["packets_received"]))
    
    tables.append(throughput_table)
    
    return tables


def format_idle_processes_table(idle_processes: List[Dict[str, Any]]) -> List[Union[Table, Panel]]:
    """
    Format idle processes data into tables.
    
    Args:
        idle_processes: List of idle process dictionaries
        
    Returns:
        List of Rich Table or Panel objects
    """
    result = []
    
    summary_table = Table(title="Idle Processes", show_header=True, header_style=COLORS["header"])
    summary_table.add_column("PID", style=COLORS["pid"])
    summary_table.add_column("Process", style=COLORS["process"])
    summary_table.add_column("CPU %", style=COLORS["info"])
    summary_table.add_column("Ports", style=COLORS["port"])
    summary_table.add_column("Protocols", style=COLORS["protocol"])
    
    for proc in idle_processes:
        pid = str(proc["pid"])
        name = proc["name"]
        cpu = f"{proc['cpu_percent']:.1f}%"
        ports = ", ".join(str(port) for port in proc["ports"])
        protocols = ", ".join(proc["protocols"])
        
        summary_table.add_row(pid, name, cpu, ports, protocols)
    
    result.append(summary_table)
    
    for proc in idle_processes:
        pid = str(proc["pid"])
        name = proc["name"]
        
        cmdline = " ".join(proc["cmdline"]) if proc["cmdline"] else "Unknown"
        if len(cmdline) > 80:
            cmdline = cmdline[:77] + "..."
        
        panel = Panel(
            f"[{COLORS['process']}]Process:[/{COLORS['process']}] {name}\n"
            f"[{COLORS['pid']}]PID:[/{COLORS['pid']}] {pid}\n"
            f"[{COLORS['info']}]CPU Usage:[/{COLORS['info']}] {proc['cpu_percent']:.1f}%\n"
            f"[{COLORS['port']}]Ports:[/{COLORS['port']}] {', '.join(str(port) for port in proc['ports'])}\n"
            f"[{COLORS['protocol']}]Protocols:[/{COLORS['protocol']}] {', '.join(proc['protocols'])}\n"
            f"[{COLORS['command']}]Command:[/{COLORS['command']}] {cmdline}",
            title=f"Process Detail: {name} (PID: {pid})",
            border_style="yellow"
        )
        
        result.append(panel)
    
    return result


def print_table(table: Union[Table, List[Union[Table, Panel]]]) -> None:
    """
    Print a table or list of tables to the console.
    
    Args:
        table: Rich Table object or list of tables/panels
    """
    if isinstance(table, list):
        for t in table:
            console.print(t)
            console.print()
    else:
        console.print(table) 