/*
Copyright © 2025 NAME HERE <EMAIL ADDRESS>
*/
package cmd

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"github.com/spf13/cobra"
)

var (
	editMessage string
	editFile    string
	editTags    []string
)

// editCmd represents the edit command
var editCmd = &cobra.Command{
	Use:   "edit",
	Short: "Edit an existing note by ID",
	Long: `Edit an existing note in the current project.
	
You must supply the note ID (first 8 chars or full). 
Provide any of --message, --file, or --tags to update just those fields.`,
	Args: cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		idToEdit := args[0]

		root, err := os.Getwd()
		if err != nil {
			fmt.Println("Error getting current directory:", err)
			return
		}

		notesPath := filepath.Join(root, ".notes", "notes.json")
		if _, err := os.Stat(notesPath); os.IsNotExist(err) {
			fmt.Println("No notes found in current project")
			return
		}

		data, err := os.ReadFile(notesPath)
		if err != nil {
			fmt.Println("Error reading notes file:", err)
			return
		}

		var notes []Note
		if err := json.Unmarshal(data, &notes); err != nil {
			fmt.Println("Error parsing notes:", err)
			return
		}

		edited := false
		for i, n := range notes {
			short := n.ID
			if len(short) > 8 {
				short = short[:8]
			}

			if short == idToEdit || n.ID == idToEdit {
				if editMessage != "" {
					notes[i].Message = editMessage
				}
				if cmd.Flags().Changed("file") {
					if editFile == "" {
						notes[i].File = ""
					} else {
						if rel, err := filepath.Rel(root, editFile); err == nil {
							notes[i].File = rel
						} else {
							notes[i].File = editFile
						}
					}
				}

				if cmd.Flags().Changed("tags") {
					notes[i].Tags = editTags
				}
				notes[i].CreatedAt = n.CreatedAt // n.CreatedAt is the original createdAt. We don't want to change it.
				edited = true
				break
			}
		}

		if !edited {
			fmt.Printf("No note found with ID %s\n", idToEdit)
			return
		}

		out, err := json.MarshalIndent(notes, "", "  ")
		if err != nil {
			fmt.Println("Error marshalling notes:", err)
			return
		}

		if err := os.WriteFile(notesPath, out, 0644); err != nil {
			fmt.Println("Error writing notes:", err)
			return
		}

		fmt.Printf("Note %s updated successfully\n", idToEdit)
	},
}

func init() {
	rootCmd.AddCommand(editCmd)

	editCmd.Flags().StringVarP(&editMessage, "message", "m", "", "Update note message")
	editCmd.Flags().StringVarP(&editFile, "file", "f", "", "New file to associate (optional)")
	editCmd.Flags().StringSliceVarP(&editTags, "tags", "t", []string{}, "New comma-separated tags (optional)")

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	// editCmd.PersistentFlags().String("foo", "", "A help for foo")

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// editCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
