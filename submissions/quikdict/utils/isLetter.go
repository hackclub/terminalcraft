package utils

import (
	"strings"
	"unicode"
)

func IsLetter(s string) bool {
	return !strings.ContainsFunc(s, func(r rune) bool {
		return !unicode.IsLetter(r)
	})
}
