"""
Process operations for Peeky.

This module provides functions for process management and inspection.
"""

import os
import sys
import time
import socket
import psutil
from typing import Dict, List, Optional, Union, Any, Tuple

def kill_process(pid: int, force: bool = False) -> bool:
    """
    Kill a process by PID.
    
    Args:
        pid: Process ID to kill
        force: Whether to force kill the process (SIGKILL instead of SIGTERM)
        
    Returns:
        True if the process was killed, False otherwise
    """
    try:
        process = psutil.Process(pid)
        if force:
            process.kill() 
        else:
            process.terminate() 
            
        gone, still_alive = psutil.wait_procs([process], timeout=3)
        if still_alive:
            if not force:
                process.kill()
                psutil.wait_procs([process], timeout=3)
        
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        return False


def kill_process_by_port(port: int, force: bool = False) -> bool:
    """
    Kill all processes using a specific port.
    
    Args:
        port: Port number
        force: Whether to force kill the process (SIGKILL instead of SIGTERM)
        
    Returns:
        True if any process was killed, False otherwise
    """
    from peeky.core.network import get_connections
    connections = get_connections(port=port)
    
    pids = set(conn["pid"] for conn in connections if conn["pid"] is not None)
    
    success = False
    for pid in pids:
        if kill_process(pid, force):
            success = True
    
    return success


def is_risky_process(pid: int) -> Tuple[bool, str]:
    """
    Check if killing a process might be risky (system process, etc.).
    
    Args:
        pid: Process ID to check
        
    Returns:
        Tuple of (is_risky, reason)
    """
    try:
        process = psutil.Process(pid)
        
        name = process.name().lower()
        try:
            username = process.username()
        except:
            username = "unknown"
        
        system_processes = [
            "system", "systemd", "explorer.exe", "svchost.exe", "csrss.exe",
            "winlogon.exe", "services.exe", "lsass.exe", "wininit.exe"
        ]
        
        for sys_proc in system_processes:
            if sys_proc in name:
                return True, f"'{name}' appears to be a system process"
        
        system_users = ["root", "system", "local service", "network service"]
        if any(u.lower() in username.lower() for u in system_users):
            return True, f"'{name}' is running as a system user ({username})"
        
        children = process.children(recursive=True)
        if len(children) > 5:
            return True, f"'{name}' has {len(children)} child processes, it might be important"
        
        return False, ""
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False, ""


def find_idle_processes(min_idle_time: int = 3600, cpu_threshold: float = 0.5) -> List[Dict[str, Any]]:
    """
    Find idle processes that are using ports but appear inactive.
    
    Args:
        min_idle_time: Minimum idle time in seconds (default: 1 hour)
        cpu_threshold: Maximum CPU usage threshold to consider idle
        
    Returns:
        List of idle process dictionaries
    """
    from peeky.core.network import get_connection_with_process_info
    connections = get_connection_with_process_info()
    
    processes = {}
    for conn in connections:
        pid = conn["pid"]
        if pid is None:
            continue
            
        if pid not in processes:
            processes[pid] = {
                "pid": pid,
                "name": conn.get("name", "Unknown"),
                "cpu_percent": conn.get("cpu_percent", 0),
                "create_time": conn.get("create_time", 0),
                "ports": set(),
                "protocols": set(),
                "cmdline": conn.get("cmdline", [])
            }
        
        if conn["local_port"] is not None:
            processes[pid]["ports"].add(conn["local_port"])
            
        if conn["protocol"] is not None:
            protocols = {socket.SOCK_STREAM: "TCP", socket.SOCK_DGRAM: "UDP"}
            protocol_name = protocols.get(conn["protocol"], str(conn["protocol"]))
            processes[pid]["protocols"].add(protocol_name)
    
    current_time = time.time()
    idle_processes = []
    
    for pid, proc_info in processes.items():
        if not proc_info["ports"]:
            continue
            
        process_age = current_time - proc_info["create_time"]
        
        is_low_cpu = proc_info["cpu_percent"] < cpu_threshold
        
        is_old = process_age > min_idle_time
        
        if is_low_cpu and is_old:
            proc_info["ports"] = list(proc_info["ports"])
            proc_info["protocols"] = list(proc_info["protocols"])
            idle_processes.append(proc_info)
    
    return idle_processes


def clean_idle_processes(force: bool = False) -> List[Dict[str, Any]]:
    """
    Clean up idle processes.
    
    Args:
        force: Whether to force kill processes
        
    Returns:
        List of killed process dictionaries
    """
    idle_processes = find_idle_processes()
    killed_processes = []
    
    for proc in idle_processes:
        pid = proc["pid"]
        if kill_process(pid, force):
            killed_processes.append(proc)
    
    return killed_processes 