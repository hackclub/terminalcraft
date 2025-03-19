import socket
import time
import subprocess
import platform
import re
import sys
import ipaddress
from urllib.request import urlopen
from urllib.parse import quote

def validate_port(port):
    try:
        port_num = int(port)
        if 1 <= port_num <= 65535:
            return port_num
        else:
            raise ValueError(f"Port must be between 1 and 65535, got {port_num}")
    except ValueError:
        raise ValueError(f"Port must be a valid integer, got {port}")

def check_port(host, port, timeout=3):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    
    try:
        sock.connect((host, port))
        sock.close()
        return True
    except socket.timeout:
        return False, "Connection timed out"
    except ConnectionRefusedError:
        return False, "Connection refused"
    except socket.gaierror:
        return False, "Could not resolve hostname"
    except OSError as e:
        return False, str(e)
    except Exception as e:
        return False, f"An unexpected error occurred: {e}"

def traceroute(host, max_hops=30, timeout=1):
    """
    Perform a traceroute to the specified host.
    
    Args:
        host (str): The target hostname or IP address
        max_hops (int): Maximum number of hops to trace
        timeout (float): Timeout in seconds for each hop
        
    Returns:
        list: List of dictionaries with hop information
    """
    os_name = platform.system().lower()
    
    try:
        socket.gethostbyname(host)
        
        if os_name == "windows":
            return _traceroute_windows(host, max_hops, timeout)
        elif os_name in ["linux", "darwin"]: 
            return _traceroute_unix(host, max_hops, timeout)
        else:
            return [{"hop": 0, "ip": None, "hostname": None, "time": None, 
                    "error": f"Unsupported operating system: {os_name}"}]
    except socket.gaierror:
        return [{"hop": 0, "ip": None, "hostname": None, "time": None, 
                "error": f"Could not resolve hostname: {host}"}]
    except Exception as e:
        return [{"hop": 0, "ip": None, "hostname": None, "time": None, 
                "error": f"Error during traceroute: {str(e)}"}]

def _traceroute_windows(host, max_hops, timeout):
    timeout_ms = int(timeout * 1000)
    result = []
    
    try:
        cmd = ['tracert', '-d', '-h', str(max_hops), '-w', str(timeout_ms), host]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        skip_count = 0
        for line in process.stdout:
            skip_count += 1
            if "Tracing route" in line:
                break
            if skip_count > 5: 
                break
        
        hop_num = 0
        for line in process.stdout:
            line = line.strip()
            
            if not line:
                continue
            
            if line[0].isdigit():
                hop_num = int(line.split()[0])
                

                if "Request timed out" in line:
                    result.append({
                        "hop": hop_num,
                        "ip": None,
                        "hostname": None,
                        "time": None,
                        "error": "Request timed out"
                    })
                    continue
                
                ip_match = re.search(r'(\d+\.\d+\.\d+\.\d+)', line)
                ip = ip_match.group(1) if ip_match else None
                
                times = re.findall(r'(\d+) ms', line)
                avg_time = sum(int(t) for t in times) / len(times) if times else None
                
                hostname = None
                if ip:
                    try:
                        hostname = socket.gethostbyaddr(ip)[0]
                    except:
                        hostname = ip
                
                result.append({
                    "hop": hop_num,
                    "ip": ip,
                    "hostname": hostname,
                    "time": avg_time,
                    "error": None if ip else "No response"
                })
        
        process.terminate()
        return result
    except subprocess.SubprocessError as e:
        return [{"hop": 0, "ip": None, "hostname": None, "time": None, 
                "error": f"Error running tracert: {str(e)}"}]

