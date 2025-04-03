package utils

import "strings"

// based on https://rosettacode.org/wiki/Word_wrap#Go
func WordWrap(text string, width int, newline string) string {
	words := strings.Fields(text)
	if len(words) == 0 {
		return ""
	}
	wrapped := words[0]
	spaceLeft := width - len(wrapped)
	for _, word := range words[1:] {
		if len(word)+1 > spaceLeft {
			wrapped += "\n" + newline + word
			spaceLeft = width - len(word)
		} else {
			wrapped += " " + word
			spaceLeft -= len(word) + 1
		}
	}
	return wrapped
}
