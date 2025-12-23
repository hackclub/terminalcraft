import psutil
from collections import defaultdict

def get_ports():
    ports = defaultdict(list)
    for conn in psutil.net_connections(kind='inet'):
        laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else ""
        raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else ""
        ports[conn.status].append({
            "pid": conn.pid,
            "laddr": laddr,
            "raddr": raddr,
            "status": conn.status
        })
    return ports

def get_process_info(pid: int) -> str:
    try:
        p = psutil.Process(pid)
        name = p.name()
        cpu = p.cpu_percent(interval=0.1)
        mem = p.memory_info().rss // (1024 * 1024)  # in MB
        return f"{name} | CPU: {cpu:.1f}% | MEM: {mem}MB"
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return "Process info not available"

def kill_process_by_pid(pid: int) -> bool:
    try:
        p = psutil.Process(pid)
        p.terminate()
        p.wait(timeout=3)
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
        return False