def _traceroute_unix(host, max_hops, timeout):
    result = []
    
    try:
        cmd = ['traceroute', '-n', '-m', str(max_hops), '-w', str(timeout), host]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        next(process.stdout)
        
        for line in process.stdout:
            line = line.strip()
            match = re.search(r'^\s*(\d+)\s+(?:(\d+\.\d+\.\d+\.\d+)|(\*))', line)
            
            if not match:
                continue
                
            hop = int(match.group(1))
            ip = match.group(2) if match.group(2) else None
            
            times = re.findall(r'(\d+\.\d+) ms', line)
            avg_time = sum(float(t) for t in times) / len(times) if times else None
            
            hostname = None
            if ip:
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except:
                    hostname = ip
            
            result.append({
                "hop": hop,
                "ip": ip,
                "hostname": hostname,
                "time": avg_time,
                "error": "No response" if not ip else None
            })
        
        process.terminate()
        return result
    except FileNotFoundError:
        return _traceroute_ping_fallback(host, max_hops, timeout)
    except subprocess.SubprocessError as e:
        return [{"hop": 0, "ip": None, "hostname": None, "time": None, 
                "error": f"Error running traceroute: {str(e)}"}]

def _traceroute_ping_fallback(host, max_hops, timeout):
    result = []
    
    for ttl in range(1, max_hops + 1):
        if platform.system().lower() == "darwin":
            cmd = ['ping', '-c', '1', '-t', str(ttl), '-W', str(int(timeout * 1000)), host]
        else:
            cmd = ['ping', '-c', '1', '-t', str(ttl), '-W', str(int(timeout)), host]
        
        try:
            output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
            
            dest_reached = False
            ip = None
            time_ms = None
            
            ip_match = re.search(r'from (\d+\.\d+\.\d+\.\d+)', output)
            if ip_match:
                ip = ip_match.group(1)
                
                time_match = re.search(r'time=(\d+\.\d+) ms', output)
                if time_match:
                    time_ms = float(time_match.group(1))
                
                if ip == socket.gethostbyname(host):
                    dest_reached = True
            
            hostname = None
            if ip:
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                except:
                    hostname = ip
            
            result.append({
                "hop": ttl,
                "ip": ip,
                "hostname": hostname,
                "time": time_ms,
                "error": None
            })
            
            if dest_reached:
                break
                
        except subprocess.CalledProcessError as e:
            if "Time to live exceeded" in e.output:
                ip_match = re.search(r'from (\d+\.\d+\.\d+\.\d+)', e.output)
                ip = ip_match.group(1) if ip_match else None
                
                hostname = None
                if ip:
                    try:
                        hostname = socket.gethostbyaddr(ip)[0]
                    except:
                        hostname = ip
                
                result.append({
                    "hop": ttl,
                    "ip": ip,
                    "hostname": hostname,
                    "time": None,
                    "error": None
                })
            else:
                result.append({
                    "hop": ttl,
                    "ip": None,
                    "hostname": None,
                    "time": None,
                    "error": "Request timed out"
                })
    
    return result

def whois(domain_or_ip):
    """
    Perform WHOIS lookup for a domain or IP address.
    
    Args:
        domain_or_ip (str): The domain name or IP address to look up
        
    Returns:
        str: WHOIS information text
    """
    try:
        # Check if the input is an IP address
        try:
            ipaddress.ip_address(domain_or_ip)
            is_ip = True
        except ValueError:
            is_ip = False
        
        # Try using external WHOIS API for consistent results
        if is_ip:
            url = f"https://rdap.arin.net/registry/ip/{domain_or_ip}"
        else:
            url = f"https://rdap.org/domain/{quote(domain_or_ip)}"
        
        try:
            with urlopen(url, timeout=10) as response:
                if response.status == 200:
                    import json
                    data = json.loads(response.read().decode('utf-8'))
                    return _format_whois_data(data, is_ip)
        except Exception as e:
            pass  # Fall back to command-line WHOIS
        
        # Fall back to system's WHOIS command
        if platform.system().lower() == "windows":
            return _whois_windows(domain_or_ip)
        else:
            return _whois_unix(domain_or_ip)
    except Exception as e:
        return f"Error performing WHOIS lookup: {str(e)}"

