package cmd

import (
	"fmt"
	"os"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/spf13/cobra"
)

// tuiCmd represents the tui command
var tuiCmd = &cobra.Command{
	Use:   "tui",
	Short: "Shows a TUI for your saved notes for your current project",
	Long:  `Show your current project's notes in a nice TUI.`,
	RunE: func(cmd *cobra.Command, args []string) error {
		m, err := initialModel()
		if err != nil {
			return fmt.Errorf("failed to initialize TUI: %w", err)
		}

		p := tea.NewProgram(m)
		if err := p.Start(); err != nil {
			fmt.Fprintf(os.Stderr, "Error running TUI: %v\n", err)
			return err
		}
		return nil
	},
}

func init() {
	rootCmd.AddCommand(tuiCmd)
}
