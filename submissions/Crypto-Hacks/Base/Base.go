package Base

import (
	"encoding/base32"
	"encoding/base64")

func Normal2base64(input string) string {
	if input == "" {
		return "Input is empty"
	}else {
	encoded := base64.StdEncoding.EncodeToString([]byte(input))

	return encoded
	}
}

func Base642Normal(input string) string {
	decoded, err := base64.StdEncoding.DecodeString(input)
	if input == "" {
		return "Input is empty"
	}else {
	if err != nil {
		return "Invalid Base64 input"
	} else if err == nil {
		return string(decoded)
	}
	return "hi"
	}
}

func Normal2base32(input string) string {
	if input == "" {
		return "Input is empty"
	}else {
	str := base32.StdEncoding.EncodeToString([]byte(input))
	return str
	}
}

func Base322Normal(input string) string {
	decoded, err := base32.StdEncoding.DecodeString(input)
if input == "" {
		return "Input is empty"
	}else {
	if err != nil {
		return "Invalid Base32 input"
	} else if err == nil {
		return string(decoded)
	}
	return "hi"
}
}
