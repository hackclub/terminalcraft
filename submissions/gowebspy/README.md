# GoWebSpy

<p align="center">
  <a href="https://github.com/ArjunSharda/gowebspy/actions"><img src="https://github.com/ArjunSharda/gowebspy/workflows/Go/badge.svg" alt="Build Status"></a>
  <a href="https://goreportcard.com/report/github.com/ArjunSharda/gowebspy"><img src="https://goreportcard.com/badge/github.com/ArjunSharda/gowebspy" alt="Go Report"></a>
  <a href="https://pkg.go.dev/github.com/ArjunSharda/gowebspy"><img src="https://pkg.go.dev/badge/github.com/ArjunSharda/gowebspy.svg" alt="PkgGoDev"></a>
  <a href="https://github.com/ArjunSharda/gowebspy/blob/main/LICENSE"><img src="https://img.shields.io/github/license/ArjunSharda/gowebspy" alt="License"></a>
</p>

GoWebSpy is a powerful, comprehensive website information gathering tool. It provides an easy-to-use command-line interface and Go library for retrieving detailed information about websites, including HTTP headers, SSL certificates, WHOIS data, DNS records, port scanning, and more.

## ⚡ Features

- 🔍 Detailed website information: status codes, server details, response times
- 🔒 SSL certificate analysis and validation
- 📋 Complete HTTP headers inspection
- 📑 WHOIS domain registration data
- 🌐 DNS records lookup (A, AAAA, MX, TXT, NS, CNAME)
- 🔌 Port scanning for common services
- 🛣️ Real network path tracing (traceroute for both IPv4 and IPv6)
- 🌍 Full IPv6 support (DNS, traceroute, port scanning, dual-stack checking)
- 🔍 Advanced filtering options (status, headers, response time, SSL validity, etc.)
- 📱 Clean, color-coded console output
- 💻 JSON output for programmatic use
- 📦 Available as both a CLI tool and Go library

## 📦 Installation

### Using Go

```bash
go install github.com/ArjunSharda/gowebspy/cmd/gowebspy@latest
```

### From Source

```bash
git clone https://github.com/ArjunSharda/gowebspy.git
cd gowebspy
go mod tidy
go install ./cmd/gowebspy
```

## 🚀 Usage

### Command-Line Examples

#### Basic website information

```bash
gowebspy example.com
```

#### Show all available information

```bash
gowebspy github.com --all
# or
gowebspy github.com -a
```

#### SSL certificate information

```bash
gowebspy cloudflare.com --ssl
# or
gowebspy cloudflare.com -s
```

#### HTTP headers

```bash
gowebspy google.com --headers
# or
gowebspy google.com -H
```

#### WHOIS information

```bash
gowebspy microsoft.com --whois
# or
gowebspy microsoft.com -w
```

#### DNS records

```bash
gowebspy amazon.com --dns
# or
gowebspy amazon.com -d
```

#### Port scanning

```bash
gowebspy netflix.com --ports
# or
gowebspy netflix.com -p
```

#### IPv6 Support

```bash
# Prefer IPv6 for all operations
gowebspy google.com --ipv6

# Check both IPv4 and IPv6 support
gowebspy github.com --dual-stack

# Run IPv6 port scanning
gowebspy cloudflare.com --ports --ipv6

# IPv6 traceroute
gowebspy facebook.com --trace --ipv6
```

#### Advanced Filtering

```bash
# Filter by status code (exact or range)
gowebspy example.com --status 200
gowebspy example.com --status "200-299"

# Filter by server software
gowebspy example.com --server nginx

# Filter by response time
gowebspy example.com --response-time "<500ms"

# Filter by header existence
gowebspy example.com --has-header "Content-Security-Policy"

# Filter by SSL validity
gowebspy example.com --ssl-days ">30"

# Filter by content regex pattern
gowebspy example.com --regex "login|signup"
```

#### Traceroute

```bash
# IPv4 traceroute
gowebspy twitter.com --trace
# or
gowebspy twitter.com -t

# IPv6 traceroute
gowebspy twitter.com --trace --ipv6
```

