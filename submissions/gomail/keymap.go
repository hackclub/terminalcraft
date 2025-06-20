package main

import "github.com/charmbracelet/bubbles/key"

type KeyMap struct {
	NextInput key.Binding
	PrevInput key.Binding
	Send      key.Binding
	Attach    key.Binding
	Unattach  key.Binding
	Back      key.Binding
	Compose   key.Binding
	Inbox     key.Binding
	Setup     key.Binding
	Quit      key.Binding
	ToggleCc  key.Binding
	Config    key.Binding
	Up        key.Binding
	Down      key.Binding
	Enter     key.Binding
	Refresh   key.Binding
	NextPage  key.Binding
	PrevPage  key.Binding
}

func DefaultKeybinds() KeyMap {
	return KeyMap{
		NextInput: key.NewBinding(
			key.WithKeys("tab", "ctrl+n"),
			key.WithHelp("tab/ctrl+n", "next field"),
		),
		PrevInput: key.NewBinding(
			key.WithKeys("shift+tab", "ctrl+p"),
			key.WithHelp("shift+tab/ctrl+p", "prev field"),
		),
		Send: key.NewBinding(
			key.WithKeys("ctrl+d", "ctrl+s"),
			key.WithHelp("ctrl+d/ctrl+s", "send"),
			key.WithDisabled(),
		),
		Attach: key.NewBinding(
			key.WithKeys("ctrl+a"),
			key.WithHelp("ctrl+a", "attach file"),
			key.WithDisabled(),
		),
		Unattach: key.NewBinding(
			key.WithKeys("ctrl+x", "ctrl+delete"),
			key.WithHelp("ctrl+x/ctrl+del", "remove"),
			key.WithDisabled(),
		),
		Back: key.NewBinding(
			key.WithKeys("esc", "ctrl+h"),
			key.WithHelp("esc/ctrl+h", "back"),
			key.WithDisabled(),
		),
		Compose: key.NewBinding(
			key.WithKeys("c"),
			key.WithHelp("c", "compose"),
		),
		Inbox: key.NewBinding(
			key.WithKeys("ctrl+i", "ctrl+b"),
			key.WithHelp("ctrl+i/ctrl+b", "inbox"),
		),
		Setup: key.NewBinding(
			key.WithKeys("ctrl+u"),
			key.WithHelp("ctrl+u", "setup"),
		),
		Quit: key.NewBinding(
			key.WithKeys("ctrl+c", "ctrl+q"),
			key.WithHelp("ctrl+c/ctrl+q", "quit"),
		),
		ToggleCc: key.NewBinding(
			key.WithKeys("ctrl+t"),
			key.WithHelp("ctrl+t", "toggle cc/bcc"),
		),
		Config: key.NewBinding(
			key.WithKeys("ctrl+g"),
			key.WithHelp("ctrl+g", "config"),
		),
		Up: key.NewBinding(
			key.WithKeys("up", "k"),
			key.WithHelp("↑/k", "up"),
		),
		Down: key.NewBinding(
			key.WithKeys("down", "j"),
			key.WithHelp("↓/j", "down"),
		),
		Enter: key.NewBinding(
			key.WithKeys("enter"),
			key.WithHelp("enter", "view email"),
		),
		Refresh: key.NewBinding(
			key.WithKeys("r"),
			key.WithHelp("r", "refresh"),
		),
		NextPage: key.NewBinding(
			key.WithKeys("n", "right"),
			key.WithHelp("n/→", "next page"),
		),
		PrevPage: key.NewBinding(
			key.WithKeys("p", "left"),
			key.WithHelp("p/←", "prev page"),
		),
	}
}

func (k KeyMap) ShortHelp() []key.Binding {
	return []key.Binding{
		k.NextInput,
		k.Send,
		k.ToggleCc,
		k.Quit,
	}
}

func (k KeyMap) FullHelp() [][]key.Binding {
	return [][]key.Binding{
		{k.NextInput, k.PrevInput, k.ToggleCc, k.Compose},
		{k.Send, k.Attach, k.Unattach, k.Inbox},
		{k.Back, k.Config, k.Quit},
	}
}

func (k KeyMap) InboxShortHelp() []key.Binding {
	return []key.Binding{
		k.Up,
		k.Down,
		k.Enter,
		k.Compose,
		k.Quit,
	}
}

func (k KeyMap) InboxFullHelp() [][]key.Binding {
	return [][]key.Binding{
		{k.Up, k.Down, k.Enter, k.Compose},
		{k.NextPage, k.PrevPage, k.Refresh, k.Config},
		{k.Setup, k.Quit},
	}
}

func (m *Model) updateKeymap() {

	m.keymap.Compose.SetEnabled(m.state == StateInbox || m.state == StateInboxViewing)
	m.keymap.Inbox.SetEnabled(m.state != StateInbox && m.state != StatePickingFile && m.state != StateSendingEmail)
	m.keymap.Config.SetEnabled(m.state == StateInbox)
	m.keymap.Setup.SetEnabled(m.state == StateInbox)

	m.keymap.Up.SetEnabled(m.state == StateInbox)
	m.keymap.Down.SetEnabled(m.state == StateInbox)
	m.keymap.Enter.SetEnabled(m.state == StateInbox)
	m.keymap.Refresh.SetEnabled(m.state == StateInbox)
	m.keymap.NextPage.SetEnabled(m.state == StateInbox)
	m.keymap.PrevPage.SetEnabled(m.state == StateInbox)

	m.keymap.Attach.SetEnabled(m.state == StateEditingAttachments)
	m.keymap.Send.SetEnabled(m.canSend() && m.state == StateHoveringSendButton)
	m.keymap.Unattach.SetEnabled(m.state == StateEditingAttachments && len(m.Attachments.Items()) > 0)
	m.keymap.Back.SetEnabled(m.state == StatePickingFile)

	m.keymap.NextInput.SetEnabled(m.state != StateInbox && m.state != StatePickingFile && m.state != StateSendingEmail)
	m.keymap.PrevInput.SetEnabled(m.state != StateInbox && m.state != StatePickingFile && m.state != StateSendingEmail)

	m.filepicker.KeyMap.Up.SetEnabled(m.state == StatePickingFile)
	m.filepicker.KeyMap.Down.SetEnabled(m.state == StatePickingFile)
	m.filepicker.KeyMap.Back.SetEnabled(m.state == StatePickingFile)
	m.filepicker.KeyMap.Select.SetEnabled(m.state == StatePickingFile)
	m.filepicker.KeyMap.Open.SetEnabled(m.state == StatePickingFile)
	m.filepicker.KeyMap.PageUp.SetEnabled(m.state == StatePickingFile)
	m.filepicker.KeyMap.PageDown.SetEnabled(m.state == StatePickingFile)
	m.filepicker.KeyMap.GoToTop.SetEnabled(m.state == StatePickingFile)
	m.filepicker.KeyMap.GoToLast.SetEnabled(m.state == StatePickingFile)
}

func (m Model) canSend() bool {
	return m.From.Value() != "" && m.To.Value() != "" && m.Subject.Value() != "" && m.Body.Value() != ""
}
