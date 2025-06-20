package cmd

import (
	"fmt"
	"strings"

	"github.com/spf13/cobra"
)

var searchCmd = &cobra.Command{
	Use:   "search <title>",
	Short: "Search snippets by title",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		titleQuery := strings.ToLower(args[0])
		snippets := loadSnippets()

		if len(snippets) == 0 {
			ascii := loadASCIISticker("stickers/orphmoji_scared.txt")
			fmt.Println("❌ No snippets found.")
			fmt.Println(ascii)
			return
		}

		found := false
		for _, snip := range snippets {
			if strings.Contains(strings.ToLower(snip.Title), titleQuery) {
				printSnippet(snip.ID, snip.Title, snip.Code, snip.CreatedAt)
				fmt.Println()
				found = true
			}
		}

		if !found {
			ascii := loadASCIISticker("stickers/orphmoji_scared.txt")
			fmt.Println("❌ No matching snippets found.")
			fmt.Println(ascii)
		}
	},
}

func init() {
	rootCmd.AddCommand(searchCmd)
}
