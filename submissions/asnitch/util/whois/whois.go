package whois

import (
	"fmt"
	"regexp"
	"strconv"
	"strings"

	"github.com/likexian/whois"
)

// IP or ASN
func Whois(what string) (string, error) {
	if isIPorASN(what) == N_A {
		return "", fmt.Errorf("invalid input: %s", what)
	}

	whoisServer := "whois.ripe.net"
	if whois.IsASN(what) {
		whoisServer = "bgp.tools"
	} else {
		whoisServer = "whois.ripe.net"
		// sources: ARIN-GRS,RIPE,AFRINIC-GRS,APNIC-GRS,LACNIC-GRS
		// GRS is the Global Resource Service, it converts all of the weird stuff like ARIN's NetHandle to inetnum, etc.
		what = fmt.Sprintf("-s ARIN-GRS,RIPE,AFRINIC-GRS,APNIC-GRS,LACNIC-GRS %s", what)
	}

	result, err := whois.Whois(what, whoisServer)
	if err != nil {
		return "", err
	}

	result = removeAppendedInformation(result)

	return result, nil
}

func removeAppendedInformation(input string) string {
	// all of the useless whois server comments/junk
	re := regexp.MustCompile(`(%.*)`)
	result := re.ReplaceAllString(input, "")

	// convert all the \r to \n for easy splitting in the cursed code that comes just after this
	result = strings.ReplaceAll(result, "\r\n", "\n")
	result = strings.ReplaceAll(result, "\r", "\n")

	lines := strings.Split(result, "\n")
	var cleanedLines []string
	previousLineEmpty := false

	// this is probably very innefficient for large whois results but it's not going to be used by automations so
	for _, line := range lines {
		trimmed := strings.TrimSpace(line)
		if trimmed == "" {
			if !previousLineEmpty {
				cleanedLines = append(cleanedLines, "")
				previousLineEmpty = true
			}
		} else {
			cleanedLines = append(cleanedLines, trimmed)
			previousLineEmpty = false
		}
	}

	return strings.Trim(strings.Join(cleanedLines, "\n"), "\n") + "\n"
}

func isIPorASN(str string) WhoIsRequestType {
	ipv4Regex := `^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}(\/([0-9]|[1-2][0-9]|3[0-2]))?$`
	ipv6Regex := `^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\/([0-9]|[1-9][0-9]|1[0-1][0-9]|12[0-8])$`
	asnRegex := `^(?:as)?(\d{1,4}|[1-9]\d{4,7})$`

	matchIPv4, _ := regexp.MatchString(ipv4Regex, str)
	matchIPv6, _ := regexp.MatchString(ipv6Regex, str)
	if matchIPv4 || matchIPv6 {
		return "IP"
	}

	// bgp.tools returns information about reserved asns so we just need to check if it's a valid asn inbetween the 16 and 32bit ranges
	normalizedStr := regexp.MustCompile(`(?i)^as`).ReplaceAllString(str, "")

	// convert the remaining part to an integer and check if it's a valid ASN
	asn, err := strconv.Atoi(normalizedStr)
	if err == nil && asn >= 1 && asn <= 4294967295 && regexp.MustCompile(asnRegex).MatchString(normalizedStr) {
		return "ASN"
	}

	return "N/A"
}

type WhoIsRequestType string

const (
	IP  WhoIsRequestType = "IP"
	ASN WhoIsRequestType = "ASN"
	N_A WhoIsRequestType = "N/A"
)
