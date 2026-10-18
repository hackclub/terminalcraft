package main

import (
	"fmt"
	"os"
	"rinogodson/DreamShell/ui"
//	"rinogodson/DreamShell/filehandler"
)

func main()  {
//	fmt.Println(filehandler.GetFiles())
//	return
	Args := os.Args
	ui.TviewConfigInit()
	if len(Args) > 1 {
		fmt.Println("Invalid command")
	}
	if Args[1] == "new" {
		ui.NewUI()
	} else if Args[1] == "list" {
		ui.ListUI()
	} else {
		fmt.Println("Invalid command")
	}
}
