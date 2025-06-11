"""
Network operations for Peeky.

This module provides functions for network operations and port scanning.
"""

import socket
import psutil
from typing import Dict, List, Optional, Union, Any

def get_connections(port: Optional[int] = None, tcp_only: bool = False, udp_only: bool = False) -> List[Dict[str, Any]]:
    """
    Get all network connections.
    
    Args:
        port: Optional port filter
        tcp_only: Whether to show only TCP connections
        udp_only: Whether to show only UDP connections
        
    Returns:
        List of connection dictionaries
    """
    connections = []
    
    network_connections = psutil.net_connections()
    
    for conn in network_connections:
        connection_info = {
            "protocol": conn.type,
            "local_address": conn.laddr.ip if conn.laddr else None,
            "local_port": conn.laddr.port if conn.laddr else None,
            "remote_address": conn.raddr.ip if conn.raddr else None,
            "remote_port": conn.raddr.port if conn.raddr else None,
            "status": conn.status,
            "pid": conn.pid
        }
        
        if tcp_only and connection_info["protocol"] != socket.SOCK_STREAM:
            continue
        if udp_only and connection_info["protocol"] != socket.SOCK_DGRAM:
            continue
        
        if port is not None and connection_info["local_port"] != port:
            continue
        
        connections.append(connection_info)
    
    return connections


def get_connection_with_process_info(
    port: Optional[int] = None,
    tcp_only: bool = False,
    udp_only: bool = False,
    process_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get connections with detailed process information.
    
    Args:
        port: Optional port filter
        tcp_only: Whether to show only TCP connections
        udp_only: Whether to show only UDP connections
        process_filter: Optional process name filter
        
    Returns:
        List of connection dictionaries with process info
    """
    connections = get_connections(port, tcp_only, udp_only)
    enhanced_connections = []
    
    for conn in connections:
        if conn["pid"] is None:
            continue
        
        try:
            process = psutil.Process(conn["pid"])
            process_info = {
                "name": process.name(),
                "create_time": process.create_time(),
                "cpu_percent": process.cpu_percent(),
                "memory_percent": process.memory_percent(),
                "cmdline": process.cmdline()
            }
            
            if process_filter and process_filter.lower() not in process_info["name"].lower():
                continue
                
            enhanced_conn = {**conn, **process_info}
            enhanced_connections.append(enhanced_conn)
            
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    
    return enhanced_connections


def detect_port_conflicts() -> Dict[int, List[Dict[str, Any]]]:
    """
    Detect port conflicts (multiple processes using the same port).
    
    Returns:
        Dictionary mapping ports to lists of conflicting processes
    """
    connections = get_connections()
    port_processes = {}
    
    for conn in connections:
        port = conn["local_port"]
        if port is None:
            continue
        
        if port not in port_processes:
            port_processes[port] = []
            
        if conn["pid"] is not None:
            try:
                process = psutil.Process(conn["pid"])
                process_info = {
                    "pid": conn["pid"],
                    "name": process.name(),
                    "protocol": conn["protocol"],
                    "status": conn["status"]
                }
                port_processes[port].append(process_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    
    conflicts = {port: procs for port, procs in port_processes.items() if len(procs) > 1}
    return conflicts


def calculate_network_stats() -> Dict[str, Any]:
    """
    Calculate network statistics.
    
    Returns:
        Dictionary with network statistics
    """
    connections = get_connections()
    tcp_connections = [conn for conn in connections if conn["protocol"] == socket.SOCK_STREAM]
    udp_connections = [conn for conn in connections if conn["protocol"] == socket.SOCK_DGRAM]
    
    ports = set()
    listening_ports = set()
    for conn in connections:
        if conn["local_port"] is not None:
            ports.add(conn["local_port"])
            if conn["protocol"] == socket.SOCK_STREAM and conn["status"] == "LISTEN":
                listening_ports.add(conn["local_port"])
    
    processes = set()
    for conn in connections:
        if conn["pid"] is not None:
            processes.add(conn["pid"])
    
    status_counts = {}
    for conn in tcp_connections:
        status = conn["status"]
        if status not in status_counts:
            status_counts[status] = 0
        status_counts[status] += 1
    
    network_io = psutil.net_io_counters()
    
    return {
        "total_ports": len(ports),
        "listening_ports": len(listening_ports),
        "total_connections": len(connections),
        "tcp_connections": len(tcp_connections),
        "udp_connections": len(udp_connections),
        "unique_processes": len(processes),
        "status_counts": status_counts,
        "bytes_sent": network_io.bytes_sent,
        "bytes_received": network_io.bytes_recv,
        "packets_sent": network_io.packets_sent,
        "packets_received": network_io.packets_recv
    } 