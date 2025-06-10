package main

import (
	"fmt"
	"strings"

	"github.com/charmbracelet/lipgloss"
)

const (
	primaryColor    = lipgloss.Color("99")
	highlightColor  = lipgloss.Color("#ECFD66")
	textActiveColor = lipgloss.Color("255")
	textColor       = lipgloss.Color("247")
	labelColor      = lipgloss.Color("241")
	mutedColor      = lipgloss.Color("236")
	errorColor      = lipgloss.Color("#FF5F87")
	successColor    = lipgloss.Color("#00AF87")
	neutralColor    = lipgloss.Color("#757575")
	codeColor       = lipgloss.Color("#3A3A3A")
)

var (
	activeTextStyle = lipgloss.NewStyle().Foreground(textActiveColor)
	textStyle       = lipgloss.NewStyle().Foreground(textColor)

	activeLabelStyle = lipgloss.NewStyle().Foreground(primaryColor)
	labelStyle       = lipgloss.NewStyle().Foreground(labelColor)

	placeholderStyle = lipgloss.NewStyle().Foreground(mutedColor)
	cursorStyle      = lipgloss.NewStyle().Foreground(textActiveColor)

	paddedStyle = lipgloss.NewStyle().Padding(1)

	errorHeaderStyle = lipgloss.NewStyle().
				Foreground(lipgloss.Color("#F1F1F1")).
				Background(errorColor).
				Bold(true).
				Padding(0, 1).
				SetString("ERROR")
	errorStyle = lipgloss.NewStyle().Foreground(errorColor)

	commentStyle = lipgloss.NewStyle().
			Foreground(neutralColor).
			PaddingLeft(1)

	sendButtonActiveStyle = lipgloss.NewStyle().
				Background(primaryColor).
				Foreground(highlightColor).
				Padding(0, 2)
	sendButtonInactiveStyle = lipgloss.NewStyle().
				Background(mutedColor).
				Foreground(textColor).
				Padding(0, 2)
	sendButtonStyle = lipgloss.NewStyle().
			Background(mutedColor).
			Foreground(labelColor).
			Padding(0, 2)

	inlineCodeStyle = lipgloss.NewStyle().
			Foreground(errorColor).
			Background(codeColor).
			Padding(0, 1)
	linkStyle = lipgloss.NewStyle().
			Foreground(successColor).
			Underline(true)
	successStyle = lipgloss.NewStyle().
			Foreground(successColor).
			Bold(true)
)

const (
	defaultTerminalWidth = 80
	wrapMargin           = 4
)

func wrapText(text string, width int) string {
	if width <= 0 {
		width = defaultTerminalWidth
	}

	effectiveWidth := width - wrapMargin

	if effectiveWidth <= 10 {
		effectiveWidth = 40
	}

	lines := strings.Split(text, "\n")
	var wrapped []string

	for _, line := range lines {
		if len(line) <= effectiveWidth {
			wrapped = append(wrapped, line)
			continue
		}

		words := strings.Fields(line)
		if len(words) == 0 {
			wrapped = append(wrapped, "")
			continue
		}

		var currentLine strings.Builder
		currentLength := 0

		for _, word := range words {
			wordLen := len(word)

			if currentLength > 0 && currentLength+1+wordLen > effectiveWidth {
				wrapped = append(wrapped, currentLine.String())
				currentLine.Reset()
				currentLength = 0
			}

			if currentLength > 0 {
				currentLine.WriteString(" ")
				currentLength++
			}

			currentLine.WriteString(word)
			currentLength += wordLen
		}

		if currentLine.Len() > 0 {
			wrapped = append(wrapped, currentLine.String())
		}
	}

	return strings.Join(wrapped, "\n")
}

func wrapTextStyle(text string, width int, style lipgloss.Style) string {
	wrapped := wrapText(text, width)
	return style.Render(wrapped)
}

func emailSummary(recipients []string, subject string) string {
	var summary strings.Builder
	summary.WriteString("\n  Email ")
	summary.WriteString(activeTextStyle.Render("\"" + subject + "\""))
	summary.WriteString(" sent to ")

	for i, recipient := range recipients {
		if i > 0 {
			summary.WriteString(", ")
		}
		summary.WriteString(linkStyle.Render(strings.TrimSpace(recipient)))
	}
	summary.WriteString("\n\n")

	return summary.String()
}

func truncateText(text string, maxLength int) string {
	if len(text) <= maxLength {
		return text
	}
	if maxLength <= 3 {
		return "..."
	}
	return text[:maxLength-3] + "..."
}

func formatEmailLine(from, subject string, terminalWidth int, prefix string) string {

	prefixLen := len(prefix)
	separatorLen := 3
	availableWidth := terminalWidth - prefixLen - separatorLen - wrapMargin

	if availableWidth <= 10 {
		availableWidth = 40
	}

	fromWidth := availableWidth / 3
	if fromWidth < 15 {
		fromWidth = 15
	}

	subjectWidth := availableWidth - fromWidth
	if subjectWidth < 10 {
		subjectWidth = 10
		fromWidth = availableWidth - subjectWidth
	}

	truncatedFrom := truncateText(from, fromWidth)
	truncatedSubject := truncateText(subject, subjectWidth)

	return fmt.Sprintf("%s%s - %s", prefix, truncatedFrom, truncatedSubject)
}