#### JSON output (for scripting)

```bash
gowebspy facebook.com --json
# or
gowebspy facebook.com -j
```

### Sample Output

```
BASIC INFORMATION
==================================================
URL:            https://github.com
Title:          GitHub: Let's build from here
Description:    GitHub is where over 100 million developers shape the future of software, together. Contribute to the open source community, manage your Git repositories...
Status Code:    200
Server:         GitHub.com
Content Type:   text/html; charset=utf-8
Response Time:  245ms
IP Addresses:   140.82.121.3, 2606:50c0:8000::154

SSL CERTIFICATE INFORMATION
==================================================
Common Name:    github.com
Issuer:         DigiCert High Assurance TLS Hybrid ECC SHA256 2020 CA1
Valid:          Yes
Issued Date:    2022-11-08T00:00:00Z
Expiry Date:    2023-12-08T23:59:59Z
Days Until Expiry: 275 days
Alternative Names: github.com, www.github.com, *.github.com, *.github.io, ...

HTTP HEADERS
==================================================
Content-Type: text/html; charset=utf-8
Server: GitHub.com
Date: Fri, 10 Mar 2023 12:01:52 GMT
Content-Security-Policy: default-src 'none'; ...
Strict-Transport-Security: max-age=31536000; includeSubdomains; preload
...

WHOIS INFORMATION
==================================================
Registrar:      MarkMonitor Inc.
Created Date:   2007-10-09T18:20:50Z
Updated Date:   2022-09-07T09:10:44Z
Expires Date:   2024-10-09T18:20:50Z
Name Servers:   ns-1283.awsdns-32.org, ns-1707.awsdns-21.co.uk, ...
Domain Status:  clientDeleteProhibited, clientTransferProhibited, ...

DNS RECORDS
==================================================
A/AAAA Records: 140.82.121.3, 140.82.121.4, 2606:50c0:8000::154, 2606:50c0:8001::154
MX Records: aspmx.l.google.com (priority: 1), alt1.aspmx.l.google.com (priority: 5)
TXT Records: v=spf1 ip4:192.30.252.0/22 include:_netblocks.google.com ...
NS Records: ns-1283.awsdns-32.org, ns-1707.awsdns-21.co.uk, ...

PORT SCAN (IPv4)
==================================================
✓ Port 22 (SSH): Open
✓ Port 80 (HTTP): Open
✓ Port 443 (HTTPS): Open
✗ Port 21 (FTP): Closed
✗ Port 25 (SMTP): Closed
...

TRACEROUTE (IPv4)
==================================================
 1  192.168.1.1  10ms
 2  10.40.10.6  25ms
 3  10.60.15.9  40ms
 4  140.82.121.3  55ms

DUAL STACK SUPPORT
==================================================
IPv4 Support: Yes
IPv4 Addresses: 140.82.121.3, 140.82.121.4
IPv6 Support: Yes
IPv6 Addresses: 2606:50c0:8000::154, 2606:50c0:8001::154
Dual Stack: Yes
```

## 📚 Library Usage

GoWebSpy can also be used as a Go library in your applications:

