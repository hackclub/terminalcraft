package cmd

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io"
	"net"
	"net/http"
	"os"
	"regexp"
	"strings"
	"time"

	"github.com/spf13/cobra"
)

// subnetsCmd represents the subnets command
var subnetsCmd = &cobra.Command{
	Use:   "subnets",
	Short: "Returns all of the subnets that belong to the given ASN",
	Long: `Returns all of the subnets that belong to the given ASN
	Usage:
	./<binary> subnets --asn asn`,
	Run: func(cmd *cobra.Command, args []string) {
		// remove as as a prefix
		asns := strings.Split(strings.ReplaceAll(cmd.Flag("asn").Value.String(), "as", ""), ",")
		fmt.Print("ASNs: ", asns, "\n")

		if cmd.Flag("use-he").Changed {
			// HE route server telnet client
			timeout := 30 * time.Second
			conn, err := net.DialTimeout("tcp", "route-server.he.net:23", timeout)
			if err != nil {
				fmt.Println("Error connecting:", err)
				return
			}
			defer conn.Close()

			fmt.Println("Connected successfully, starting to read output...")

			conn.SetDeadline(time.Now().Add(timeout))

			for {
				output := readOutput(conn)

				switch {
				case strings.Contains(output, "Password:"):
					// Send password if "Password:" prompt appears
					fmt.Println("Password prompt detected, sending password...")
					_, err := conn.Write([]byte("rviews\n"))
					if err != nil {
						fmt.Println("Error sending password:", err)
					}

				case strings.Contains(output, "route-server>"):
					// Once the prompt "route-server>" appears, start fetching networks for each ASN
					for _, asn := range asns {
						cmd := fmt.Sprintf("show ip bgp regexp %s\n", asn)
						fmt.Println("Sending command:", cmd)
						_, err := conn.Write([]byte(cmd))
						if err != nil {
							fmt.Printf("Error sending command for ASN %s: %v\n", asn, err)
							continue
						}

						output := readOutput(conn)
						lines := strings.Split(output, "\n")
						re := regexp.MustCompile(`^(\d{1,3}\.){3}\d{1,3}/\d{1,2}$`)
						for _, line := range lines {
							if strings.Contains(line, "Network") || !strings.HasPrefix(line, "* i") {
								continue
							}
							parts := strings.Fields(line)
							if len(parts) > 1 {
								subnet := parts[1]
								subnet = strings.TrimPrefix(subnet, "i")
								match, _ := regexp.MatchString(re.String(), subnet)
								if match {
									fmt.Println(subnet)
								}
							}
						}

						return
					}
				}

				// end of output and close connection
				if strings.Contains(output, "route-server>") {
					fmt.Println("Closing connection...")
					conn.Close()
					return
				}
			}
		} else {
			// BGP.tools API client instead of telnet oh god please save me
			fmt.Println("Using BGP.Tools API")
			var body []byte

			// check if the file exists and if it's older than 30 minutes
			fileInfo, err := os.Stat("table.jsonl")
			if err == nil {
				if time.Since(fileInfo.ModTime()) > 30*time.Minute {
					fmt.Println("Cache is older than 30 minutes, fetching new data...")
					httpReq, err := http.NewRequest("GET", "https://bgp.tools/table.jsonl", nil)
					if err != nil {
						fmt.Println("Error creating request:", err)
						return
					}

					httpReq.Header.Set("Accept", "application/json")
					httpReq.Header.Set("Content-Type", "application/json")
					httpReq.Header.Set("User-Agent", "ASNitch CLI - adriant@ingot.gg")

					httpClient := &http.Client{}
					resp, err := httpClient.Do(httpReq)
					if err != nil {
						fmt.Println("Error sending request:", err)
						return
					}
					defer resp.Body.Close()

					// Check if the response status is OK
					if resp.StatusCode != http.StatusOK {
						fmt.Println("Error: Received non-OK HTTP status:", resp.StatusCode)
						return
					}

					body, err = io.ReadAll(resp.Body)
					if err != nil {
						fmt.Println("Error reading response body:", err)
						return
					}

					// cache the body for 30 minutes so that i dont get ratelimited AGAIN
					// i'm not sure if this is the best idea but whatever :dies:
					os.WriteFile("table.jsonl", body, 0600)
				} else {
					fmt.Println("Cache is still fresh, using cached data...")
					// read the file and parse it
					body, err = os.ReadFile("table.jsonl")
					if err != nil {
						fmt.Println("Error reading cache:", err)
						return
					}
				}
			} else {
				httpReq, err := http.NewRequest("GET", "https://bgp.tools/table.jsonl", nil)
					if err != nil {
						fmt.Println("Error creating request:", err)
						return
					}

					httpReq.Header.Set("Accept", "application/json")
					httpReq.Header.Set("Content-Type", "application/json")
					httpReq.Header.Set("User-Agent", "ASNitch CLI - adriant@ingot.gg")

					httpClient := &http.Client{}
					resp, err := httpClient.Do(httpReq)
					if err != nil {
						fmt.Println("Error sending request:", err)
						return
					}
					defer resp.Body.Close()

					// Check if the response status is OK
					if resp.StatusCode != http.StatusOK {
						fmt.Println("Error: Received non-OK HTTP status:", resp.StatusCode)
						return
					}

					body, err = io.ReadAll(resp.Body)
					if err != nil {
						fmt.Println("Error reading response body:", err)
						return
					}

					// cache the body for 30 minutes so that i dont get ratelimited AGAIN
					// i'm not sure if this is the best idea but whatever :dies:
					os.WriteFile("table.jsonl", body, 0600)
			}

			subnetMap := make(map[string][]string)
			scanner := bufio.NewScanner(strings.NewReader(string(body)))
			for scanner.Scan() {
				var subnet map[string]interface{}
				if err := json.Unmarshal(scanner.Bytes(), &subnet); err != nil {
					fmt.Println("Error parsing JSONL line:", err)
					continue
				}
				asn := fmt.Sprintf("%v", subnet["ASN"])
				subnetMap[asn] = append(subnetMap[asn], fmt.Sprintf("%v", subnet["CIDR"]))
			}
			if err := scanner.Err(); err != nil {
				fmt.Println("Error reading input:", err)
				return
			}
			for _, asn := range asns {
				fmt.Printf("Subnets for ASN %s: %v\n", asn, strings.Join(subnetMap[asn], ", "))
			}
		}

	},
}

