package cmd

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"

	"hackabin/pocketbasehelper"

	"github.com/charmbracelet/lipgloss"
	"github.com/spf13/cobra"
)

const orphmoji_scared = `
            ....:::. .              
          .:+;......;;.;:..         
      ...:;:....:+;;..::..;+:..     
    .:+;;..::...;:..;:::......;+:. .
  .;;..:;...:..;;...;:.;..........+.
.+;....;:;;;....::;;:...:;+:......+.
.+:...:;...............  .+......;: 
.:;...;+;:.......:;...;..+:.....+:  
  ;;...:;..::+::......+.+......+.   
  .;;....;:..+........++.....;;.    
   .:+.....+:;.........:....+.      
    ..;;....:.............;.        
      ..;:.................         
`

var globalFlag bool

var removeCmd = &cobra.Command{
	Use:   "remove <id>",
	Short: "Remove a snippet by ID (locally or globally)",
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		id := args[0]

		if globalFlag {
			pocketbasehelper.RemoveSnippet(id)
			return
		}

		snippets := loadSnippets()

		if len(snippets) == 0 {
			fmt.Println("❌ No snippets found.")
			fmt.Println(orphmoji_scared)
			return
		}

		index := -1
		for i, s := range snippets {
			if s.ID == id {
				index = i
				break
			}
		}

		if index == -1 {
			fmt.Println(lipgloss.NewStyle().SetString("Snippet not found.").Foreground(lipgloss.Color("#ec3750")).Italic(true).Bold(true))
			fmt.Println(orphmoji_scared)
			return
		}

		snippets = append(snippets[:index], snippets[index+1:]...)
		saveAllSnippets(snippets)

		fmt.Println(lipgloss.NewStyle().SetString("Snippet removed.").Foreground(lipgloss.Color("#ec3750")).Italic(true).Bold(true))
	},
}

func init() {
	removeCmd.Flags().BoolVarP(&globalFlag, "global", "g", false, "Remove snippet from PocketBase instead of locally")
	rootCmd.AddCommand(removeCmd)
}

func saveAllSnippets(snippets []Snippet) {
	home, _ := os.UserHomeDir()
	file := home + "/.hackabin/snippets.json"

	newData, _ := json.MarshalIndent(snippets, "", "  ")
	_ = os.WriteFile(file, newData, 0644)
}

func loadASCIISticker(path string) string {
	data, err := os.ReadFile(path)
	if err != nil {
		return ""
	}
	return strings.TrimSpace(string(data))
}
