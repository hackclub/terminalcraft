package cmd

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/list"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

type model struct {
	notesList        list.Model
	confirmingDelete bool
	deleteIndex      int
	width            int
	height           int
}

type NoteItem struct {
	ID        string
	Message   string
	File      string
	Line      int
	CreatedAt time.Time
	Tags      []string
}

var _ list.Item = (*NoteItem)(nil)

func (i NoteItem) Title() string {
	if len(i.Message) > 40 {
		return i.Message[:37] + "..."
	}
	return i.Message
}

func (i NoteItem) Description() string {
	loc := ""
	if i.File != "" {
		if i.Line > 0 {
			loc = fmt.Sprintf("%s:%d", i.File, i.Line)
		} else {
			loc = i.File
		}
	}
	if len(i.Tags) > 0 {
		loc += " [" + strings.Join(i.Tags, ", ") + "]"
	}
	return loc
}

func (i NoteItem) FilterValue() string {
	return i.Message
}

func initialModel() (model, error) {
	notes, err := LoadAllNotes()
	if err != nil {
		return model{}, err
	}

	items := make([]list.Item, len(notes))
	for i, n := range notes {
		items[i] = NoteItem{
			ID:        n.ID,
			Message:   n.Message,
			File:      n.File,
			Line:      n.Line,
			CreatedAt: n.CreatedAt,
			Tags:      n.Tags,
		}
	}

	const listWidth = 20
	const listHeight = 10

	delegate := list.NewDefaultDelegate()

	l := list.New(items, delegate, listWidth, listHeight)
	l.Title = "Notes (press ↑/↓ to scroll, Delete to delete, q to quit)"
	l.SetShowStatusBar(false)
	l.SetFilteringEnabled(false)
	l.SetShowHelp(false)

	return model{
		notesList:        l,
		confirmingDelete: false,
		deleteIndex:      -1,
		width:            0,
		height:           0,
	}, nil
}

func LoadAllNotes() ([]Note, error) {
	root, err := os.Getwd()
	if err != nil {
		return nil, err
	}

	notesPath := filepath.Join(root, ".notes", "notes.json")
	if _, err := os.Stat(notesPath); os.IsNotExist(err) {
		return []Note{}, nil
	}

	data, err := os.ReadFile(notesPath)
	if err != nil {
		return nil, err
	}

	var notes []Note
	if err := json.Unmarshal(data, &notes); err != nil {
		return nil, err
	}

	return notes, nil
}

func DeleteNoteByID(id string) error {
	root, err := os.Getwd()
	if err != nil {
		return err
	}

	notesPath := filepath.Join(root, ".notes", "notes.json")
	if _, err := os.Stat(notesPath); os.IsNotExist(err) {
		return fmt.Errorf("notes file does not exist")
	}

	data, err := os.ReadFile(notesPath)
	if err != nil {
		return err
	}

	var notes []Note
	if err := json.Unmarshal(data, &notes); err != nil {
		return err
	}

	var updated []Note
	found := false
	for _, n := range notes {
		if n.ID[:8] == id || n.ID == id {
			found = true
			continue
		}
		updated = append(updated, n)
	}

	if !found {
		return fmt.Errorf("no note found with id %s", id)
	}

	out, err := json.MarshalIndent(updated, "", "  ")
	if err != nil {
		return err
	}

	return os.WriteFile(notesPath, out, 0644)
}

var (
	modalBorder = lipgloss.RoundedBorder()
	modalStyle  = lipgloss.NewStyle().
			Border(modalBorder, true).
			BorderForeground(lipgloss.Color("#FF5F87")).
			Foreground(lipgloss.Color("#FFFFFF")).
			Background(lipgloss.Color("#333333")).
			Padding(1, 2).
			Render
)

func (m model) Init() tea.Cmd {
	return nil
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {

	case tea.WindowSizeMsg:
		m.width, m.height = msg.Width, msg.Height
		m.notesList.SetSize(m.width-2, m.height-4)
		return m, nil

	case tea.KeyMsg:
		key := msg.String()

		if m.confirmingDelete {
			switch key {
			case "y", "yes", "Y":
				item := m.notesList.Items()[m.deleteIndex].(NoteItem)
				if err := DeleteNoteByID(item.ID); err != nil {
					fmt.Fprintf(os.Stderr, "Error deleting note: %v\n", err)
				}

				newModel, _ := initialModel()
				newModel.width, newModel.height = m.width, m.height
				newModel.notesList.SetSize(m.width-2, m.height-4)
				return newModel, nil

			default:
				// Make any other key cancel the deletion
				m.confirmingDelete = false
				m.deleteIndex = -1
				return m, nil
			}
		}

		switch key {
		case "q", "esc", "ctrl+c":
			return m, tea.Quit

		case "delete":
			idx := m.notesList.Index()
			if idx >= 0 && idx < len(m.notesList.Items()) {
				m.confirmingDelete = true
				m.deleteIndex = idx
			}
			return m, nil
		}
	}
	updatedList, cmd := m.notesList.Update(msg)
	m.notesList = updatedList
	return m, cmd
}

func (m model) View() string {
	if m.confirmingDelete {
		item := m.notesList.Items()[m.deleteIndex].(NoteItem)

		var lines []string
		lines = append(lines, "Delete note:", "")
		lines = append(lines, fmt.Sprintf("\"%s\"", item.Message), "")

		if item.File != "" {
			lines = append(lines, fmt.Sprintf("File: %s:%d", item.File, item.Line))
		}

		if len(item.Tags) > 0 {
			lines = append(lines, fmt.Sprintf("Tags: %s", strings.Join(item.Tags, ", ")))
		}

		lines = append(lines, "", "Press Y to confirm, any other key to cancel")

		content := strings.Join(lines, "\n")

		modal := modalStyle(content)
		return lipgloss.Place(m.width, m.height, lipgloss.Center, lipgloss.Center, modal)
	}

	return "\n" + m.notesList.View() + "\n\n(Use Delete to remove, q to quit)"
}