```go
package main

import (
	"context"
	"fmt"
	"log"

	"github.com/ArjunSharda/gowebspy/pkg/gowebspy"
)

func main() {
	// Get basic website information
	info, err := gowebspy.GetWebsiteInfo("github.com")
	if err != nil {
		log.Fatalf("Error: %v", err)
	}

	fmt.Printf("URL: %s\n", info.URL)
	fmt.Printf("Title: %s\n", info.Title)
	fmt.Printf("Server: %s\n", info.ServerInfo)
	fmt.Printf("Status Code: %d\n", info.StatusCode)
	
	// Check SSL certificate
	if info.SSLInfo != nil {
		fmt.Printf("SSL Valid: %v\n", info.SSLInfo.Valid)
		fmt.Printf("SSL Expiry: %v\n", info.SSLInfo.Expiry)
	}
	
	// Get DNS records
	records, err := gowebspy.GetDNSRecords("github.com")
	if err != nil {
		log.Printf("DNS error: %v", err)
	} else {
		fmt.Println("DNS Records:", records)
	}
	
	// Get IPv6 records specifically
	ipv6Records, _ := gowebspy.GetIPv6DNSRecords("github.com")
	fmt.Println("IPv6 Records:", ipv6Records)
	
	// Check dual stack support
	isDualStack, _ := gowebspy.CheckDualStack("github.com")
	fmt.Println("Dual Stack Support:", isDualStack)
	
	// Scan ports (IPv4)
	ports := []int{22, 80, 443, 8080}
	results := gowebspy.PortScan("github.com", ports)
	for port, open := range results {
		fmt.Printf("Port %d: %v\n", port, open)
	}
	
	// Scan ports (IPv6)
	resultsIPv6 := gowebspy.PortScanIPv6("github.com", ports)
	for port, open := range resultsIPv6 {
		fmt.Printf("IPv6 Port %d: %v\n", port, open)
	}
	
	// Trace route (IPv4)
	hops, err := gowebspy.SimpleTraceroute(context.Background(), "github.com", 30)
	if err != nil {
		log.Printf("Traceroute error: %v", err)
	} else {
		for _, hop := range hops {
			fmt.Printf("Hop %d: %s (%s)\n", hop.Number, hop.IP, hop.RTT)
		}
	}
	
	// Trace route (IPv6)
	hopsIPv6, err := gowebspy.TracerouteIPv6(context.Background(), "github.com", 30)
	if err != nil {
		log.Printf("IPv6 Traceroute error: %v", err)
	} else {
		for _, hop := range hopsIPv6 {
			fmt.Printf("IPv6 Hop %d: %s (%s)\n", hop.Number, hop.IP, hop.RTT)
		}
	}
	
	// Using filters
	filterOpts := gowebspy.NewFilterOptions()
	filterOpts.MinStatusCode = 200
	filterOpts.MaxStatusCode = 299
	filterOpts.ServerContains = "nginx"
	filterOpts.HeaderKeyMustExist = []string{"Strict-Transport-Security"}
	filterOpts.SSLMustBeValid = true
	
	if gowebspy.ApplyFilter(info, filterOpts) {
		fmt.Println("Website matches all filter criteria!")
	} else {
		fmt.Println("Website doesn't match filter criteria.")
	}
}
```

### Advanced Security Analysis Example

