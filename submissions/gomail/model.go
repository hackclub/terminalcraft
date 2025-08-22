package main

import (
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/filepicker"
	"github.com/charmbracelet/bubbles/help"
	"github.com/charmbracelet/bubbles/key"
	"github.com/charmbracelet/bubbles/list"
	"github.com/charmbracelet/bubbles/spinner"
	"github.com/charmbracelet/bubbles/textarea"
	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/x/exp/ordered"
	"github.com/resendlabs/resend-go"
)

type State int

const (
	StateInbox State = iota
	StateInboxLoading
	StateInboxViewing
	StateCompose
	StateEditingFrom
	StateEditingTo
	StateEditingCc
	StateEditingBcc
	StateEditingSubject
	StateEditingBody
	StateEditingAttachments
	StateHoveringSendButton
	StatePickingFile
	StateSendingEmail
	StateConfiguration
)

type DeliveryMethod int

const (
	DeliveryMethodNone DeliveryMethod = iota
	DeliveryMethodResend
	DeliveryMethodSMTP
	DeliveryMethodUnknown
)

type Model struct {
	state        State
	composeState State

	DeliveryMethod DeliveryMethod

	inboxEmails    []InboxEmail
	selectedEmail  int
	inboxManager   *InboxManager
	currentPage    int
	emailsPerPage  int
	totalEmails    int
	isLoadingInbox bool

	From textinput.Model

	To textinput.Model

	Subject textinput.Model

	Body textarea.Model

	Attachments list.Model

	showCc bool
	Cc     textinput.Model
	Bcc    textinput.Model

	filepicker     filepicker.Model
	loadingSpinner spinner.Model
	help           help.Model
	keymap         KeyMap
	quitting       bool
	abort          bool
	err            error

	terminalWidth  int
	terminalHeight int
}

