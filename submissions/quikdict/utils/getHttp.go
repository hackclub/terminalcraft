package utils

import (
	"errors"
	"io"
	"net/http"
)

func GetHttp(url string, method string, header http.Header, body io.Reader) ([]byte, error) {
	client := &http.Client{}
	req, err := http.NewRequest(method, url, body)
	if err != nil {
		return nil, err
	}

	req.Header = header

	r, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer r.Body.Close()

	// Return definition not found when not 200 (even if not quite universally correct)
	if r.StatusCode != 200 {
		return nil, errors.New("server returned " + r.Status)
	}

	// Parse the response body
	return io.ReadAll(r.Body)
}
