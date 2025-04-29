# OSINT Rizzler - OSINT & Reconnaissance Tool

OSINT Rizzler is a powerful reconnaissance tool designed to help security professionals and ethical hackers gather information about domains, IP addresses, emails, and websites. This tool provides various OSINT (Open Source Intelligence) techniques to facilitate information gathering.

## Features
- **Domain WHOIS Lookup**: Retrieve domain registration details.
- **IP Address Lookup**: Fetch geolocation and ASN information of an IP.
- **Email Breach Check**: Check if an email has been compromised in data breaches.
- **DNS Records Retrieval**: Obtain various DNS records of a domain.
- **Social Media Search**: Identify the presence of usernames on popular social platforms.
- **Port Scanning**: Scan for open ports and banner grabbing.
- **Reverse IP Lookup**: Discover domains hosted on a given IP.
- **Subdomain Enumeration**: Find subdomains associated with a domain.
- **Website Security Check**: Analyze missing security headers.

## Installation
Ensure you have Python installed on your system. Then, install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage
Run the script using:

```bash
python osint.py
```

You will be prompted to choose an option from the menu to perform reconnaissance tasks.

## Dependencies
- `requests`
- `whois`
- `socialscan`
- `dns.resolver`
- `socket`
- `itertools`

Ensure all dependencies are installed before running the script.

## Contribution
Contributions are welcome! Feel free to submit pull requests for enhancements or bug fixes.

## Disclaimer
This tool is intended for educational and ethical purposes only. Use it responsibly.

---

Happy Hacking!

