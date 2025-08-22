import psutil
import time
import os
import platform
from datetime import datetime
import sys
import shutil

try:
    from colorama import Fore, Back, Style, init
    colorama_available = True
    init(autoreset=True)
except ImportError:
    colorama_available = False

def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def get_cpu_info():
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_count = psutil.cpu_count(logical=True)
        cpu_count_physical = psutil.cpu_count(logical=False)
        
        try:
            cpu_freq = psutil.cpu_freq()
            freq_current = cpu_freq.current if cpu_freq else "N/A"
            freq_max = cpu_freq.max if cpu_freq else "N/A"
        except Exception:
            freq_current = "N/A"
            freq_max = "N/A"
        
        return {
            'percent': cpu_percent,
            'cores': cpu_count,
            'physical_cores': cpu_count_physical if cpu_count_physical else cpu_count,
            'freq_current': freq_current,
            'freq_max': freq_max
        }
    except Exception as e:
        print(f"Error getting CPU info: {e}")
        return {
            'percent': 0,
            'cores': 0,
            'physical_cores': 0,
            'freq_current': "Error",
            'freq_max': "Error"
        }

def get_memory_info():
    try:
        memory = psutil.virtual_memory()
        
        return {
            'total': memory.total / (1024 * 1024 * 1024),
            'available': memory.available / (1024 * 1024 * 1024),
            'used': memory.used / (1024 * 1024 * 1024),
            'percent': memory.percent
        }
    except Exception as e:
        print(f"Error getting memory info: {e}")
        return {
            'total': 0,
            'available': 0,
            'used': 0,
            'percent': 0
        }

def get_network_info():
    try:
        network = psutil.net_io_counters()
        
        return {
            'bytes_sent': network.bytes_sent / (1024 * 1024),
            'bytes_recv': network.bytes_recv / (1024 * 1024),
        }
    except Exception as e:
        print(f"Error getting network info: {e}")
        return {
            'bytes_sent': 0,
            'bytes_recv': 0
        }

def get_processes(limit=5):
    processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_percent': proc.info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return processes[:limit]
    except Exception as e:
        print(f"Error getting process info: {e}")
        return []

def get_terminal_size():
    try:
        columns, rows = shutil.get_terminal_size()
        return columns, rows
    except:
        return 80, 24

def draw_box(title, content, width=None):
    if width is None:
        term_width, _ = get_terminal_size()
        width = min(term_width - 2, 80)
        
    title = f" {title} "
    padding = max(0, width - len(title))
    top_border = "╭" + title + "─" * padding + "╮"
    bottom_border = "╰" + "─" * (width) + "╯"
    
    result = [top_border]
    for line in content:
        line_content = line[:width-2] if len(line) > width-2 else line
        result.append("│" + line_content + " " * (width - len(line_content)) + "│")
    result.append(bottom_border)
    
    return result

def center_text(text, width=None):
    if width is None:
        term_width, _ = get_terminal_size()
        width = term_width
    
    padding = max(0, width - len(text))
    return " " * (padding // 2) + text + " " * (padding - padding // 2)

def progress_bar(percent, width=30, style='modern'):
    try:
        filled = int(width * percent / 100)
        
        if style == 'modern' and not (sys.platform == 'win32' and sys.version_info < (3, 6)):
            bar = '█' * filled + '░' * (width - filled)
        elif style == 'block':
            blocks = ['█', '▓', '▒', '░']
            bar = blocks[0] * filled + blocks[3] * (width - filled)
        else:
            bar = '#' * filled + '-' * (width - filled)
            
        if colorama_available:
            if percent < 60:
                color = Fore.GREEN
            elif percent < 80:
                color = Fore.YELLOW
            else:
                color = Fore.RED
            return f"{color}[{bar}]{Style.RESET_ALL} {percent:.1f}%"
        else:
            return f"[{bar}] {percent:.1f}%"
    except Exception:
        return f"{percent:.1f}%"

def format_size(bytes_value, unit='auto'):
    if unit == 'auto':
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024 or unit == 'TB':
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024
    else:
        conversions = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
        return f"{bytes_value / conversions.get(unit, 1):.2f} {unit}"

def colored_text(text, color_code):
    if colorama_available:
        return f"{color_code}{text}{Style.RESET_ALL}"
    return text

def display_system_info():
    try:
        cpu_info = get_cpu_info()
        memory_info = get_memory_info()
        network_info = get_network_info()
        processes = get_processes(limit=8)
        
        term_width, term_height = get_terminal_size()
        
        clear_screen()
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        system_info = f"Platform: {platform.system()} {platform.release()}"
        python_info = f"Python: {platform.python_version()}"
        
        header_title = "SYSTEM RESOURCE MONITOR"
        header = [
            center_text(f"📊 {header_title} 📊", term_width),
            center_text(f"Time: {current_time} | {system_info} | {python_info}", term_width),
            ""
        ]
        
        for line in header:
            print(line)
        
        cpu_percent = cpu_info['percent']
        cpu_content = [
            f"Usage: {progress_bar(cpu_percent, width=40, style='modern')}",
            f"Logical Cores: {cpu_info['cores']} | Physical Cores: {cpu_info['physical_cores']}",
            f"Frequency: Current: {cpu_info['freq_current']:.2f} MHz" if not isinstance(cpu_info['freq_current'], str) else f"Frequency: Current: {cpu_info['freq_current']}"
        ]
        
        cpu_box = draw_box("CPU", cpu_content, width=term_width-4)
        
        mem_percent = memory_info['percent']
        mem_content = [
            f"Usage: {progress_bar(mem_percent, width=40, style='modern')}",
            f"Total: {memory_info['total']:.2f} GB | Used: {memory_info['used']:.2f} GB | Available: {memory_info['available']:.2f} GB"
        ]
        
        mem_box = draw_box("MEMORY", mem_content, width=term_width-4)
        
        net_content = [
            f"Total Sent: {network_info['bytes_sent']:.2f} MB",
            f"Total Received: {network_info['bytes_recv']:.2f} MB"
        ]
        
        net_box = draw_box("NETWORK", net_content, width=term_width-4)
        
        proc_content = [f"{'PID':<10} {'CPU%':<10} {'MEM%':<10} {'NAME':<30}"]
        proc_content.append("─" * (term_width-6))
        
        for proc in processes:
            cpu_pct = proc['cpu_percent']
            if colorama_available:
                if cpu_pct < 5:
                    cpu_color = Fore.GREEN
                elif cpu_pct < 20:
                    cpu_color = Fore.YELLOW
                else:
                    cpu_color = Fore.RED
                    
                proc_line = f"{proc['pid']:<10} {cpu_color}{cpu_pct:<10.1f}{Style.RESET_ALL} {proc['memory_percent']:<10.1f} {proc['name'][:30]}"
            else:
                proc_line = f"{proc['pid']:<10} {cpu_pct:<10.1f} {proc['memory_percent']:<10.1f} {proc['name'][:30]}"
            proc_content.append(proc_line)
        
        proc_box = draw_box("TOP PROCESSES", proc_content, width=term_width-4)
        
        for section in [cpu_box, mem_box, net_box, proc_box]:
            for line in section:
                print(line)
            print()
            
        print(center_text("Press Ctrl+C to exit", term_width))
        
    except Exception as e:
        print(f"Error displaying system information: {e}")
        time.sleep(5)

def main():
    print("Initializing System Resource Monitor...")
    print("Cross-platform support: Windows, Linux, and macOS")
    print("Press Ctrl+C to exit")
    time.sleep(1)
    
    try:
        while True:
            display_system_info()
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nExiting System Monitor...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
