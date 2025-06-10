package main

import (
	"io"
	"path/filepath"

	"github.com/charmbracelet/bubbles/list"
	tea "github.com/charmbracelet/bubbletea"
)

type attachment string

func (a attachment) FilterValue() string {
	return string(a)
}

type attachmentDelegate struct {
	focused bool
}

func (d attachmentDelegate) Height() int {
	return 1
}

func (d attachmentDelegate) Spacing() int {
	return 0
}

func (d attachmentDelegate) Render(w io.Writer, m list.Model, index int, item list.Item) {
	filename := filepath.Base(item.(attachment).FilterValue())
	style := textStyle

	if m.Index() == index && d.focused {
		style = activeTextStyle
	}

	var prefix string
	if m.Index() == index {
		prefix = "• "
	} else {
		prefix = "  "
	}

	_, _ = w.Write([]byte(style.Render(prefix + filename)))
}

func (d attachmentDelegate) Update(_ tea.Msg, _ *list.Model) tea.Cmd {
	return nil
}