func NewModel(defaults resend.SendEmailRequest, deliveryMethod DeliveryMethod, config *TOMLConfig) Model {
	from := textinput.New()
	from.Prompt = "From "
	from.Placeholder = "me@example.com"
	from.PromptStyle = labelStyle
	from.TextStyle = textStyle
	from.Cursor.Style = cursorStyle
	from.PlaceholderStyle = placeholderStyle
	from.SetValue(defaults.From)

	to := textinput.New()
	to.Prompt = "To "
	to.PromptStyle = labelStyle
	to.Cursor.Style = cursorStyle
	to.PlaceholderStyle = placeholderStyle
	to.TextStyle = textStyle
	to.Placeholder = "you@example.com"
	to.SetValue(strings.Join(defaults.To, ToSeparator))

	cc := textinput.New()
	cc.Prompt = "Cc "
	cc.PromptStyle = labelStyle
	cc.Cursor.Style = cursorStyle
	cc.PlaceholderStyle = placeholderStyle
	cc.TextStyle = textStyle
	cc.Placeholder = "cc@example.com"
	cc.SetValue(strings.Join(defaults.Cc, ToSeparator))

	bcc := textinput.New()
	bcc.Prompt = "Bcc "
	bcc.PromptStyle = labelStyle
	bcc.Cursor.Style = cursorStyle
	bcc.PlaceholderStyle = placeholderStyle
	bcc.TextStyle = textStyle
	bcc.Placeholder = "bcc@example.com"
	bcc.SetValue(strings.Join(defaults.Bcc, ToSeparator))

	subject := textinput.New()
	subject.Prompt = "Subject "
	subject.PromptStyle = labelStyle
	subject.Cursor.Style = cursorStyle
	subject.PlaceholderStyle = placeholderStyle
	subject.TextStyle = textStyle
	subject.Placeholder = "Hello!"
	subject.SetValue(defaults.Subject)

	body := textarea.New()
	body.Placeholder = "# Email"
	body.ShowLineNumbers = false
	body.FocusedStyle.CursorLine = activeTextStyle
	body.FocusedStyle.Prompt = activeLabelStyle
	body.FocusedStyle.Text = activeTextStyle
	body.FocusedStyle.Placeholder = placeholderStyle
	body.BlurredStyle.CursorLine = textStyle
	body.BlurredStyle.Prompt = labelStyle
	body.BlurredStyle.Text = textStyle
	body.BlurredStyle.Placeholder = placeholderStyle
	body.Cursor.Style = cursorStyle
	body.CharLimit = 4000
	body.SetValue(defaults.Text)

	body.CursorUp()
	body.CursorUp()

	body.Blur()

	state := StateInbox

	composeState := StateEditingBody
	switch {
	case defaults.From == "":
		composeState = StateEditingFrom
	case len(defaults.To) == 0:
		composeState = StateEditingTo
	case defaults.Subject == "":
		composeState = StateEditingSubject
	case defaults.Text == "":
		composeState = StateEditingBody
	}

	attachments := list.New([]list.Item{}, attachmentDelegate{}, 0, 3)
	attachments.DisableQuitKeybindings()
	attachments.SetShowTitle(true)
	attachments.Title = "Attachments"
	attachments.Styles.Title = labelStyle
	attachments.Styles.TitleBar = labelStyle
	attachments.Styles.NoItems = placeholderStyle
	attachments.SetShowHelp(false)
	attachments.SetShowStatusBar(false)
	attachments.SetStatusBarItemName("attachment", "attachments")
	attachments.SetShowPagination(false)

	for _, a := range defaults.Attachments {
		attachments.InsertItem(0, attachment(a.Filename))
	}

	picker := filepicker.New()
	picker.CurrentDirectory, _ = os.UserHomeDir()

	loadingSpinner := spinner.New()
	loadingSpinner.Style = activeLabelStyle
	loadingSpinner.Spinner = spinner.Dot

	inboxManager := NewInboxManager()
	if config != nil {

		if err := inboxManager.ConfigureFromTOML(config); err != nil {

			fmt.Printf("Warning: Could not configure inbox: %v\n", err)
		}
	}

	if dbManager, err := NewDatabaseManager(); err == nil {
		inboxManager.SetDatabaseManager(dbManager)
	} else {
		fmt.Printf("Warning: Could not initialize database for caching: %v\n", err)
	}

	m := Model{
		state:          state,
		composeState:   composeState,
		From:           from,
		To:             to,
		showCc:         len(cc.Value()) > 0 || len(bcc.Value()) > 0,
		Cc:             cc,
		Bcc:            bcc,
		Subject:        subject,
		Body:           body,
		Attachments:    attachments,
		filepicker:     picker,
		help:           help.New(),
		keymap:         DefaultKeybinds(),
		loadingSpinner: loadingSpinner,
		DeliveryMethod: deliveryMethod,
		inboxManager:   inboxManager,
		inboxEmails:    []InboxEmail{},
		selectedEmail:  0,
		currentPage:    0,
		emailsPerPage:  10,
		totalEmails:    0,
		isLoadingInbox: false,
		terminalWidth:  defaultTerminalWidth,
		terminalHeight: 24,
	}

	m.focusActiveInput()

	return m
}

func (m Model) Init() tea.Cmd {
	return tea.Batch(
		m.From.Cursor.BlinkCmd(),
		m.loadInboxCmd(),
	)
}

type clearErrMsg struct{}

func clearErrAfter(d time.Duration) tea.Cmd {
	return tea.Tick(d, func(t time.Time) tea.Msg {
		return clearErrMsg{}
	})
}

