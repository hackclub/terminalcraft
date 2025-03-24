#!/usr/bin/env python3
import os
import re
import sys
import whois
import requests
from datetime import datetime
import pyfiglet

def display_banner():
    banner = pyfiglet.figlet_format("PhishDetect")
    print(banner)
    print("=" * 50)
    print(" Welcome to PhishDetect - Your Phishing Scanner ")
    print("=" * 50)

def main_menu():
    print("\n1. Scan a URL")
    print("2. Scan an Email")
    print("3. Exit")
    choice = input("Enter your choice: ")
    return choice

# Example usage
display_banner()
user_choice = main_menu()
print(f"You selected option {user_choice}.")

# List of known phishing keywords
PHISHING_KEYWORDS = ["login", "verify", "secure", "bank", "update", "paypal", "account", "password", "confirm", "alert", "prompt", "onerror", "img src", "billing", "invoice", "suspicious", "security", "auth", "authentication", "reset", "deactivate", "warning", "locked", "unusual activity", "support", "restricted", "reactivate", "session", "personal info", "credential", "access", "restore", "validate", "payment", "checkout", "fraud", "identity", "urgent"]

# Suspicious Top-Level Domains (TLDs)
SUSPICIOUS_TLDS = [".xyz", ".tk", ".gq", ".cf", ".ml"]

# URL shorteners that may hide phishing links
SHORTENERS = ["bit.ly", "tinyurl.com", "t.co", "goo.gl"]

# Regular expression for extracting URLs
URL_REGEX = r"https?://[^\s/$.?#].[^\s]*"

# Retrieve Google API key from environment variables
GOOGLE_API_KEY = "your-google-api-key-here"

if not GOOGLE_API_KEY:
    print("[ERROR] Google Safe Browsing API key is missing. Set GOOGLE_API_KEY in environment variables.")

def extract_urls(text):
    """Extracts URLs from a given text."""
    return re.findall(URL_REGEX, text)

def contains_phishing_keywords(url):
    """Checks if the URL contains phishing-related keywords."""
    return any(keyword in url.lower() for keyword in PHISHING_KEYWORDS)

def check_domain_age(url):
    """Checks the domain age using WHOIS lookup."""
    try:
        domain = re.sub(r"https?://(www\.)?", "", url).split('/')[0]
        domain_info = whois.whois(domain)
        creation_date = domain_info.creation_date

        if isinstance(creation_date, list):
            creation_date = creation_date[0]  # Handle multiple dates
        
        if not creation_date:
            return "Unknown"

        age_days = (datetime.now() - creation_date).days
        return f"{age_days} days old" if age_days else "Recently registered"
    
    except:
        return "Unable to retrieve domain info"

def check_https(url):
    """Checks if the URL uses HTTPS."""
    return "[ALERT] The site is not using HTTPS!" if not url.startswith("https://") else "Secure HTTPS connection detected."

def check_tld(url):
    """Checks if the URL has a suspicious TLD."""
    for tld in SUSPICIOUS_TLDS:
        if url.endswith(tld):
            return f"[WARNING] Suspicious TLD detected: {tld}"
    return "TLD seems safe."

def check_url_shortener(url):
    """Checks if the URL is a shortened link."""
    for shortener in SHORTENERS:
        if shortener in url:
            return "[WARNING] URL shortener detected. Might be hiding a phishing link!"
    return "No URL shortener detected."

def check_google_safe_browsing(url):
    """Checks if the URL is flagged by Google Safe Browsing API."""
    if not GOOGLE_API_KEY:
        return "[ERROR] Google Safe Browsing API key is missing. Skipping check."

    google_url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    params = {"key": GOOGLE_API_KEY}
    body = {
        "client": {"clientId": "phishdetect", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}],
        },
    }
    response = requests.post(google_url, json=body, params=params)
    result = response.json()

    if "matches" in result:
        return "[DANGER] This URL is flagged as malicious by Google Safe Browsing!"
    return "Safe according to Google Safe Browsing."

def check_whois_email(url):
    """Checks if the WHOIS email is available for the domain."""
    try:
        domain = re.sub(r"https?://(www\.)?", "", url).split('/')[0]
        domain_info = whois.whois(domain)
        if domain_info.emails:
            return f"WHOIS Email: {domain_info.emails}"
        return "[WARNING] No WHOIS email found! Could be suspicious."
    except:
        return "Unable to retrieve WHOIS info."

def analyze_url(url):
    """Runs all security checks on a given URL."""
    print(f"\n🔍 Analyzing: {url}")

    print(check_https(url))
    print(check_tld(url))
    print(check_url_shortener(url))
    print(f"Domain Age: {check_domain_age(url)}")
    print(check_google_safe_browsing(url))
    print(check_whois_email(url))

    if contains_phishing_keywords(url):
        print("[WARNING] Suspicious keywords detected in URL!")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./phishdetect.py <url> or ./phishdetect.py --file <filename>")
        sys.exit(1)

    if sys.argv[1] == "--file":
        filename = sys.argv[2]
        try:
            with open(filename, "r") as file:
                text = file.read()
                urls = extract_urls(text)
                if urls:
                    for url in urls:
                        analyze_url(url)
                else:
                    print("No URLs found in the file.")
        except FileNotFoundError:
            print("File not found.")
    else:
        analyze_url(sys.argv[1])
