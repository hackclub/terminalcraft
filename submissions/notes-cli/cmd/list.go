package cmd

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/fatih/color"
	"github.com/spf13/cobra"
)

var listFile string
var listTag string

// listCmd represents the list command
var listCmd = &cobra.Command{
	Use:   "list",
	Short: "List your saved notes",
	Long:  `Lists all notes saved for the current project.`,
	Run: func(cmd *cobra.Command, args []string) {
		root, err := os.Getwd()
		if err != nil {
			fmt.Println("Error getting root directory: ", err)
			return
		}

		notesPath := filepath.Join(root, ".notes", "notes.json")
		if _, err := os.Stat(notesPath); os.IsNotExist(err) {
			fmt.Println("No notes found")
			return
		}

		data, err := os.ReadFile(notesPath)
		if err != nil {
			fmt.Println("Error reading notes file: ", err)
			return
		}

		var notes []Note
		if err := json.Unmarshal(data, &notes); err != nil {
			fmt.Println("Error unmarshalling notes: ", err)
			return
		}

		if len(notes) == 0 {
			fmt.Println("No notes found")
			return
		}

		for _, n := range notes {

			if listFile != "" {
				noteBase := filepath.Base(n.File)
				inputBase := filepath.Base(listFile)

				if n.File != listFile && noteBase != inputBase {
					continue
				}
			}

			if listTag != "" {
				found := false
				for _, tag := range n.Tags {
					if tag == listTag {
						found = true
						break
					}
				}
				if !found {
					continue
				}
			}

			id := color.New(color.FgHiCyan).Sprint(n.ID[:8])
			timestamp := color.New(color.FgHiBlack).Sprint(n.CreatedAt.Format(time.RFC822)) // 30 May 25 12:00 PM
			message := color.New(color.FgWhite).Sprint(n.Message)

			location := ""
			if n.File != "" {
				location = fmt.Sprintf(" → %s", n.File)
				if n.Line > 0 {
					location += fmt.Sprintf(":%d", n.Line)
				}
			}

			fmt.Printf("[%s] %s%s\n", id, message, location)
			if len(n.Tags) > 0 {
				tagStr := color.New(color.FgGreen).SprintFunc()
				coloredTags := make([]string, len(n.Tags))
				for i, tag := range n.Tags {
					coloredTags[i] = tagStr(tag)
				}
				fmt.Printf("    Tags: %s\n", strings.Join(coloredTags, ", "))
			}
			fmt.Printf("    %s\n\n", timestamp)
		}
	},
}

func init() {
	rootCmd.AddCommand(listCmd)

	listCmd.Flags().StringVarP(&listFile, "file", "f", "", "Optional file to filter notes by")
	listCmd.Flags().StringVarP(&listTag, "tag", "t", "", "Optional tag to filter notes by")
}