func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.WindowSizeMsg:
		m.terminalWidth = msg.Width
		m.terminalHeight = msg.Height
		return m, nil
	case inboxLoadedMsg:
		m.inboxEmails = []InboxEmail(msg)
		m.selectedEmail = 0
		m.isLoadingInbox = false
		return m, nil
	case inboxErrorMsg:
		m.err = error(msg)
		m.isLoadingInbox = false
		return m, clearErrAfter(5 * time.Second)
	case sendEmailSuccessMsg:
		m.quitting = true
		return m, tea.Quit
	case sendEmailFailureMsg:
		m.blurInputs()
		m.state = StateEditingFrom
		m.focusActiveInput()
		m.err = msg
		return m, clearErrAfter(10 * time.Second)
	case clearErrMsg:
		m.err = nil
	case tea.KeyMsg:

		switch {
		case key.Matches(msg, m.keymap.Compose):
			if m.state == StateInbox || m.state == StateInboxViewing {
				m.state = m.composeState
				m.focusActiveInput()
				return m, nil
			}
		case key.Matches(msg, m.keymap.Inbox):
			if m.state != StateInbox && m.state != StatePickingFile && m.state != StateSendingEmail {
				m.blurInputs()
				m.composeState = m.state
				m.state = StateInbox
				return m, nil
			}
		case key.Matches(msg, m.keymap.Quit):
			m.quitting = true
			m.abort = true
			return m, tea.Quit
		case key.Matches(msg, m.keymap.Config):
			if m.state == StateInbox {
				m.state = StateConfiguration
				return m, nil
			}
		case key.Matches(msg, m.keymap.Setup):
			if m.state == StateInbox {

				m.quitting = true
				return m, tea.Quit
			}
		case key.Matches(msg, m.keymap.ToggleCc):
			m.showCc = !m.showCc

			if m.showCc && m.state == StateEditingTo {
				m.blurInputs()
				m.state = StateEditingCc
				m.focusActiveInput()
			}
			return m, nil
		}

		if !m.isTypingInTextArea(msg) {
			switch {
			case key.Matches(msg, m.keymap.NextInput):
				return m.handleNextInput(), nil
			case key.Matches(msg, m.keymap.PrevInput):
				return m.handlePrevInput(), nil
			case key.Matches(msg, m.keymap.Back):
				m.state = StateEditingAttachments
				m.updateKeymap()
				return m, nil
			case key.Matches(msg, m.keymap.Send):
				m.state = StateSendingEmail
				return m, tea.Batch(
					m.loadingSpinner.Tick,
					m.sendEmailCmd(),
				)
			case key.Matches(msg, m.keymap.Attach):
				m.state = StatePickingFile
				return m, m.filepicker.Init()
			case key.Matches(msg, m.keymap.Unattach):
				m.Attachments.RemoveItem(m.Attachments.Index())
				m.Attachments.SetHeight(ordered.Max(len(m.Attachments.Items()), 1) + 2)
			}
		}

		if msg.String() == "enter" {
			switch m.state {
			case StateEditingFrom, StateEditingTo, StateEditingCc, StateEditingBcc, StateEditingSubject:

				return m.handleNextInput(), nil
			case StateEditingBody:

				break
			case StateEditingAttachments:

				if key.Matches(msg, m.keymap.Attach) {
					m.state = StatePickingFile
					return m, m.filepicker.Init()
				}
			case StateHoveringSendButton:

				if m.canSend() {
					m.state = StateSendingEmail
					return m, tea.Batch(
						m.loadingSpinner.Tick,
						m.sendEmailCmd(),
					)
				}
			}
		}

		if m.state == StateInbox {
			switch {
			case key.Matches(msg, m.keymap.Up):
				if m.selectedEmail > 0 {
					m.selectedEmail--
				}
				return m, nil
			case key.Matches(msg, m.keymap.Down):
				if len(m.inboxEmails) > 0 && m.selectedEmail < len(m.inboxEmails)-1 {
					m.selectedEmail++
				}
				return m, nil
			case key.Matches(msg, m.keymap.Enter):
				if len(m.inboxEmails) > 0 && m.selectedEmail < len(m.inboxEmails) {
					m.state = StateInboxViewing
				}
				return m, nil
			case key.Matches(msg, m.keymap.Refresh):

				m.isLoadingInbox = true
				return m, m.loadInboxCmd()
			case key.Matches(msg, m.keymap.NextPage):

				m.currentPage++
				m.selectedEmail = 0
				m.isLoadingInbox = true
				return m, m.loadInboxCmd()
			case key.Matches(msg, m.keymap.PrevPage):

				if m.currentPage > 0 {
					m.currentPage--
					m.selectedEmail = 0
					m.isLoadingInbox = true
					return m, m.loadInboxCmd()
				}
				return m, nil
			case msg.String() == "s" && !m.inboxManager.IsConfigured():

				m.quitting = true
				return m, tea.Quit
			}
		}

		if m.state == StateInboxViewing {
			switch msg.String() {
			case "esc", "q":
				m.state = StateInbox
				return m, nil
			}
		}
	}

	m.updateKeymap()

	var cmds []tea.Cmd
	var cmd tea.Cmd
	m.From, cmd = m.From.Update(msg)
	cmds = append(cmds, cmd)
	m.To, cmd = m.To.Update(msg)
	cmds = append(cmds, cmd)
	if m.showCc {
		m.Cc, cmd = m.Cc.Update(msg)
		cmds = append(cmds, cmd)
		m.Bcc, cmd = m.Bcc.Update(msg)
		cmds = append(cmds, cmd)
	}
	m.Subject, cmd = m.Subject.Update(msg)
	cmds = append(cmds, cmd)
	m.Body, cmd = m.Body.Update(msg)
	cmds = append(cmds, cmd)
	m.filepicker, cmd = m.filepicker.Update(msg)
	cmds = append(cmds, cmd)

	switch m.state {
	case StatePickingFile:
		if didSelect, path := m.filepicker.DidSelectFile(msg); didSelect {
			m.Attachments.InsertItem(0, attachment(path))
			m.Attachments.SetHeight(len(m.Attachments.Items()) + 2)
			m.state = StateEditingAttachments
			m.updateKeymap()
		}
	case StateEditingAttachments:
		m.Attachments, cmd = m.Attachments.Update(msg)
		cmds = append(cmds, cmd)
	case StateSendingEmail:
		m.loadingSpinner, cmd = m.loadingSpinner.Update(msg)
		cmds = append(cmds, cmd)
	}

	m.help, cmd = m.help.Update(msg)
	cmds = append(cmds, cmd)

	return m, tea.Batch(cmds...)
}

