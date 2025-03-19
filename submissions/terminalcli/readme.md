# OSINT Rizzler - A Comprehensive OSINT Tool

**OSINT Rizzler** is a powerful Open Source Intelligence (OSINT) tool designed to gather and analyze publicly available information from various sources. It provides a wide range of functionalities, including domain WHOIS lookup, IP address lookup, email breach checks, DNS record retrieval, social media searches, port scanning, reverse IP lookups, subdomain enumeration, and website security checks. This tool is ideal for cybersecurity professionals, penetration testers, and anyone interested in OSINT.

---

## Features

1. **Domain WHOIS Lookup**  
   Retrieve detailed information about a domain, including registrar, creation date, expiration date, and name servers.

2. **IP Address Lookup**  
   Fetch information about an IP address, such as organization, country, city, and region.

3. **Email Breach Check**  
   Check if an email address has been involved in data breaches using the EmailRep API.

4. **Get DNS Records**  
   Retrieve DNS records (A, MX, TXT) for a domain.

5. **Social Media Search**  
   Search for a username across popular social media platforms (Twitter, Instagram, Facebook).

6. **Port Scanning & Banner Grabbing**  
   Scan common ports on a target IP or domain to identify open ports.

7. **Reverse IP Lookup**  
   Perform a reverse IP lookup to find hostnames associated with an IP address.

8. **Subdomain Enumeration**  
   Enumerate subdomains for a given domain.

9. **Website Security Check**  
   Check for missing security headers on a website (e.g., Content-Security-Policy, X-Frame-Options).

10. **Report Generation**  
    Save all findings to a JSON report file (`ossint_rizzler_dump.json`) for further analysis.

---

## Installation

### Prerequisites
- Python 3.x
- Required Python libraries (install via `pip`)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/osint-rizzler.git
   cd osint-rizzler
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory and add your API keys (if applicable):
   ```plaintext
   SHODAN_API_KEY=your_shodan_api_key_here
   ```

4. Run the tool:
   ```bash
   python osint.py
   ```

---

## Usage

### Running the Tool
After installation, execute the script:
```bash
python osint.py
```

You will be presented with a menu of options. Select the desired functionality by entering the corresponding number.

### Example Workflow
1. **Domain WHOIS Lookup**  
   Enter a domain name to retrieve WHOIS information.

2. **Email Breach Check**  
   Enter an email address to check if it has been involved in data breaches.

3. **Port Scanning**  
   Enter an IP address or domain to scan for open ports.

4. **Social Media Search**  
   Enter a username to search across social media platforms.

5. **Generate Reports**  
   All findings are automatically saved to `ossint_rizzler_dump.json` for later review.

---

## Code Structure

### Key Functions
- **`get_domain_info()`**: Fetches WHOIS information for a domain.
- **`get_ip_info()`**: Retrieves IP address details using the `ipinfo.io` API.
- **`check_email_breach()`**: Checks if an email has been involved in breaches using the EmailRep API.
- **`get_dns_records()`**: Retrieves DNS records (A, MX, TXT) for a domain.
- **`port_scan()`**: Scans common ports on a target IP or domain.
- **`social_media_search()`**: Searches for a username on social media platforms.
- **`reverse_ip_lookup()`**: Performs a reverse IP lookup to find associated hostnames.
- **`subdomain_enum()`**: Enumerates subdomains for a given domain.
- **`check_website_security()`**: Checks for missing security headers on a website.

### Helper Functions
- **`print_banner()`**: Displays the tool's banner.
- **`clear_screen()`**: Clears the terminal screen.
- **`save_report(data)`**: Saves findings to a JSON report file.
- **`loading_animation(message)`**: Displays a loading animation during long operations.

---

## Dependencies

The tool relies on the following Python libraries:
- `python-whois`: For WHOIS lookups.
- `requests`: For making HTTP requests.
- `dnspython`: For DNS record retrieval.
- `socket`: For port scanning and reverse IP lookups.
- `mimetypes`: For file metadata extraction.
- `socialscan`: For username availability checks (optional).

Install all dependencies using:
```bash
pip install -r requirements.txt
```

---

## Report Generation

All findings are saved to a JSON file (`ossint_rizzler_dump.json`) in the following format:
```json
{
  "WHOIS Information": {
    "Domain": "example.com",
    "Registrar": "Example Registrar",
    "Creation Date": "2020-01-01 12:00:00",
    "Expiration Date": "2025-01-01 12:00:00",
    "Name Servers": ["ns1.example.com", "ns2.example.com"]
  },
  "IP Information": {
    "IP": "192.168.1.1",
    "Organization": "Example Org",
    "Country": "United States",
    "City": "New York",
    "Region": "NY"
  }
}
```

---

## Contributing

Contributions are welcome! If you'd like to add new features, improve existing ones, or fix bugs, please follow these steps:
1. Fork the repository.
2. Create a new branch for your changes.
3. Submit a pull request with a detailed description of your changes.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Disclaimer

This tool is intended for educational and ethical purposes only. Do not use it for illegal or malicious activities. The developers are not responsible for any misuse of this tool.

---

## Support

For questions, issues, or feature requests, please open an issue on the [GitHub repository](https://github.com/yourusername/osint-rizzler/issues).

---

Happy OSINT-ing! 🕵️‍♂️