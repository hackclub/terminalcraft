package cmd

import (
	"encoding/json"
	"fmt"
	"os"
	"time"

	"github.com/charmbracelet/lipgloss"
	"github.com/spf13/cobra"
)

var listCmd = &cobra.Command{
	Use:   "list",
	Short: "List all saved snippets",
	Run: func(cmd *cobra.Command, args []string) {
		snippets := loadSnippets()
		if len(snippets) == 0 {
			fmt.Println("No snippets found.")
			return
		}

		for _, s := range snippets {
			printSnippet(s.ID, s.Title, s.Code, s.CreatedAt)
		}
	},
}

func init() {
	rootCmd.AddCommand(listCmd)
}

func loadSnippets() []Snippet {
	home, _ := os.UserHomeDir()
	file := home + "/.hackabin/snippets.json"

	data, err := os.ReadFile(file)
	if err != nil {
		return []Snippet{}
	}

	var snippets []Snippet
	_ = json.Unmarshal(data, &snippets)
	return snippets
}

// styles ahh
var titleStyle = lipgloss.NewStyle().
	Bold(true).
	Foreground(lipgloss.Color("#7D56F4"))

var metaStyle = lipgloss.NewStyle().
	Foreground(lipgloss.Color("#888"))

var codeStyle = lipgloss.NewStyle().
	Foreground(lipgloss.Color("#00FF9F")).
	Border(lipgloss.NormalBorder()).
	Padding(0, 1)

func printSnippet(id, title, code, date string) {
	parsedTime, _ := time.Parse(time.RFC3339, date)
	dateStr := parsedTime.Format("Jan 2, 2006 3:04PM")

	fmt.Println(titleStyle.Render(title))
	fmt.Println(metaStyle.Render(id + " • " + dateStr))
	fmt.Println(codeStyle.Render(code))
}
