package main

import (
	"testing"
)

func TestMin(t *testing.T) {
	tests := []struct {
		a, b, expected int
	}{
		{5, 10, 5},
		{10, 5, 5},
		{0, -5, -5},
		{-10, -5, -10},
		{0, 0, 0},
	}

	for _, test := range tests {
		result := min(test.a, test.b)
		if result != test.expected {
			t.Errorf("min(%d, %d) = %d, want %d", test.a, test.b, result, test.expected)
		}
	}
}

func TestGetPortName(t *testing.T) {
	tests := []struct {
		port int
		name string
	}{
		{80, "HTTP"},
		{443, "HTTPS"},
		{22, "SSH"},
		{99999, "Unknown"},
	}

	for _, test := range tests {
		result := getPortName(test.port)
		if result != test.name {
			t.Errorf("getPortName(%d) = %s, want %s", test.port, result, test.name)
		}
	}
}

func TestExtractDomain(t *testing.T) {
	tests := []struct {
		input    string
		expected string
	}{
		{"https://example.com/path", "example.com"},
		{"http://sub.domain.com", "sub.domain.com"},
		{"domain.com", "domain.com"},
		{"https://domain.com:8080/path?query=1", "domain.com"},
	}

	for _, test := range tests {
		result := extractDomain(test.input)
		if result != test.expected {
			t.Errorf("extractDomain(%q) = %q, want %q", test.input, result, test.expected)
		}
	}
}
