package pocketbasehelper

import (
	"fmt"
	"log"

	"github.com/r--w/pocketbase"
)

var client = pocketbase.NewClient("https://folios.pockethost.io/")

type Snippet struct {
	ID        string `json:"id"`
	Title     string `json:"title"`
	Code      string `json:"code"`
	CreatedAt string `json:"created_at"`
}

func UploadSnippet(s Snippet) {
	data := map[string]any{
		"id":    s.ID,
		"title": s.Title,
		"code":  s.Code,
	}

	_, err := client.Create("snippets", data)

	if err != nil {
		fmt.Println("I couldn't upload your snippet to the server :(")
		log.Fatal(err)
	} else {
		fmt.Println("I've uploaded your snippet to the server :)")
	}
}

func RemoveSnippet(id string) {
	err := client.Delete("snippets", id)
	if err != nil {
		fmt.Println("Couldn't delete the snippet from the server :(")
	} else {
		fmt.Println("Snippet deleted from the server successfully :)")
	}
}