func (m *Model) blurInputs() {
	m.From.Blur()
	m.To.Blur()
	m.Subject.Blur()
	m.Body.Blur()
	if m.showCc {
		m.Cc.Blur()
		m.Bcc.Blur()
	}
	m.From.PromptStyle = labelStyle
	m.To.PromptStyle = labelStyle
	if m.showCc {
		m.Cc.PromptStyle = labelStyle
		m.Cc.TextStyle = textStyle
		m.Bcc.PromptStyle = labelStyle
		m.Bcc.TextStyle = textStyle
	}
	m.Subject.PromptStyle = labelStyle
	m.From.TextStyle = textStyle
	m.To.TextStyle = textStyle
	m.Subject.TextStyle = textStyle
	m.Attachments.Styles.Title = labelStyle
	m.Attachments.SetDelegate(attachmentDelegate{false})
}

func (m *Model) focusActiveInput() {
	switch m.state {
	case StateEditingFrom:
		m.From.PromptStyle = activeLabelStyle
		m.From.TextStyle = activeTextStyle
		m.From.Focus()
		m.From.CursorEnd()
	case StateEditingTo:
		m.To.PromptStyle = activeLabelStyle
		m.To.TextStyle = activeTextStyle
		m.To.Focus()
		m.To.CursorEnd()
	case StateEditingCc:
		m.Cc.PromptStyle = activeLabelStyle
		m.Cc.TextStyle = activeTextStyle
		m.Cc.Focus()
		m.Cc.CursorEnd()
	case StateEditingBcc:
		m.Bcc.PromptStyle = activeLabelStyle
		m.Bcc.TextStyle = activeTextStyle
		m.Bcc.Focus()
		m.Bcc.CursorEnd()
	case StateEditingSubject:
		m.Subject.PromptStyle = activeLabelStyle
		m.Subject.TextStyle = activeTextStyle
		m.Subject.Focus()
		m.Subject.CursorEnd()
	case StateEditingBody:
		m.Body.Focus()
		m.Body.CursorEnd()
	case StateEditingAttachments:
		m.Attachments.Styles.Title = activeLabelStyle
		m.Attachments.SetDelegate(attachmentDelegate{true})
	}
}

func (m Model) View() string {
	if m.quitting {
		return ""
	}

	switch m.state {
	case StateInbox:
		return m.inboxView()
	case StateInboxViewing:
		return m.inboxViewingView()
	case StateConfiguration:
		return m.configurationView()
	case StatePickingFile:
		return "\n" + activeLabelStyle.Render("Attachments") + " " + commentStyle.Render(m.filepicker.CurrentDirectory) +
			"\n\n" + m.filepicker.View()
	case StateSendingEmail:
		return "\n " + m.loadingSpinner.View() + "Sending email"
	}

	return m.composeView()
}

