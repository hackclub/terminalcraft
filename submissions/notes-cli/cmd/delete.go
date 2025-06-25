package cmd

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"

	"github.com/spf13/cobra"
)

var forceDelete bool
var deleteTag string

// deleteCmd represents the delete command
var deleteCmd = &cobra.Command{
	Use:   "delete",
	Short: "Delete a note by ID",
	Long:  `Deletes a note from your project.`,
	Run: func(cmd *cobra.Command, args []string) {
		root, err := os.Getwd()
		if err != nil {
			fmt.Println("Error getting working directory:", err)
			return
		}

		notesPath := filepath.Join(root, ".notes", "notes.json")
		if _, err := os.Stat(notesPath); os.IsNotExist(err) {
			fmt.Println("No notes file found.")
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

		if deleteTag != "" {
			// Delete by tag
			var updatedNotes []Note
			deletedCount := 0

			for _, note := range notes {
				hasTag := false
				for _, tag := range note.Tags {
					if tag == deleteTag {
						hasTag = true
						break
					}
				}

				if hasTag {
					if !forceDelete {
						fmt.Printf("Delete note \"%s\" (file: %s)? (y/N): ", note.Message, note.File)
						var input string
						fmt.Scanln(&input)
						if input != "y" && input != "Y" {
							updatedNotes = append(updatedNotes, note)
							continue
						}
					}
					deletedCount++
					continue
				}

				updatedNotes = append(updatedNotes, note)
			}

			if deletedCount == 0 {
				fmt.Printf("No notes found with tag \"%s\"\n", deleteTag)
				return
			}

			updatedData, err := json.MarshalIndent(updatedNotes, "", "  ")
			if err != nil {
				fmt.Println("Error saving updated notes:", err)
				return
			}

			err = os.WriteFile(notesPath, updatedData, 0644)
			if err != nil {
				fmt.Println("Error writing updated notes:", err)
				return
			}

			fmt.Printf("Deleted %d note(s) with tag \"%s\".\n", deletedCount, deleteTag)
			return
		}

		// Default: Delete by ID
		if len(args) == 0 {
			fmt.Println("Please provide a note ID or use --tag to delete all notes with a given tag")
			return
		}

		idToDelete := args[0]
		var updatedNotes []Note
		deleted := false

		for _, note := range notes {
			if note.ID[:8] == idToDelete || note.ID == idToDelete {
				if !forceDelete {
					fmt.Printf("Are you sure you want to delete note \"%s\"? (y/N): ", note.Message)
					var input string
					fmt.Scanln(&input)
					if input != "y" && input != "Y" {
						fmt.Println("Aborted.")
						return
					}
				}
				deleted = true
				continue
			}
			updatedNotes = append(updatedNotes, note)
		}

		if !deleted {
			fmt.Printf("No note found with ID %s\n", idToDelete)
			return
		}

		updatedData, err := json.MarshalIndent(updatedNotes, "", "  ")
		if err != nil {
			fmt.Println("Error saving updated notes:", err)
			return
		}

		err = os.WriteFile(notesPath, updatedData, 0644)
		if err != nil {
			fmt.Println("Error writing updated notes:", err)
			return
		}

		fmt.Printf("Note with ID %s deleted successfully.\n", idToDelete)
	},
}

func init() {
	rootCmd.AddCommand(deleteCmd)

	deleteCmd.Flags().StringVarP(&deleteTag, "tag", "t", "", "Delete all notes with a given tag")
	deleteCmd.Flags().BoolVarP(&forceDelete, "yes", "y", false, "Delete without confirmation")
}
