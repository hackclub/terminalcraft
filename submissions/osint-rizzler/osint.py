
from dotenv import load_dotenv
import os
import whois
import requests
from socialscan.util import Platforms, sync_execute_queries
import asyncio
import dns.resolver
import json
from datetime import datetime
import mimetypes
import socket
import itertools
import sys
import time

load_dotenv()
REPORT_FILE = "ossint_rizzler_dump.json"

def print_banner():
    print("\033[1;34m")  # blueeee
    print("""
 ██████╗ ███████╗██╗███╗   ██╗████████╗    ██████╗ ██╗███████╗███████╗██╗     ███████╗██████╗ 
██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝    ██╔══██╗██║╚══███╔╝╚══███╔╝██║     ██╔════╝██╔══██╗
██║   ██║███████╗██║██╔██╗ ██║   ██║       ██████╔╝██║  ███╔╝   ███╔╝ ██║     █████╗  ██████╔╝
██║   ██║╚════██║██║██║╚██╗██║   ██║       ██╔══██╗██║ ███╔╝   ███╔╝  ██║     ██╔══╝  ██╔══██╗
╚██████╔╝███████║██║██║ ╚████║   ██║       ██║  ██║██║███████╗███████╗███████╗███████╗██║  ██║
 ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝       ╚═╝  ╚═╝╚═╝╚══════╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═╝                                                                          
          """)
    print("\033[0m")  

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def save_report(data):
    try:
        with open(REPORT_FILE, "a") as f:
            json.dump(data, f, indent=4)
            f.write("\n")
    except Exception as e:
        print(f"Error saving report: {e}")

def get_domain_info():
    domain = input("Enter Domain: ")
    try:
        info = whois.whois(domain)
        
        clear_screen()
        print_banner()

        creation_date = info.creation_date[0] if isinstance(info.creation_date, list) else info.creation_date
        expiration_date = info.expiration_date[0] if isinstance(info.expiration_date, list) else info.expiration_date
        print("\033[1;34m") 
        print("\n[WHOIS INFORMATION]")
        print("\033[0m")
        print(f"Domain: {info.domain_name}")
        print(f"Registrar: {info.registrar}")
        print(f"Creation Date: {creation_date.strftime('%Y-%m-%d %H:%M:%S') if creation_date else 'N/A'}")
        print(f"Expiration Date: {expiration_date.strftime('%Y-%m-%d %H:%M:%S') if expiration_date else 'N/A'}")
        print(f"Name Servers: {info.name_servers}")
    except Exception as e:
        print(f"Error fetching WHOIS info: {e}")

def get_ip_info():
    ip = input("Enter IP address: ")
    try:
        response = requests.get(f"http://ipinfo.io/{ip}/json")
        info = response.json()
        print("\033[1;34m") 
        print("\n[IP Information]")
        print("\033[0m")
        print(f"IP: {info.get('ip', 'N/A')}")
        print(f"Organization: {info.get('org', 'N/A')}")
        print(f"Country: {info.get('country', 'N/A')}")
        print(f"City: {info.get('city', 'N/A')}")
        print(f"Region: {info.get('region', 'N/A')}")
    except Exception as e:
        print(f"Error fetching IP info: {e}")

def check_email_breach():
    email = input("Enter e-mail: ")
    url = f"https://emailrep.io/{email}"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200 and data.get("details"):
            print(f"\n\033[1;31m[BREACH FOUND] {email} has been involved in breaches!\033[0m")
            print(f"Reputation: {data.get('reputation', 'Unknown')}")
            print(f"Suspicious: {data.get('suspicious', 'Unknown')}")
            print(f"Data Leaks: {data.get('details').get('data_breach', 'Unknown')}")
        else:
            print(f"\n\033[1;32m[SAFE] No known breaches for {email}.\033[0m")
    except Exception as e:
        print(f"Error checking email breach: {e}")

# def check_username_availability():
#     # username = input("Enter username: ")
#     # platforms = list(Platforms)
#     # results = await sync_execute_queries(username, platforms, [])
#     # for x in results:
#     #     print(f"{x.url}: {'Available' if x.available else 'Taken'}")
    
#     queries = ["username1", "email2@gmail.com", "mail42@me.com"]
#     platforms = [Platforms.GITHUB]
#     results = sync_execute_queries(queries, platforms)
#     for result in results:
#         print(f"{result.query} on {result.platform}: {result.message} (Success: {result.success}, Valid: {result.valid}, Available: {result.available})")


