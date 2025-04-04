/*
Copyright © 2025 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"os"

	"github.com/spf13/cobra"
)

// rootCmd represents the base command when called without any subcommands
var rootCmd = &cobra.Command{
	Use:   "asnitch",
	Short: "Wanted to lookup your favourite company's ASN or IP addresses? Look no further!",
	Long: `ASNitch is a CLI tool that allows you to lookup ASN and IP addresses with the help of the BGP.Tools API and Hurricane Electric's route server.
	
	Usage:
	./<binary> whois --asn asn[,asn2,asn3,...]
	./<binary> whois --ip ip[,ip2,ip3,...]`,
	// Uncomment the following line if your bare application
	// has an action associated with it:
	// Run: func(cmd *cobra.Command, args []string) { },
}

// Execute adds all child commands to the root command and sets flags appropriately.
// This is called by main.main(). It only needs to happen once to the rootCmd.
func Execute() {
	err := rootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}

	os.Exit(0)
}

func init() {
	// Here you will define your flags and configuration settings.
	// Cobra supports persistent flags, which, if defined here,
	// will be global for your application.

	whoisCmd.PersistentFlags().BoolP("json", "j", false, "Return the results in JSON format")
	// rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default is $HOME/.asnitch.yaml)")

	// Cobra also supports local flags, which will only run
	// when this action is called directly.
	rootCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
