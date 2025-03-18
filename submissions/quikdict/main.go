package main

import (
	"fmt"
	"github.com/fatih/color"
	"golang.org/x/term"
	"os"
	"quikdict/cli"
	"quikdict/server"
)

func main() {
	if len(os.Args) < 2 {
		handleErrStr("no word was provided")
	}

	args, err := cli.Parse(os.Args[1:])
	handleErr(err)

	if args.Host {
		handleErr(server.Host(8246))
	} else {
		tw, _, err := term.GetSize(int(os.Stdin.Fd()))
		handleErr(err)
		handleErr(cli.Print(args, tw))
	}
}

func handleErrStr(err string) {
	fmt.Printf("%s %s\n", color.HiRedString("Error:"), err)
	os.Exit(1)
}

func handleErr(err error) {
	if err != nil {
		handleErrStr(err.Error())
	}
}
