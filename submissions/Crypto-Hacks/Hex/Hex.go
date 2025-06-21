package Hex

import (
	"encoding/hex"
	"strings"
)

func Normal2Hex(input string) string {
	if input == "" {
		return "Input is empty"
	}else {
	encoded := hex.EncodeToString([]byte(input))

	return encoded
	}
}

func Hex2Normal(input string) string {
	input = strings.TrimSpace(input)
	decoded, err := hex.DecodeString(input)
	if input == "" {
		return "Input is empty"
	}else {
	if err != nil {
		return "Invalid Hex input"
	} else if err == nil {

		return string(decoded)
	}
	return "hi"
}
}