func (m Model) inboxView() string {
	var s strings.Builder

	s.WriteString(activeLabelStyle.Render("📬 Inbox"))

	if m.inboxManager.IsConfigured() {
		s.WriteString(" " + textStyle.Render(fmt.Sprintf("(%s)", m.inboxManager.host)))
	} else {
		s.WriteString(" " + errorStyle.Render("(not configured)"))
	}

	if len(m.inboxEmails) > 0 {
		startEmail := m.currentPage*m.emailsPerPage + 1
		endEmail := startEmail + len(m.inboxEmails) - 1
		s.WriteString(" " + commentStyle.Render(fmt.Sprintf("(Page %d: %d-%d)", m.currentPage+1, startEmail, endEmail)))
	}
	s.WriteString("\n\n")

	if m.err != nil {
		wrappedError := wrapTextStyle("Error: "+m.err.Error(), m.terminalWidth, errorStyle)
		s.WriteString(wrappedError)
		s.WriteString("\n\n")
	}

	if m.isLoadingInbox {
		s.WriteString(commentStyle.Render("  Loading emails..."))
		s.WriteString("\n\n")
	} else if len(m.inboxEmails) == 0 {
		if m.inboxManager.IsConfigured() {
			s.WriteString(commentStyle.Render("  No emails found"))
		} else {
			s.WriteString(commentStyle.Render("  📧 Inbox not configured"))
			s.WriteString("\n\n")
			s.WriteString(textStyle.Render("  To view your inbox, you need IMAP settings configured."))
			s.WriteString("\n")
			s.WriteString(textStyle.Render("  Run 'gomail setup' to configure email settings."))
			s.WriteString("\n\n")
			s.WriteString(commentStyle.Render("  For Gmail: Enable 2FA and use an App Password"))
			s.WriteString("\n")
			s.WriteString(commentStyle.Render("  For Outlook: Use your regular password"))
		}
		s.WriteString("\n\n")
	} else {

		for i, email := range m.inboxEmails {
			prefix := "  "
			if i == m.selectedEmail {
				prefix = "▶ "

				emailLine := formatEmailLine(email.From, email.Subject, m.terminalWidth, prefix)
				s.WriteString(activeLabelStyle.Render(emailLine))
			} else {
				emailLine := formatEmailLine(email.From, email.Subject, m.terminalWidth, prefix)
				if email.IsUnread {
					s.WriteString(textStyle.Render(emailLine) + " " + activeLabelStyle.Render("●"))
				} else {
					s.WriteString(commentStyle.Render(emailLine))
				}
			}
			s.WriteString("\n")
		}
		s.WriteString("\n")
	}

	if !m.inboxManager.IsConfigured() {
		s.WriteString(commentStyle.Render("  Press 's' to run setup wizard"))
		s.WriteString("\n")
	}
	s.WriteString(m.getHelpView())

	return paddedStyle.Render(s.String())
}

func (m Model) configurationView() string {
	var s strings.Builder

	s.WriteString(activeLabelStyle.Render("🔧 Configuration"))
	s.WriteString("\n\n")

	config, err := LoadTOMLConfig()
	if err != nil {
		s.WriteString(errorStyle.Render("Error loading configuration: " + err.Error()))
		s.WriteString("\n\n")
		s.WriteString(commentStyle.Render("Press 'i' to return to inbox"))
		return paddedStyle.Render(s.String())
	}

	s.WriteString(labelStyle.Render("Application Settings:"))
	s.WriteString("\n")
	s.WriteString(fmt.Sprintf("  Default From: %s\n", textStyle.Render(config.App.DefaultFrom)))
	s.WriteString(fmt.Sprintf("  Signature: %s\n", textStyle.Render(config.App.Signature)))
	s.WriteString(fmt.Sprintf("  Unsafe HTML: %s\n", textStyle.Render(strconv.FormatBool(config.App.UnsafeHTML))))
	s.WriteString("\n")

	s.WriteString(labelStyle.Render("Email Settings:"))
	s.WriteString("\n")
	s.WriteString(fmt.Sprintf("  Delivery Method: %s\n", textStyle.Render(config.Email.DeliveryMethod)))
	s.WriteString(fmt.Sprintf("  SMTP Host: %s\n", textStyle.Render(config.Email.SMTP.Host)))
	s.WriteString(fmt.Sprintf("  SMTP Port: %s\n", textStyle.Render(strconv.Itoa(config.Email.SMTP.Port))))
	s.WriteString(fmt.Sprintf("  SMTP Username: %s\n", textStyle.Render(config.Email.SMTP.Username)))
	s.WriteString("\n")

	s.WriteString(labelStyle.Render("UI Settings:"))
	s.WriteString("\n")
	s.WriteString(fmt.Sprintf("  Theme: %s\n", textStyle.Render(config.UI.Theme)))
	s.WriteString(fmt.Sprintf("  Show CC/BCC: %s\n", textStyle.Render(strconv.FormatBool(config.UI.ShowCcBcc))))
	s.WriteString(fmt.Sprintf("  Compact Mode: %s\n", textStyle.Render(strconv.FormatBool(config.UI.CompactMode))))
	s.WriteString("\n")

	s.WriteString(commentStyle.Render("Use 'gomail config' CLI commands to modify settings"))
	s.WriteString("\n")
	s.WriteString(commentStyle.Render("Use 'gomail reconfigure' to launch setup wizard"))
	s.WriteString("\n")
	s.WriteString(commentStyle.Render("Press 'i' to return to inbox"))

	return paddedStyle.Render(s.String())
}

