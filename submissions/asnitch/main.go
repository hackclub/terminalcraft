package main

import (
	"os"
	"os/signal"
	"syscall"

	"ssmidge.xyz/asnitch/cmd"
)

func main() {
	// Set up channel to listen for termination signals (Ctrl+C, SIGTERM)
	signalChannel := make(chan os.Signal, 1)
	signal.Notify(signalChannel, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		cmd.Execute()
	}()

	<-signalChannel
	os.Exit(0)
}
