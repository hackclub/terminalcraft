package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

// addCmd represents the add command
var addCmd = &cobra.Command{
	Use:   "add",
	Short: "Add a new note",
	Long:  `Adds a new note to your project. Save a new note by providing a message after the add command surrounded by quotes.`,
	Args:  cobra.ExactArgs(1),
	Run: func(cmd *cobra.Command, args []string) {
		if len(args) == 0 {
			fmt.Println("Please provide a note message")
			return
		}

		note := args[0]
		err := SaveNote(note, noteFile, noteLine, noteTags)
		fmt.Println("Note Saved Successfully")
		if err != nil {
			fmt.Println("Error saving note: ", err)
		}
	},
}

var noteFile string
var noteLine int
var noteTags []string

func init() {
	rootCmd.AddCommand(addCmd)

	addCmd.Flags().StringVarP(&noteFile, "file", "f", "", "Optional file to associate with the note (e.g. --file cmd/root.go)")
	addCmd.Flags().IntVarP(&noteLine, "line", "l", 0, "Optional line number in the file to associate with the note (e.g. --line 10)")
	addCmd.Flags().StringSliceVarP(&noteTags, "tags", "t", []string{}, "Optional comma-separated tags for the note (e.g. --tags bug,urgent)")
}