func readOutput(conn net.Conn) string {
	buffer := make([]byte, 4096)
	var result strings.Builder

	for {
		n, err := conn.Read(buffer)
		if err != nil {
			if err == io.EOF {
				break
			}
			fmt.Println("Error reading data:", err)
			break
		}
		if n > 0 {
			cleanData := filterNonPrintable(buffer[:n])
			// fmt.Print(cleanData) // uncomment if you want to see all of the telnet output
			result.WriteString(cleanData)
		}
		if strings.Contains(result.String(), "\n") {
			break
		}
	}
	return result.String()
}

// ChatGPT helped me with this, I still don't get how the telnet libraries also break but just using this + net.Dial works
func filterNonPrintable(data []byte) string {
	var cleanData []rune
	for _, b := range data {
		if b == 0xFF || b == 0xFE || b == 0xFD || b == 0xFC || b == 0xFB {
			continue
		}
		if b >= 32 && b <= 126 {
			if b != '"' {
				cleanData = append(cleanData, rune(b))
			}
		} else if b == '\n' || b == '\r' {
			cleanData = append(cleanData, rune(b))
		}
	}
	return string(cleanData)
}

func init() {
	rootCmd.AddCommand(subnetsCmd)

	subnetsCmd.Flags().StringP("asn", "a", "", "Comma separated list of ASNs to lookup")
	subnetsCmd.MarkFlagRequired("asn")

	// this is if you have a small asn and just want to use whatever i spent like 6 hours working on :sob:
	subnetsCmd.Flags().BoolP("use-he", "u", false, "Use Hurricane Electric's route server to fetch subnets")
	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// subnetsCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// subnetsCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
