package cmd

import (
	"encoding/json"
	"fmt"
	"hackabin/pocketbasehelper"
	"os"

	"github.com/spf13/cobra"
)

var uploadCmd = &cobra.Command{
	Use:   "upload <id>",
	Short: "Upload a snippet by ID to server",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		id := args[0]
		snippet := findSnippetByID(id)
		if snippet == nil {
			fmt.Println("❌ Snippet not found.")
			return
		}

		pocketbasehelper.UploadSnippet(*snippet)
	},
}

func init() {
	rootCmd.AddCommand(uploadCmd)
}

func findSnippetByID(id string) *pocketbasehelper.Snippet {
	home, _ := os.UserHomeDir()
	file := home + "/.hackabin/snippets.json"

	data, err := os.ReadFile(file)
	if err != nil {
		return nil
	}

	var snippets []pocketbasehelper.Snippet
	_ = json.Unmarshal(data, &snippets)

	for _, s := range snippets {
		if s.ID == id {
			return &s
		}
	}
	return nil
}
