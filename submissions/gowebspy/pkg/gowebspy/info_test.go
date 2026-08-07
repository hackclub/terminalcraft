package gowebspy

import (
	"net/http"
	"net/http/httptest"
	"strconv"
	"strings"
	"testing"
)

func TestExtractDomainFromURL(t *testing.T) {
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

func TestPortScan(t *testing.T) {
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_, err := w.Write([]byte("OK"))
		if err != nil {
			t.Fatalf("Failed to write response: %v", err)
		}
	}))
	defer server.Close()

	host, port := extractHostPort(server.URL)

	results := PortScan(host, []int{port})
	if !results[port] {
		t.Errorf("PortScan didn't detect open port %d", port)
	}

	nonExistentPort := 54321
	results = PortScan(host, []int{nonExistentPort})
	if results[nonExistentPort] {
		t.Errorf("PortScan incorrectly detected closed port %d as open", nonExistentPort)
	}
}

func TestCheckHTTPRedirects(t *testing.T) {
	finalHandler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		_, err := w.Write([]byte("Final destination"))
		if err != nil {
			t.Fatalf("Failed to write response: %v", err)
		}
	})

	redirectHandler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		http.Redirect(w, r, "/final", http.StatusFound)
	})

	mux := http.NewServeMux()
	mux.Handle("/final", finalHandler)
	mux.Handle("/redirect", redirectHandler)

	server := httptest.NewServer(mux)
	defer server.Close()

	redirects, err := CheckHTTPRedirects(server.URL + "/redirect")
	if err != nil {
		t.Fatalf("CheckHTTPRedirects failed: %v", err)
	}

	if len(redirects) != 2 {
		t.Errorf("Expected 2 redirects, got %d", len(redirects))
	}
}

func extractDomain(urlStr string) string {
	urlStr = strings.TrimPrefix(urlStr, "http://")
	urlStr = strings.TrimPrefix(urlStr, "https://")
	return strings.Split(strings.Split(urlStr, ":")[0], "/")[0]
}

func extractHostPort(url string) (string, int) {
	url = strings.TrimPrefix(url, "http://")
	parts := strings.Split(url, ":")
	host := parts[0]
	port := 80
	if len(parts) > 1 {
		port, _ = strconv.Atoi(parts[1])
	}
	return host, port
}
