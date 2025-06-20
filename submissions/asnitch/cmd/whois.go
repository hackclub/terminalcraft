package cmd

import (
	"encoding/json"
	"fmt"
	"strings"

	"github.com/spf13/cobra"
	"ssmidge.xyz/asnitch/util/whois"
)

var whoisCmd = &cobra.Command{
	Use:   "whois",
	Short: "Returns information on who owns the ASN or IP address",
	Long: `Returns information on who owns the ASN or IP address
	
	Usage:
	./<binary> whois --asn asn[,asn2,asn3,...]
	./<binary> whois --ip ip[,ip2,ip3,...]`,
	Run: func(cmd *cobra.Command, args []string) {

		asn, _ := cmd.Flags().GetString("asn")
		asns := strings.Split(asn, ",")
		ip, _ := cmd.Flags().GetString("ip")
		ips := strings.Split(ip, ",")

		if asn == "" && ip == "" {
			cmd.Usage()
		}

		jsonOutput, err := cmd.Flags().GetBool("json")
		if err != nil {
			fmt.Printf("Error getting json flag: %v\n", err)
			return
		}
		if jsonOutput {
			if ip == "" {
				fmt.Println("No IPs provided")
			} else {
				for _, ip := range ips {
					response, err := whois.Whois(strings.TrimSpace(ip))
					if err != nil {
						fmt.Printf("Error querying %s: %v\n", ip, err)
						continue
					}

					jsonResult, err := json.MarshalIndent(whois.ParseWhoisResult(response), "", "  ")
					if err != nil {
						fmt.Printf("Error marshalling JSON: %v\n", err)
						continue
					}
					if string(jsonResult) != "null" {
						fmt.Println(string(jsonResult))
					}
				}
			}
		} else {
			fmt.Print("ASN Information:\n")
			if asn != "" {
				var firstResponse bool = true

				for _, asn := range asns {
					response, err := whois.Whois(strings.TrimSpace(asn))
					if err != nil {
						fmt.Printf("Error querying %s: %v\n", asn, err)
						continue
					}

					lines := strings.Split(response, "\n")

					if firstResponse {
						fmt.Print(response)
						firstResponse = false
					} else {
						// Skip the first line, assuming it's the header
						fmt.Print(strings.Join(lines[1:], "\n"))
					}
				}
			}

			fmt.Print("\n\nIP Information:\n")
			if ip != "" {
				var firstResponse bool = true

				for _, ip := range ips {
					response, err := whois.Whois(strings.TrimSpace(ip))
					if err != nil {
						fmt.Printf("Error querying %s: %v\n", ip, err)
						continue
					}

					lines := strings.Split(response, "\n")

					if firstResponse {
						fmt.Println()
						fmt.Print(response)
						firstResponse = false
					} else {
						// Skip the first line, assuming it's the header
						fmt.Print(strings.Join(lines[1:], "\n"))
					}
				}
			}
		}
	},
}

func init() {
	rootCmd.AddCommand(whoisCmd)

	whoisCmd.Flags().StringP("asn", "a", "", "Comma separated list of ASNs to lookup")
	whoisCmd.Flags().StringP("ip", "i", "", "Comma separated list of IPs to lookup")

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// whoisCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// whoisCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
