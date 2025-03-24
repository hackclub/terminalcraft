# PhishDetect, a URL & Email phishing Detection Tool

PhishDetect is a command-line phishing detection tool that analyzes URLs and email text to detect malicious links. It uses **regex-based URL analysis,** domain reputation checks, WHOIS lookup, TLD verification, Google Safe Browsing API, and more** to identify potential phishing attempts.

## Features:
✔️ **Extract URLs** from email text or input  
✔️ **Detect phishing keywords** in URLs  
✔️ **Check domain age** via WHOIS lookup  
✔️ **Verify HTTPS security**  
✔️ **Identify suspicious TLDs** (.xyz, .tk, etc.)  
✔️ **Detect URL shorteners** (bit.ly, tinyurl, etc.)  
✔️ **Google Safe Browsing API check**  
✔️ **Analyze WHOIS Email** to check domain registration details <br>
✔️ **Excutable in Linux, Windows, and macOS**

## Set up:
** Make Sure that Python & pip are installed on your system
  You can check by:
      `python --version`

  If they are not installed, you can install them by:

  **Linux**: <br>
    `sudo apt intall python3 python3-pip` <br>
    `pip3 install requests python-whois` <br>
    `pip install pyfiglet`


  **macOs**: <br>
    `brew install python3` <br>
    `pip3 install requests python-whois` <br>
    `pip install pyfiglet`


  **Windows**: <br>
    Download Python from [python.org](url) and install it. <br>
      (Make sure to add the file in the System Path) <br>
    `pip install pyfiglet`


## Installation:
 ** You can install the tool simply by running this command in your terminal:

   **Linux & macOS:** <br>
    `git clone https://github.com/belalmostafaaa/Phishdetect.git` <br>
    `cd PhishDetect` <br>
    `pip3 install requests python-whois` <br>
    `chmod +x phishdetect.py` <br>
    `python3 phishdetect.py <url> or python phishdetect.py <url> or ./phishdetect.py <url>` <br>

  **Windows:** <br>
   `git clone https://github.com/belalmostafaaa/Phishdetect.git` <br>
    `cd PhishDetect` <br>
    `pip3 install requests python-whois` <br>
    `python3 phishdetect.py <url> or python phishdetect.py <url>`