func (m Model) composeView() string {
	var s strings.Builder

	statusLine := ""
	switch m.state {
	case StateEditingFrom:
		statusLine = "📝 Editing From field"
	case StateEditingTo:
		statusLine = "📝 Editing To field"
	case StateEditingCc:
		statusLine = "📝 Editing CC field"
	case StateEditingBcc:
		statusLine = "📝 Editing BCC field"
	case StateEditingSubject:
		statusLine = "📝 Editing Subject"
	case StateEditingBody:
		statusLine = "📝 Editing Message Body"
	case StateEditingAttachments:
		statusLine = "📎 Managing Attachments"
	case StateHoveringSendButton:
		if m.canSend() {
			statusLine = "🚀 Ready to Send"
		} else {
			statusLine = "⚠️  Fill required fields to send"
		}
	}

	if statusLine != "" {
		s.WriteString(commentStyle.Render(statusLine))
		s.WriteString("\n\n")
	}

	s.WriteString(m.From.View())
	s.WriteString("\n")
	s.WriteString(m.To.View())
	if !m.showCc {
		s.WriteString(" ")
		s.WriteString(commentStyle.Render("(ctrl+t to add CC/BCC)"))
	}
	s.WriteString("\n")
	if m.showCc {
		s.WriteString(m.Cc.View())
		s.WriteString("\n")
		s.WriteString(m.Bcc.View())
		s.WriteString("\n")
	}
	s.WriteString(m.Subject.View())
	s.WriteString("\n\n")
	s.WriteString(m.Body.View())
	s.WriteString("\n\n")
	s.WriteString(m.Attachments.View())
	s.WriteString("\n")
	if m.state == StateHoveringSendButton && m.canSend() {
		s.WriteString(sendButtonActiveStyle.Render("Send"))
	} else if m.state == StateHoveringSendButton {
		s.WriteString(sendButtonInactiveStyle.Render("Send"))
	} else {
		s.WriteString(sendButtonStyle.Render("Send"))
	}
	s.WriteString("\n\n")
	s.WriteString(m.getHelpView())

	if m.err != nil {
		s.WriteString("\n\n")
		wrappedError := wrapTextStyle(m.err.Error(), m.terminalWidth, errorStyle)
		s.WriteString(wrappedError)
	}

	return paddedStyle.Render(s.String())
}

func (m *Model) isTypingInTextArea(msg tea.KeyMsg) bool {

	if len(msg.String()) == 1 {
		return true
	}

	switch msg.String() {
	case "backspace", "delete", "left", "right", "up", "down",
		"home", "end", "pageup", "pagedown", "ctrl+a", "ctrl+c",
		"ctrl+v", "ctrl+x", "ctrl+z", "ctrl+y":
		return true
	}

	if m.state == StateEditingBody && (msg.String() == "tab" || msg.String() == "shift+tab") {
		return true
	}

	return false
}

