package main

import (
	"fmt"
	"os"
	"os/exec"
	"strings"

	"greeter/lib/configuration"
	"greeter/lib/display"

	"github.com/spf13/cobra"
)

func selectMenu(directory *configuration.Directory) {
	menu := display.NewMenu("Select an option", directory.Name)

	//back option if not root
	if directory.Parent != nil {
		menu.AddItem("../")
	}

	//display subdirectories
	for _, subsection := range directory.Subsections {
		menu.AddItem(subsection.Name)
	}
	//display any actions below
	for _, action := range directory.Actions {
		menu.AddItem("▶ " + action.Name)
	}

	result, err := menu.Display()
	if err != nil {
		fmt.Printf("%s\n", err)
		return
	}

	if resultStr, ok := result.(string); ok {

		if resultStr == "../" && directory.Parent != nil {
			selectMenu(directory.Parent)
			return
		}

		//action
		if strings.HasPrefix(resultStr, "▶ ") {
			actionName := strings.TrimPrefix(resultStr, "▶ ")

			for _, action := range directory.Actions {
				if action.Name == actionName {
					fmt.Printf("Executing: %s\n", action.Name)
					execBash(action.ScriptPath)
					selectMenu(directory)
					return
				}
			}
			//directory
		} else {
			for _, subsection := range directory.Subsections {
				if subsection.Name == resultStr {
					selectMenu(subsection)
					return
				}
			}
		}

		fmt.Println("Invalid selection")
		selectMenu(directory)
	}
}

func execBash(file string) {
	cmd := exec.Command("/bin/bash", "../../"+file)
	cmd.Stdout = os.Stdout
	cmd.Stdin = os.Stdin
	cmd.Stderr = os.Stderr

	err := cmd.Run()
	if err != nil {
		fmt.Printf("%s\n", err)
	}
}

func main() {
	rootCmd := &cobra.Command{
		Use:   "ssu",
		Short: "Performs a system security overview",
		Long:  "A CLI tool for running system security checks on your computer",
		Run: func(cmd *cobra.Command, args []string) {
			configuration.LoadDirectories()
			selectMenu(&configuration.Root)
		},
	}

	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
	}
}
