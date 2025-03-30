# PhishDetect: A CLI Tool for Phishing Detection

import requests
import whois
import re
import argparse
from urllib.parse import urlparse
from pyfiglet import figlet_format

# Suspicious keywords that indicate phishing in URLs or emails
SUSPICIOUS_KEYWORDS = [
    'login', 'verify', 'update', 'secure', 'account', 'bank', 'signin',
    'confirm', 'password', 'auth', 'webscr', 'pay', 'ebayisapi', 'wp-',
    'admin', 'support', 'secure', 'verification', 'suspend', 'compromised'
]

# Suspicious file extensions often used in phishing attachments
SUSPICIOUS_EXTENSIONS = ['exe', 'bat', 'scr', 'pif', 'cmd', 'com', 'vbs', 'js', 'jse', 'wsf', 'wsh']

# Function to check if the URL contains suspicious keywords
def is_suspicious_url(url):
    return any(keyword in url.lower() for keyword in SUSPICIOUS_KEYWORDS)

# Function to check the domain age
def get_domain_age(domain):
    try:
        domain_info = whois.whois(domain)
        if domain_info.creation_date:
            return str(domain_info.creation_date)
        else:
            return 'Unknown'
    except:
        return 'Unable to retrieve domain info'

# Function to check URL reputation using Google Safe Browsing API
def check_url_reputation(url, api_key):
    api_url = f'https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}'
    body = {
        'client': {'clientId': 'phishdetect', 'clientVersion': '1.0'},
        'threatInfo': {
            'threatTypes': ['MALWARE', 'SOCIAL_ENGINEERING'],
            'platformTypes': ['ANY_PLATFORM'],
            'threatEntryTypes': ['URL'],
            'threatEntries': [{'url': url}]
        }
    }
    try:
        response = requests.post(api_url, json=body)
        result = response.json()
        if 'matches' in result:
            return 'Unsafe according to Google Safe Browsing.'
        return 'Safe according to Google Safe Browsing.'
    except:
        return 'Unable to check reputation.'

# Function to analyze URLs
def analyze_url(url, api_key=None):
    print(f'🔍 Analyzing: {url}')
    parsed_url = urlparse(url)
    domain = parsed_url.netloc

    # HTTPS Check
    if parsed_url.scheme == 'https':
        print('✅ Secure HTTPS connection detected.')
    else:
        print('❗ Warning: The site is not using HTTPS!')

    # TLD Check
    if domain.endswith(('.com', '.org', '.net', '.edu')):
        print('✅ TLD seems safe.')
    else:
        print('⚠️ Uncommon TLD detected.')

    # URL Length Check
    if len(domain) > 10:
        print('✅ No URL shortener detected.')
    else:
        print('⚠️ URL shortener detected.')

    # Domain Age Check
    print(f'Domain Age: {get_domain_age(domain)}')

    # Reputation Check (if API key is provided)
    if api_key:
        print(check_url_reputation(url, api_key))

# Function to analyze email content
def analyze_email(content):
    print('\n📧 Analyzing Email Content...')
    urls = re.findall(r'(https?://[\w./-]+)', content)
    suspicious = any(keyword in content.lower() for keyword in SUSPICIOUS_KEYWORDS)

    # Check for suspicious keywords
    if suspicious:
        detected_keywords = set([kw for kw in SUSPICIOUS_KEYWORDS if kw in content.lower()])
        print(f'🚨 Suspicious keywords detected: {", ".join(detected_keywords)}')

    # Attachment Inspection
    attachments = re.findall(r'\.(\w+)', content)
    detected_extensions = set([ext for ext in attachments if ext in SUSPICIOUS_EXTENSIONS])
    if detected_extensions:
        print(f'⚠️ Dangerous attachment detected: {", ".join(detected_extensions)}')

    # Check for urgent or threatening language
    if re.search(r"(urgent|immediate action|compromised|suspend|deactivate)", content, re.IGNORECASE):
        print("⚠️ Urgent or threatening language detected!")

    # Check for generic greetings
    if re.search(r"(dear user|dear customer|valued client)", content, re.IGNORECASE):
        print("⚠️ Generic greeting detected!")

    # Check for mismatched domains in email addresses
    email_domains = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", content)
    for email in email_domains:
        domain = email.split('@')[1]
        if domain not in ["officialsite.com", "trustedsource.com"]:
            print(f"⚠️ Unrecognized or mismatched domain in email address: {email}")

    # Extract and analyze URLs if present
    if urls:
        print("\n🔗 Extracted URLs from Email:")
        for url in urls:
            if is_suspicious_url(url):
                print(f'⚠️ Warning: This URL contains phishing indicators!')
    else:
        print("✅ No URLs found in the email text.")

# Main function to parse arguments and run the analysis
def main():
    print(figlet_format("PhishDetect", font="slant"))
    parser = argparse.ArgumentParser(description='PhishDetect: Phishing Detection Tool')
    parser.add_argument('--url', help='Analyze a URL')
    parser.add_argument('--file', help='Analyze email content from a file')
    parser.add_argument('--api_key', help='API key for Google Safe Browsing')
    args = parser.parse_args()

    if args.url:
        analyze_url(args.url, args.api_key)
    elif args.file:
        try:
            with open(args.file, 'r') as f:
                email_content = f.read()
            analyze_email(email_content)
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.")
    else:
        print('Please provide a valid URL or email file for analysis.')

if __name__ == '__main__':
    main()
