package util

import (
	"os"

	"github.com/charmbracelet/lipgloss"
)

func ErrorPrinter(err error) {
	if err != nil {
		errorStyle := lipgloss.NewStyle().Foreground(lipgloss.Color("9")).Bold(true).BorderTop(true).BorderBottom(true).BorderStyle(lipgloss.NormalBorder())
		errorMessage := errorStyle.Render("Error: " + err.Error())
		println(errorMessage)
		os.Exit(1)
	}
}

func ErrorHandler[T any](result T, err error) T {
	if err != nil {
		ErrorPrinter(err)
		return result
	}
	return result
}

func ErrorOnlyHandler[T any](result T, err error) error {
	if err == nil {
		ErrorPrinter(err)
		return err
	}

	return nil
}

func SuccessPrinter(message string) {
	successStyle := lipgloss.NewStyle().Foreground(lipgloss.Color("2")).Bold(true).BorderBottom(true).BorderStyle(lipgloss.NormalBorder())
	successMessage := successStyle.Render("Success: " + message)
	println(successMessage)
}