def extract_metadata():
    file_path = input("Enter file path: ")
    if not os.path.exists(file_path):
        print("Error: File does not exist.")
        return
    
    metadata = {
        "Filename": os.path.basename(file_path),
        "File Size (bytes)": os.path.getsize(file_path),
        "Creation Time": datetime.fromtimestamp(os.path.getctime(file_path)).strftime('%Y-%m-%d %H:%M:%S'),
        "Modification Time": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S'),
        "MIME Type": mimetypes.guess_type(file_path)[0] or "Unknown",
        "Location": os.path.abspath(file_path)  
    }

    save_report({"File Metadata": metadata})
    print(json.dumps(metadata, indent=4))


def port_scan():
    target = input("Enter IP or domain to scan: ")
    ports = [21, 22, 25, 53, 80, 80, 443, 8080]
    open_ports = []
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    save_report({"Port Scan": open_ports})
    print(f"Open Ports: {open_ports}")

def loading_animation(message):
    spinner = itertools.cycle(['|', '/', '-', '\\'])
    for _ in range(30): 
        sys.stdout.write(f"\r{message} {next(spinner)}")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * (len(message) + 2) + "\r")
    sys.stdout.flush()

def social_media_search():
    username = input("Enter username: ")
    loading_animation("Searching social media")
    results = {}
    sites = ["https://twitter.com/", "https://instagram.com/", "https://facebook.com/"]   
    for site in sites:
        url = site + username
        response = requests.get(url)
    results[url] = "Exists" if response.status_code == 200 else "Not Found"
    save_report({"Social Media Search": results})
    print(json.dumps(results, indent=4))


def get_dns_records():
    domain = input("Enter domain: ")
    loading_animation("Loading DNS Records.") 
    try:
        records = {}
        for record_type in ["A", "MX", "TXT"]:
            answers = dns.resolver.resolve(domain, record_type)
            records[record_type] = [answer.to_text() for answer in answers]
        save_report({"DNS Records": records})
        print(json.dumps(records, indent=4))
    except Exception as e:
        print(f"Error fetching DNS records: {e}")        


def reverse_ip_lookup():
    ip = input("Enter IP Address: ")
    loading_animation("Performing IP Address lookup")

    try:
        hostnames = socket.gethostbyaddr(ip)
        save_report({"Reverse IP Lookup": hostnames})
        print(f"Hostnames: {hostnames}")
    except socket.herror:
        print("No hostnames found!")

def subdomain_enum():
    domain = input("Enter domain: ")
    loading_animation("Enumerating subdomains")
    subdomains = ["mail", "www", "ftp", "blog"]
    found_subdomains = []
    for sub in subdomains:
        subdomain = f"{sub}.{domain}"
        try:
            dns.resolver.resolve(subdomain, "A")
            found_subdomains.append(subdomain)
        except dns.resolver.NXDOMAIN:
            pass
    save_report({"Subdomains": found_subdomains})
    print("Found Subdomains:", found_subdomains)


def check_website_security():
    url = input("Enter website URL: ")
    loading_animation("Checking website security")
    headers = requests.get(url).headers
    security_headers = ["Content-Security-Policy", "X-Frame-Options", "X-XSS-Protection"]
    missing_headers = [h for h in security_headers if h not in headers]
    save_report({"Missing Security Headers": missing_headers})
    print("Missing Security Headers:", missing_headers)

def run_async(func):
    asyncio.run(func())

def main():
    while True:
        clear_screen()
        print_banner()
        print("1. Domain WHOIS Lookup")
        print("2. IP Address Lookup")
        print("3. Email Breach Check")
        print("4. Get DNS Records")
        print("5. Social Media Search")
        print("6. Port Scanning & Banner Grabbing")
        print("7. Reverse IP Lookup")
        print("8. Subdomain Enumeration")
        print("9. Website Security Check")
        print("10. Exit")
        choice = input("\033[1;36mSelect an option (1-10): \033[0m")
        
        if choice == "1":
            get_domain_info()
        elif choice == "2":
            get_ip_info()
        elif choice == "3":
            check_email_breach()
        elif choice == "4":
            get_dns_records()
        elif choice == "5":
            social_media_search()
        elif choice == "6":
            port_scan()
        elif choice == "7":
            reverse_ip_lookup()
        elif choice == "8":
            subdomain_enum()
        elif choice == "9":
            check_website_security()
        elif choice == "10":
            print("Exiting OSINT Rizzler. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 10.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()