func (m *Model) handleNextInput() tea.Model {
	m.blurInputs()
	switch m.state {
	case StateEditingFrom:
		m.state = StateEditingTo
	case StateEditingTo:
		if m.showCc {
			m.state = StateEditingCc
		} else {
			m.state = StateEditingSubject
		}
	case StateEditingCc:
		m.state = StateEditingBcc
	case StateEditingBcc:
		m.state = StateEditingSubject
	case StateEditingSubject:
		m.state = StateEditingBody
	case StateEditingBody:
		m.state = StateEditingAttachments
	case StateEditingAttachments:
		m.state = StateHoveringSendButton
	case StateHoveringSendButton:
		m.state = StateEditingFrom
	}
	m.focusActiveInput()
	return m
}

func (m *Model) handlePrevInput() tea.Model {
	m.blurInputs()
	switch m.state {
	case StateEditingFrom:
		m.state = StateHoveringSendButton
	case StateEditingTo:
		m.state = StateEditingFrom
	case StateEditingCc:
		m.state = StateEditingTo
	case StateEditingBcc:
		m.state = StateEditingCc
	case StateEditingSubject:
		if m.showCc {
			m.state = StateEditingBcc
		} else {
			m.state = StateEditingTo
		}
	case StateEditingBody:
		m.state = StateEditingSubject
	case StateEditingAttachments:
		m.state = StateEditingBody
	case StateHoveringSendButton:
		m.state = StateEditingAttachments
	}
	m.focusActiveInput()
	return m
}

type loadInboxMsg struct{}
type inboxLoadedMsg []InboxEmail
type inboxErrorMsg error

func (m Model) loadInboxCmd() tea.Cmd {
	return func() tea.Msg {
		if !m.inboxManager.IsConfigured() {
			return inboxErrorMsg(fmt.Errorf("inbox not configured - SMTP settings required"))
		}

		emails, err := m.inboxManager.FetchInboxEmails(m.emailsPerPage, m.currentPage*m.emailsPerPage)
		if err != nil {
			return inboxErrorMsg(err)
		}

		if len(emails) > 0 {
			prefetchCount := len(emails)
			if prefetchCount > 5 {
				prefetchCount = 5
			}
			go m.inboxManager.PrefetchEmailBodies(emails[:prefetchCount], 2)
		}

		return inboxLoadedMsg(emails)
	}
}

func (m Model) inboxViewingView() string {
	var s strings.Builder

	if len(m.inboxEmails) == 0 || m.selectedEmail >= len(m.inboxEmails) {
		s.WriteString(errorStyle.Render("No email selected"))
		s.WriteString("\n\n")
		s.WriteString(commentStyle.Render("Press 'q' or Esc to return to inbox"))
		return paddedStyle.Render(s.String())
	}

	email := m.inboxEmails[m.selectedEmail]

	s.WriteString(activeLabelStyle.Render(fmt.Sprintf("📧 %s", email.Subject)))
	s.WriteString("\n\n")

	s.WriteString(labelStyle.Render("From: ") + textStyle.Render(email.From))
	s.WriteString("\n")
	s.WriteString(labelStyle.Render("Date: ") + textStyle.Render(email.Date.Format("2006-01-02 15:04:05")))
	s.WriteString("\n")
	s.WriteString(labelStyle.Render("Size: ") + textStyle.Render(fmt.Sprintf("%d bytes", email.Size)))
	s.WriteString("\n\n")

	body, err := m.inboxManager.FetchEmailBody(email.UID)
	if err != nil {
		wrappedError := wrapTextStyle("Error loading email body: "+err.Error(), m.terminalWidth, errorStyle)
		s.WriteString(wrappedError)
	} else {

		wrappedBody := wrapTextStyle(body, m.terminalWidth, textStyle)
		s.WriteString(wrappedBody)
	}

	s.WriteString("\n\n")
	s.WriteString(commentStyle.Render("Press 'q' or Esc to return to inbox"))

	return paddedStyle.Render(s.String())
}

func (m Model) getHelpView() string {
	switch m.state {
	case StateInbox:

		inboxKeymap := InboxKeyMap{keymap: m.keymap}
		return m.help.View(inboxKeymap)
	default:
		return m.help.View(m.keymap)
	}
}

type InboxKeyMap struct {
	keymap KeyMap
}

func (k InboxKeyMap) ShortHelp() []key.Binding {
	return k.keymap.InboxShortHelp()
}

func (k InboxKeyMap) FullHelp() [][]key.Binding {
	return k.keymap.InboxFullHelp()
}
