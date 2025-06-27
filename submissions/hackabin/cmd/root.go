package cmd

import (
	"fmt"
	"os"

	"github.com/charmbracelet/lipgloss"
	"github.com/spf13/cobra"
)

var ascii = ` _                _         _     _       
| |__   __ _  ___| | ____ _| |__ (_)_ __  
| '_ \ / _` + "`" + ` |/ __| |/ / _` + "`" + ` | '_ \| | '_ \ 
| | | | (_| | (__|   < (_| | |_) | | | | |
|_| |_|\__,_|\___|_|\_\__,_|_.__/|_|_| |_|
`

var rootCmd = &cobra.Command{
	Use:   "hackabin",
	Short: "CLI app to save code snippets",
	Long: `Hackabin is a CLI tool to save, search, and manage your code snippets with context.
Use "hackabin add" to save a new snippet or "hackabin search" to find one.`,
	Run: func(cmd *cobra.Command, args []string) {
		// show help if no subcommand is provided
		fmt.Println(lipgloss.NewStyle().Bold(true).SetString(ascii).Foreground(lipgloss.Color("#a633d6")))
		cmd.Help()
	},
}

func Execute() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Println("Error:", err)
		os.Exit(1)
	}
}