```go
package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strings"
	"time"

	"github.com/ArjunSharda/gowebspy/pkg/gowebspy"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: websecuritycheck <domain>")
		os.Exit(1)
	}

	domain := os.Args[1]
	info, err := gowebspy.GetWebsiteInfo(domain)
	if err != nil {
		log.Fatalf("Error getting website info: %v", err)
	}

	report := generateSecurityReport(info)

	// Output as JSON
	jsonData, err := json.MarshalIndent(report, "", "  ")
	if err != nil {
		log.Fatalf("Error marshalling JSON: %v", err)
	}
	fmt.Println(string(jsonData))
}

type SecurityReport struct {
	Domain           string    `json:"domain"`
	ScanTime         time.Time `json:"scan_time"`
	SecurityScore    int       `json:"security_score"`
	IPv6Support      bool      `json:"ipv6_support"`
	Findings         []Finding `json:"findings"`
	RecommendedFixes []string  `json:"recommended_fixes"`
}

type Finding struct {
	Type        string `json:"type"`
	Description string `json:"description"`
	Severity    string `json:"severity"` // high, medium, low
}

func generateSecurityReport(info *gowebspy.WebsiteInfo) SecurityReport {
	report := SecurityReport{
		Domain:   extractDomain(info.URL),
		ScanTime: time.Now(),
	}

	// Check for IPv6 support
	hasIPv6 := false
	for _, ip := range info.IP {
		if strings.Contains(ip, ":") {
			hasIPv6 = true
			break
		}
	}
	report.IPv6Support = hasIPv6

	// Security score starts at 100 and gets reduced based on issues
	score := 100

	// Check for HTTPS
	if !strings.HasPrefix(info.URL, "https://") {
		report.Findings = append(report.Findings, Finding{
			Type:        "no_https",
			Description: "Website does not use HTTPS",
			Severity:    "high",
		})
		report.RecommendedFixes = append(report.RecommendedFixes, "Enable HTTPS")
		score -= 30
	}

	// Check SSL certificate
	if info.SSLInfo != nil {
		// Check if certificate is valid
		if !info.SSLInfo.Valid {
			report.Findings = append(report.Findings, Finding{
				Type:        "invalid_ssl",
				Description: "SSL certificate is invalid",
				Severity:    "high",
			})
			report.RecommendedFixes = append(report.RecommendedFixes, "Install a valid SSL certificate")
			score -= 25
		}

		// Check if certificate expires soon
		daysLeft := int(time.Until(info.SSLInfo.Expiry).Hours() / 24)
		if daysLeft < 30 {
			report.Findings = append(report.Findings, Finding{
				Type:        "expiring_ssl",
				Description: fmt.Sprintf("SSL certificate expires in %d days", daysLeft),
				Severity:    "medium",
			})
			report.RecommendedFixes = append(report.RecommendedFixes, "Renew SSL certificate")
			score -= 15
		}
	}

	// Check headers
	if info.Headers.Get("Strict-Transport-Security") == "" {
		report.Findings = append(report.Findings, Finding{
			Type:        "missing_hsts",
			Description: "HSTS header is missing",
			Severity:    "medium",
		})
		report.RecommendedFixes = append(report.RecommendedFixes, "Implement HTTP Strict Transport Security")
		score -= 10
	}

	if info.Headers.Get("Content-Security-Policy") == "" {
		report.Findings = append(report.Findings, Finding{
			Type:        "missing_csp",
			Description: "Content-Security-Policy header is missing",
			Severity:    "medium",
		})
		report.RecommendedFixes = append(report.RecommendedFixes, "Implement Content Security Policy")
		score -= 10
	}

	if info.Headers.Get("X-Content-Type-Options") != "nosniff" {
		report.Findings = append(report.Findings, Finding{
			Type:        "missing_xcontenttype",
			Description: "X-Content-Type-Options: nosniff header is missing",
			Severity:    "low",
		})
		report.RecommendedFixes = append(report.RecommendedFixes, "Add X-Content-Type-Options: nosniff header")
		score -= 5
	}

	// Check IPv6 support
	if !hasIPv6 {
		report.Findings = append(report.Findings, Finding{
			Type:        "no_ipv6",
			Description: "Website does not support IPv6",
			Severity:    "low",
		})
		report.RecommendedFixes = append(report.RecommendedFixes, "Enable IPv6 support")
		score -= 5
	}

	// Ensure score doesn't go below 0
	if score < 0 {
		score = 0
	}

	report.SecurityScore = score

	return report
}

func extractDomain(urlStr string) string {
	urlStr = strings.TrimPrefix(urlStr, "http://")
	urlStr = strings.TrimPrefix(urlStr, "https://")
	return strings.Split(strings.Split(urlStr, ":")[0], "/")[0]
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [PuerkitoBio/goquery](https://github.com/PuerkitoBio/goquery) for HTML parsing
- [likexian/whois](https://github.com/likexian/whois) for WHOIS data
- [likexian/whois-parser](https://github.com/likexian/whois-parser) for WHOIS parsing
- [spf13/cobra](https://github.com/spf13/cobra) for CLI commands
- [fatih/color](https://github.com/fatih/color) for colorized output

## 🔮 Future Plans

- Content analysis and screenshot capture
- Extended HTTP security checks
- Custom scripting/plugins support
- Web interface
- Batch processing and scanning capabilities
- Export to various formats (CSV, PDF, HTML)

---

Made with ❤️ by [ArjunSharda](https://github.com/ArjunSharda)
<hr>
<h6 align="center">© Arjun Sharda 2025-present
<br>
All Rights Reserved</h6>
