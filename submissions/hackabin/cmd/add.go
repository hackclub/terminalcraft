package cmd

import (
	"encoding/json"
	"fmt"
	"os"
	"strings"
	"time"

	"github.com/charmbracelet/lipgloss"
	"github.com/spf13/cobra"
)

type Snippet struct {
	ID        string `json:"id"`
	Title     string `json:"title"`
	Code      string `json:"code"`
	CreatedAt string `json:"created_at"`
}

var addCmd = &cobra.Command{
	Use:   "add <title> <code|file>",
	Short: "Add a new code snippet (inline or from file)",
	Args:  cobra.ExactArgs(2),
	Run: func(cmd *cobra.Command, args []string) {
		title := strings.TrimSpace(args[0])
		codeInput := strings.TrimSpace(args[1])
		var code string

		if fileContent, err := os.ReadFile(codeInput); err == nil {
			// If it's a valid file path, use file content
			code = string(fileContent)
		} else {
			// Otherwise, treat it as inline code
			code = codeInput
		}

		var theID = fmt.Sprintf("%d", time.Now().UnixNano())

		snippet := Snippet{
			ID:        theID,
			Title:     title,
			Code:      code,
			CreatedAt: time.Now().Format(time.RFC3339),
		}

		saveSnippet(snippet)

		msg := lipgloss.NewStyle().
			Italic(true).
			Bold(true).
			Foreground(lipgloss.Color("#33d6a6")).
			SetString("Snippet saved!")

		codee := lipgloss.NewStyle().
			Border(lipgloss.NormalBorder()).
			SetString(code).Padding(0, 1)

		fmt.Println(msg)
		fmt.Println(theID)
		fmt.Println(codee)
	},
}

func init() {
	rootCmd.AddCommand(addCmd)
}

func saveSnippet(s Snippet) {
	home, _ := os.UserHomeDir()
	dir := home + "/.hackabin"
	file := dir + "/snippets.json"

	_ = os.MkdirAll(dir, os.ModePerm)

	var snippets []Snippet

	data, err := os.ReadFile(file)
	if err == nil {
		_ = json.Unmarshal(data, &snippets)
	}

	snippets = append(snippets, s)

	newData, _ := json.MarshalIndent(snippets, "", "  ")
	_ = os.WriteFile(file, newData, 0644)
}