def _whois_windows(domain_or_ip):
    """Windows implementation using external service"""
    try:
        # Windows doesn't have a native whois command
        # Use socket to connect to whois server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("whois.iana.org", 43))
        s.send((domain_or_ip + "\r\n").encode())
        
        response = b""
        while True:
            data = s.recv(4096)
            if not data:
                break
            response += data
        s.close()
        
        text = response.decode('utf-8', errors='ignore')
        
        # Extract the appropriate whois server
        refer_match = re.search(r"refer:\s+(\S+)", text, re.IGNORECASE)
        if refer_match:
            whois_server = refer_match.group(1)
            
            # Query the specific whois server
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((whois_server, 43))
            s.send((domain_or_ip + "\r\n").encode())
            
            response = b""
            while True:
                data = s.recv(4096)
                if not data:
                    break
                response += data
            s.close()
            
            return response.decode('utf-8', errors='ignore')
        
        return text
    except Exception as e:
        # Try an alternative method - querying web service
        try:
            with urlopen(f"https://www.whois.com/whois/{quote(domain_or_ip)}", timeout=10) as response:
                html = response.read().decode('utf-8')
                # Extract whois data from HTML (simple approach)
                if '<div class="whois-data">' in html:
                    start = html.index('<div class="whois-data">') + 24
                    end = html.index('</div>', start)
                    data = html[start:end].strip()
                    return data.replace('<br>', '\n').replace('&nbsp;', ' ')
        except:
            pass
        
        return f"Error performing WHOIS lookup: {str(e)}"

def _whois_unix(domain_or_ip):
    """Unix implementation using whois command"""
    try:
        output = subprocess.check_output(['whois', domain_or_ip], universal_newlines=True)
        return output
    except subprocess.CalledProcessError as e:
        return f"Error running whois command: {str(e)}"
    except FileNotFoundError:
        return "WHOIS command not found. Please install whois package."

def _format_whois_data(data, is_ip=False):
    """Format JSON WHOIS data into readable text"""
    result = []
    
    # Add header
    if is_ip:
        result.append(f"WHOIS for IP: {data.get('handle', '')}")
    else:
        result.append(f"WHOIS for domain: {data.get('handle', '')}")
    
    result.append("-" * 50)
    
    # Extract registration and expiration dates
    events = data.get('events', [])
    for event in events:
        if event.get('eventAction') == 'registration':
            result.append(f"Registration Date: {event.get('eventDate', 'Unknown')}")
        elif event.get('eventAction') == 'expiration':
            result.append(f"Expiration Date: {event.get('eventDate', 'Unknown')}")
    
    # Extract nameservers
    nameservers = data.get('nameservers', [])
    if nameservers:
        result.append("\nNameservers:")
        for ns in nameservers:
            result.append(f"  {ns.get('ldhName', '')}")
    
    # Extract entities (organizations, persons)
    entities = data.get('entities', [])
    if entities:
        result.append("\nRegistrar/Entities:")
        for entity in entities:
            result.append(f"  Role: {entity.get('roles', ['Unknown'])[0]}")
            result.append(f"  Handle: {entity.get('handle', 'Unknown')}")
            result.append(f"  Name: {entity.get('vcardArray', [[],[]])[-1][-1][-1] if len(entity.get('vcardArray', [[],[]]))>1 else 'Unknown'}")
            
            # Add contact info if available
            vcard = entity.get('vcardArray', [])
            if len(vcard) > 1:
                for item in vcard[1]:
                    if item[0] == 'email':
                        result.append(f"  Email: {item[3]}")
                    elif item[0] == 'tel':
                        result.append(f"  Phone: {item[3]}")
            
            result.append("")
    
    # Add status information
    statuses = data.get('status', [])
    if statuses:
        result.append("\nStatus:")
        for status in statuses:
            result.append(f"  {status}")
    
    # If we couldn't parse the JSON properly, just return the raw data
    if len(result) < 5:
        import json
        return json.dumps(data, indent=2)
    
    return "\n".join(result)
