package main

import (
	"bufio"
	"fmt"
	"os"
	"os/exec"
	"strings"

	"github.com/awesomebrownies/ssu/lib/configuration"
	"github.com/awesomebrownies/ssu/lib/display"

	"github.com/spf13/cobra"
)

const (
	baseURL  = "https://raw.githubusercontent.com/awesomebrownies/ssu/main/"
	filePath = "/Documents/ssu/"
)

var HomeDir string

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

		// if strings.HasPrefix(resultStr, "v:") {
		// 	err := exec.Command("nano", resultStr)
		// 	if err != nil {
		// 		fmt.Printf("%s\n", err)
		// 	}
		// 	selectMenu(directory)
		// 	return
		// }

		//action
		view := strings.HasPrefix(resultStr, "v:")
		if strings.HasPrefix(resultStr, "▶ ") || view {
			actionName := strings.TrimPrefix(resultStr, "v:")
			actionName = strings.TrimPrefix(actionName, "▶ ")

			for _, action := range directory.Actions {
				if action.Name == actionName {
					if view {
						cmd := exec.Command("nano", HomeDir+filePath+action.ScriptPath)

						cmd.Stdin = os.Stdin
						cmd.Stdout = os.Stdout
						cmd.Stderr = os.Stderr

						err := cmd.Run()
						if err != nil {
							fmt.Printf("%s\n", err)
						}
						selectMenu(directory)
						return
					}

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
	cmd := exec.Command("/bin/bash", HomeDir+filePath+file)
	cmd.Stdout = os.Stdout
	cmd.Stdin = os.Stdin
	cmd.Stderr = os.Stderr

	err := cmd.Run()
	if err != nil {
		fmt.Printf("%s\n", err)
	}
}

func configFolder() {
	files := []string{"scripts/dis_guest_remote.sh", "scripts/dis_root.sh", "scripts/file_perms.sh", "scripts/ssh.sh", "scripts/ufw_sysctl.sh", "directories.yaml"}

	err := os.MkdirAll(HomeDir+filePath+"/scripts", 0755)
	if err != nil {
		fmt.Printf("%s\n", err)
	}
	answer := prompt("Download default shell scripts? (Y/n)")
	if !strings.HasPrefix(strings.ToLower(answer), "n") {
		for _, file := range files {
			if err := configuration.DownloadFile(baseURL+file, HomeDir+filePath+file); err != nil {
				fmt.Println("Failed: ", file, err)
			} else {
				fmt.Println("Downloaded: ", file)
			}
		}
	}
}

func prompt(prompt string) string {
	var s string
	r := bufio.NewReader(os.Stdin)
	for {
		fmt.Fprint(os.Stderr, prompt+" ")
		s, _ = r.ReadString('\n')
		if s != "" {
			break
		}
	}
	return strings.TrimSpace(s)
}

func dirExists(path string) bool {
	info, err := os.Stat(path)
	return err == nil && info.IsDir() // Returns true only if it's a directory
}

func main() {
	rootCmd := &cobra.Command{
		Use:   "ssu",
		Short: "Performs a system security overview",
		Long:  "A CLI tool for running system security checks on your computer",
		Run: func(cmd *cobra.Command, args []string) {
			homeDir, err := os.UserHomeDir()
			if err != nil {
				fmt.Printf("%s\n", err)
			}
			HomeDir = homeDir
			if !dirExists(homeDir + filePath) {
				configFolder()
			}

			configuration.LoadDirectories()
			selectMenu(&configuration.Root)
		},
	}

	if err := rootCmd.Execute(); err != nil {
		fmt.Println(err)
	}
}
