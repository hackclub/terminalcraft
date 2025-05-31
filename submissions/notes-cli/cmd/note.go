package cmd

import (
	"encoding/json"
	"os"
	"path/filepath"
	"time"

	"github.com/google/uuid"
)

type Note struct {
	ID        string    `json:"id"`
	Message   string    `json:"message"`
	File      string    `json:"file,omitempty"`
	Line      int       `json:"line,omitempty"`
	CreatedAt time.Time `json:"created_at"`
	Tags      []string  `json:"tags,omitempty"`
}

func SaveNote(message string, file string, line int, tags []string) error {
	//get the project root folder
	root, err := os.Getwd()
	if err != nil {
		return err
	}

	if file != "" {
		if relPath, err := filepath.Rel(root, file); err == nil {
			file = relPath
		}
	}

	note := Note{
		ID:        uuid.New().String(),
		Message:   message,
		File:      file,
		Line:      line,
		CreatedAt: time.Now(),
		Tags:      tags,
	}

	//create the notes directory if it doesn't exist
	notesDir := filepath.Join(root, ".notes")
	if err := os.MkdirAll(notesDir, 0755); err != nil {
		return err
	}

	if err := hideFile(notesDir); err != nil {
		return err
	}

	//read existing notes
	notesPath := filepath.Join(notesDir, "notes.json")
	var notes []Note

	if _, err := os.Stat(notesPath); err == nil {
		data, err := os.ReadFile(notesPath)
		if err != nil {
			return err
		}
		json.Unmarshal(data, &notes)
	}

	//Append the new note
	notes = append(notes, note)

	//Save the data back to the JSON file
	updatedData, err := json.MarshalIndent(notes, "", "  ")
	if err != nil {
		return err
	}

	return os.WriteFile(notesPath, updatedData, 0644)

}
