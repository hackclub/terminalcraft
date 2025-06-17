package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/charmbracelet/bubbles/help"
	"github.com/charmbracelet/bubbles/key"
	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
)

type SetupState int

const (
	SetupStateWelcome SetupState = iota
	SetupStateDeliveryMethod
	SetupStateResendKey
	SetupStateSMTPHost
	SetupStateSMTPPort
	SetupStateSMTPUsername
	SetupStateSMTPPassword
	SetupStateSMTPEncryption
	SetupStateFromAddress
	SetupStateIMAPHost
	SetupStateIMAPPort
	SetupStateIMAPUsername
	SetupStateIMAPPassword
	SetupStateIMAPEncryption
	SetupStateComplete
)

type Config struct {
	DeliveryMethod string `json:"delivery_method"`
	ResendAPIKey   string `json:"resend_api_key,omitempty"`
	SMTPHost       string `json:"smtp_host,omitempty"`
	SMTPPort       int    `json:"smtp_port,omitempty"`
	SMTPUsername   string `json:"smtp_username,omitempty"`
	SMTPPassword   string `json:"smtp_password,omitempty"`
	SMTPEncryption string `json:"smtp_encryption,omitempty"`
	FromAddress    string `json:"from_address,omitempty"`

	IMAPHost       string `json:"imap_host,omitempty"`
	IMAPPort       int    `json:"imap_port,omitempty"`
	IMAPUsername   string `json:"imap_username,omitempty"`
	IMAPPassword   string `json:"imap_password,omitempty"`
	IMAPEncryption string `json:"imap_encryption,omitempty"`
}

type SetupModel struct {
	state          SetupState
	config         Config
	selectedMethod int

	resendKeyInput    textinput.Model
	smtpHostInput     textinput.Model
	smtpPortInput     textinput.Model
	smtpUsernameInput textinput.Model
	smtpPasswordInput textinput.Model
	smtpEncryptInput  textinput.Model
	fromAddressInput  textinput.Model
	imapHostInput     textinput.Model
	imapPortInput     textinput.Model
	imapUsernameInput textinput.Model
	imapPasswordInput textinput.Model
	imapEncryptInput  textinput.Model

	help     help.Model
	keymap   SetupKeyMap
	err      error
	quitting bool
}

type SetupKeyMap struct {
	Up    key.Binding
	Down  key.Binding
	Enter key.Binding
	Back  key.Binding
	Quit  key.Binding
}

func DefaultSetupKeybinds() SetupKeyMap {
	return SetupKeyMap{
		Up: key.NewBinding(
			key.WithKeys("up", "ctrl+k"),
			key.WithHelp("↑/ctrl+k", "up"),
		),
		Down: key.NewBinding(
			key.WithKeys("down", "ctrl+j"),
			key.WithHelp("↓/ctrl+j", "down"),
		),
		Enter: key.NewBinding(
			key.WithKeys("enter"),
			key.WithHelp("enter", "select/continue"),
		),
		Back: key.NewBinding(
			key.WithKeys("esc"),
			key.WithHelp("esc", "back"),
		),
		Quit: key.NewBinding(
			key.WithKeys("ctrl+c"),
			key.WithHelp("ctrl+c", "quit"),
		),
	}
}

func (k SetupKeyMap) ShortHelp() []key.Binding {
	return []key.Binding{k.Up, k.Down, k.Enter, k.Back, k.Quit}
}

func (k SetupKeyMap) FullHelp() [][]key.Binding {
	return [][]key.Binding{
		{k.Up, k.Down, k.Enter, k.Back, k.Quit},
	}
}

func NewSetupModel() SetupModel {

	resendKeyInput := textinput.New()
	resendKeyInput.Placeholder = "re_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
	resendKeyInput.PromptStyle = labelStyle
	resendKeyInput.TextStyle = textStyle
	resendKeyInput.Cursor.Style = cursorStyle
	resendKeyInput.PlaceholderStyle = placeholderStyle
	resendKeyInput.EchoMode = textinput.EchoPassword
	resendKeyInput.EchoCharacter = '*'

	smtpHostInput := textinput.New()
	smtpHostInput.Placeholder = "smtp.gmail.com"
	smtpHostInput.PromptStyle = labelStyle
	smtpHostInput.TextStyle = textStyle
	smtpHostInput.Cursor.Style = cursorStyle
	smtpHostInput.PlaceholderStyle = placeholderStyle

	smtpPortInput := textinput.New()
	smtpPortInput.Placeholder = "587"
	smtpPortInput.PromptStyle = labelStyle
	smtpPortInput.TextStyle = textStyle
	smtpPortInput.Cursor.Style = cursorStyle
	smtpPortInput.PlaceholderStyle = placeholderStyle

	smtpUsernameInput := textinput.New()
	smtpUsernameInput.Placeholder = "your-email@gmail.com"
	smtpUsernameInput.PromptStyle = labelStyle
	smtpUsernameInput.TextStyle = textStyle
	smtpUsernameInput.Cursor.Style = cursorStyle
	smtpUsernameInput.PlaceholderStyle = placeholderStyle

	smtpPasswordInput := textinput.New()
	smtpPasswordInput.Placeholder = "your-app-password"
	smtpPasswordInput.PromptStyle = labelStyle
	smtpPasswordInput.TextStyle = textStyle
	smtpPasswordInput.Cursor.Style = cursorStyle
	smtpPasswordInput.PlaceholderStyle = placeholderStyle
	smtpPasswordInput.EchoMode = textinput.EchoPassword
	smtpPasswordInput.EchoCharacter = '*'

	smtpEncryptInput := textinput.New()
	smtpEncryptInput.Placeholder = "starttls"
	smtpEncryptInput.PromptStyle = labelStyle
	smtpEncryptInput.TextStyle = textStyle
	smtpEncryptInput.Cursor.Style = cursorStyle
	smtpEncryptInput.PlaceholderStyle = placeholderStyle
	smtpEncryptInput.SetValue("starttls")

	fromAddressInput := textinput.New()
	fromAddressInput.Placeholder = "your-email@example.com"
	fromAddressInput.PromptStyle = labelStyle
	fromAddressInput.TextStyle = textStyle
	fromAddressInput.Cursor.Style = cursorStyle
	fromAddressInput.PlaceholderStyle = placeholderStyle

	imapHostInput := textinput.New()
	imapHostInput.Placeholder = "imap.gmail.com"
	imapHostInput.PromptStyle = labelStyle
	imapHostInput.TextStyle = textStyle
	imapHostInput.Cursor.Style = cursorStyle
	imapHostInput.PlaceholderStyle = placeholderStyle

	imapPortInput := textinput.New()
	imapPortInput.Placeholder = "993"
	imapPortInput.PromptStyle = labelStyle
	imapPortInput.TextStyle = textStyle
	imapPortInput.Cursor.Style = cursorStyle
	imapPortInput.PlaceholderStyle = placeholderStyle

	imapUsernameInput := textinput.New()
	imapUsernameInput.Placeholder = "your-email@gmail.com"
	imapUsernameInput.PromptStyle = labelStyle
	imapUsernameInput.TextStyle = textStyle
	imapUsernameInput.Cursor.Style = cursorStyle
	imapUsernameInput.PlaceholderStyle = placeholderStyle

	imapPasswordInput := textinput.New()
	imapPasswordInput.Placeholder = "your-password"
	imapPasswordInput.PromptStyle = labelStyle
	imapPasswordInput.TextStyle = textStyle
	imapPasswordInput.Cursor.Style = cursorStyle
	imapPasswordInput.PlaceholderStyle = placeholderStyle
	imapPasswordInput.EchoMode = textinput.EchoPassword
	imapPasswordInput.EchoCharacter = '*'

	imapEncryptInput := textinput.New()
	imapEncryptInput.Placeholder = "ssl"
	imapEncryptInput.PromptStyle = labelStyle
	imapEncryptInput.TextStyle = textStyle
	imapEncryptInput.Cursor.Style = cursorStyle
	imapEncryptInput.PlaceholderStyle = placeholderStyle
	imapEncryptInput.SetValue("ssl")

	return SetupModel{
		state:             SetupStateWelcome,
		selectedMethod:    0,
		resendKeyInput:    resendKeyInput,
		smtpHostInput:     smtpHostInput,
		smtpPortInput:     smtpPortInput,
		smtpUsernameInput: smtpUsernameInput,
		smtpPasswordInput: smtpPasswordInput,
		smtpEncryptInput:  smtpEncryptInput,
		fromAddressInput:  fromAddressInput,
		imapHostInput:     imapHostInput,
		imapPortInput:     imapPortInput,
		imapUsernameInput: imapUsernameInput,
		imapPasswordInput: imapPasswordInput,
		imapEncryptInput:  imapEncryptInput,
		help:              help.New(),
		keymap:            DefaultSetupKeybinds(),
	}
}

func (m SetupModel) Init() tea.Cmd {
	return nil
}

func (m SetupModel) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch {
		case key.Matches(msg, m.keymap.Quit):
			m.quitting = true
			return m, tea.Quit
		case key.Matches(msg, m.keymap.Back):
			return m.goBack(), nil
		case key.Matches(msg, m.keymap.Enter):
			return m.handleEnter()
		case key.Matches(msg, m.keymap.Up):
			if m.state == SetupStateDeliveryMethod {
				m.selectedMethod = 0
			}
		case key.Matches(msg, m.keymap.Down):
			if m.state == SetupStateDeliveryMethod {
				m.selectedMethod = 1
			}
		}
	}

	var cmd tea.Cmd
	switch m.state {
	case SetupStateResendKey:
		m.resendKeyInput, cmd = m.resendKeyInput.Update(msg)
	case SetupStateSMTPHost:
		m.smtpHostInput, cmd = m.smtpHostInput.Update(msg)
	case SetupStateSMTPPort:
		m.smtpPortInput, cmd = m.smtpPortInput.Update(msg)
	case SetupStateSMTPUsername:
		m.smtpUsernameInput, cmd = m.smtpUsernameInput.Update(msg)
	case SetupStateSMTPPassword:
		m.smtpPasswordInput, cmd = m.smtpPasswordInput.Update(msg)
	case SetupStateSMTPEncryption:
		m.smtpEncryptInput, cmd = m.smtpEncryptInput.Update(msg)
	case SetupStateFromAddress:
		m.fromAddressInput, cmd = m.fromAddressInput.Update(msg)
	case SetupStateIMAPHost:
		m.imapHostInput, cmd = m.imapHostInput.Update(msg)
	case SetupStateIMAPPort:
		m.imapPortInput, cmd = m.imapPortInput.Update(msg)
	case SetupStateIMAPUsername:
		m.imapUsernameInput, cmd = m.imapUsernameInput.Update(msg)
	case SetupStateIMAPPassword:
		m.imapPasswordInput, cmd = m.imapPasswordInput.Update(msg)
	case SetupStateIMAPEncryption:
		m.imapEncryptInput, cmd = m.imapEncryptInput.Update(msg)
	}

	return m, cmd
}

func (m *SetupModel) autoDetectSMTPSettings(email string) {
	domain := strings.ToLower(strings.Split(email, "@")[1])

	switch domain {
	case "gmail.com", "googlemail.com":
		if m.smtpHostInput.Value() == "" {
			m.smtpHostInput.SetValue("smtp.gmail.com")
			m.config.SMTPHost = "smtp.gmail.com"
		}
		if m.smtpPortInput.Value() == "" {
			m.smtpPortInput.SetValue("587")
			m.config.SMTPPort = 587
		}
		if m.smtpEncryptInput.Value() == "" || m.smtpEncryptInput.Value() == "starttls" {
			m.smtpEncryptInput.SetValue("starttls")
			m.config.SMTPEncryption = "starttls"
		}
	case "outlook.com", "hotmail.com", "live.com", "msn.com":
		if m.smtpHostInput.Value() == "" {
			m.smtpHostInput.SetValue("smtp-mail.outlook.com")
			m.config.SMTPHost = "smtp-mail.outlook.com"
		}
		if m.smtpPortInput.Value() == "" {
			m.smtpPortInput.SetValue("587")
			m.config.SMTPPort = 587
		}
		if m.smtpEncryptInput.Value() == "" || m.smtpEncryptInput.Value() == "starttls" {
			m.smtpEncryptInput.SetValue("starttls")
			m.config.SMTPEncryption = "starttls"
		}
	case "yahoo.com", "ymail.com", "rocketmail.com":
		if m.smtpHostInput.Value() == "" {
			m.smtpHostInput.SetValue("smtp.mail.yahoo.com")
			m.config.SMTPHost = "smtp.mail.yahoo.com"
		}
		if m.smtpPortInput.Value() == "" {
			m.smtpPortInput.SetValue("587")
			m.config.SMTPPort = 587
		}
		if m.smtpEncryptInput.Value() == "" || m.smtpEncryptInput.Value() == "starttls" {
			m.smtpEncryptInput.SetValue("starttls")
			m.config.SMTPEncryption = "starttls"
		}
	case "icloud.com", "me.com", "mac.com":
		if m.smtpHostInput.Value() == "" {
			m.smtpHostInput.SetValue("smtp.mail.me.com")
			m.config.SMTPHost = "smtp.mail.me.com"
		}
		if m.smtpPortInput.Value() == "" {
			m.smtpPortInput.SetValue("587")
			m.config.SMTPPort = 587
		}
		if m.smtpEncryptInput.Value() == "" || m.smtpEncryptInput.Value() == "starttls" {
			m.smtpEncryptInput.SetValue("starttls")
			m.config.SMTPEncryption = "starttls"
		}
	}
}

func (m *SetupModel) autoDetectIMAPSettings(email string) {
	domain := strings.ToLower(strings.Split(email, "@")[1])

	switch domain {
	case "gmail.com", "googlemail.com":
		if m.imapHostInput.Value() == "" {
			m.imapHostInput.SetValue("imap.gmail.com")
			m.config.IMAPHost = "imap.gmail.com"
		}
		if m.imapPortInput.Value() == "" {
			m.imapPortInput.SetValue("993")
			m.config.IMAPPort = 993
		}
		if m.imapEncryptInput.Value() == "" || m.imapEncryptInput.Value() == "ssl" {
			m.imapEncryptInput.SetValue("ssl")
			m.config.IMAPEncryption = "ssl"
		}
	case "outlook.com", "hotmail.com", "live.com", "msn.com":
		if m.imapHostInput.Value() == "" {
			m.imapHostInput.SetValue("outlook.office365.com")
			m.config.IMAPHost = "outlook.office365.com"
		}
		if m.imapPortInput.Value() == "" {
			m.imapPortInput.SetValue("993")
			m.config.IMAPPort = 993
		}
		if m.imapEncryptInput.Value() == "" || m.imapEncryptInput.Value() == "ssl" {
			m.imapEncryptInput.SetValue("ssl")
			m.config.IMAPEncryption = "ssl"
		}
	case "yahoo.com", "ymail.com", "rocketmail.com":
		if m.imapHostInput.Value() == "" {
			m.imapHostInput.SetValue("imap.mail.yahoo.com")
			m.config.IMAPHost = "imap.mail.yahoo.com"
		}
		if m.imapPortInput.Value() == "" {
			m.imapPortInput.SetValue("993")
			m.config.IMAPPort = 993
		}
		if m.imapEncryptInput.Value() == "" || m.imapEncryptInput.Value() == "ssl" {
			m.imapEncryptInput.SetValue("ssl")
			m.config.IMAPEncryption = "ssl"
		}
	case "icloud.com", "me.com", "mac.com":
		if m.imapHostInput.Value() == "" {
			m.imapHostInput.SetValue("imap.mail.me.com")
			m.config.IMAPHost = "imap.mail.me.com"
		}
		if m.imapPortInput.Value() == "" {
			m.imapPortInput.SetValue("993")
			m.config.IMAPPort = 993
		}
		if m.imapEncryptInput.Value() == "" || m.imapEncryptInput.Value() == "ssl" {
			m.imapEncryptInput.SetValue("ssl")
			m.config.IMAPEncryption = "ssl"
		}
	}
}

func (m SetupModel) goBack() SetupModel {

	m.err = nil

	switch m.state {
	case SetupStateWelcome:
		m.quitting = true
	case SetupStateDeliveryMethod:
		m.state = SetupStateWelcome
	case SetupStateResendKey:
		m.state = SetupStateDeliveryMethod
	case SetupStateSMTPHost:
		m.state = SetupStateDeliveryMethod
	case SetupStateSMTPPort:
		m.state = SetupStateSMTPHost
	case SetupStateSMTPUsername:
		m.state = SetupStateSMTPPort
	case SetupStateSMTPPassword:
		m.state = SetupStateSMTPUsername
	case SetupStateSMTPEncryption:
		m.state = SetupStateSMTPPassword
	case SetupStateFromAddress:
		if m.config.DeliveryMethod == "resend" {
			m.state = SetupStateResendKey
		} else {
			m.state = SetupStateSMTPEncryption
		}
	case SetupStateIMAPHost:
		m.state = SetupStateFromAddress
	case SetupStateIMAPPort:
		m.state = SetupStateIMAPHost
	case SetupStateIMAPUsername:
		m.state = SetupStateIMAPPort
	case SetupStateIMAPPassword:
		m.state = SetupStateIMAPUsername
	case SetupStateIMAPEncryption:
		m.state = SetupStateIMAPPassword
	case SetupStateComplete:
		if m.config.DeliveryMethod == "smtp" {
			m.state = SetupStateIMAPEncryption
		} else {
			m.state = SetupStateFromAddress
		}
	}
	return m
}

func (m SetupModel) handleEnter() (SetupModel, tea.Cmd) {
	switch m.state {
	case SetupStateWelcome:
		m.state = SetupStateDeliveryMethod
	case SetupStateDeliveryMethod:
		if m.selectedMethod == 0 {
			m.state = SetupStateResendKey
			m.resendKeyInput.Focus()
		} else {
			m.state = SetupStateSMTPHost
			m.smtpHostInput.Focus()
		}
	case SetupStateResendKey:
		apiKey := strings.TrimSpace(m.resendKeyInput.Value())
		if apiKey == "" {
			m.err = fmt.Errorf("Please enter your Resend API key")
			return m, nil
		}

		if !strings.HasPrefix(apiKey, "re_") {
			m.err = fmt.Errorf("Resend API key should start with 're_'")
			return m, nil
		}

		m.config.ResendAPIKey = apiKey
		m.config.DeliveryMethod = "resend"
		m.err = nil
		m.state = SetupStateFromAddress
		m.fromAddressInput.Focus()
	case SetupStateSMTPHost:
		host := strings.TrimSpace(m.smtpHostInput.Value())
		if host == "" {
			m.err = fmt.Errorf("Please enter the SMTP host")
			return m, nil
		}

		m.config.SMTPHost = host
		m.err = nil
		m.state = SetupStateSMTPPort
		m.smtpPortInput.Focus()
	case SetupStateSMTPPort:
		portStr := strings.TrimSpace(m.smtpPortInput.Value())
		port := 587

		if portStr != "" {
			if _, err := fmt.Sscanf(portStr, "%d", &port); err != nil {
				m.err = fmt.Errorf("Please enter a valid port number")
				return m, nil
			}
		}

		m.config.SMTPPort = port
		m.err = nil
		m.state = SetupStateSMTPUsername
		m.smtpUsernameInput.Focus()
	case SetupStateSMTPUsername:
		username := strings.TrimSpace(m.smtpUsernameInput.Value())
		if username == "" {
			m.err = fmt.Errorf("Please enter your email address")
			return m, nil
		}

		if !strings.Contains(username, "@") {
			m.err = fmt.Errorf("Please enter your full email address")
			return m, nil
		}

		m.config.SMTPUsername = username
		m.err = nil
		m.autoDetectSMTPSettings(username)
		m.state = SetupStateSMTPPassword
		m.smtpPasswordInput.Focus()
	case SetupStateSMTPPassword:
		password := strings.TrimSpace(m.smtpPasswordInput.Value())
		if password == "" {
			m.err = fmt.Errorf("Please enter your password")
			return m, nil
		}

		m.config.SMTPPassword = password
		m.err = nil
		m.state = SetupStateSMTPEncryption
		m.smtpEncryptInput.Focus()
	case SetupStateSMTPEncryption:
		encryption := strings.TrimSpace(m.smtpEncryptInput.Value())
		if encryption == "" {
			encryption = "starttls"
		}

		validEncryptions := []string{"starttls", "ssl", "tls", "none"}
		isValid := false
		for _, valid := range validEncryptions {
			if strings.ToLower(encryption) == valid {
				isValid = true
				break
			}
		}

		if !isValid {
			m.err = fmt.Errorf("Please enter a valid encryption method: starttls, ssl, tls, or none")
			return m, nil
		}

		m.config.SMTPEncryption = strings.ToLower(encryption)
		m.config.DeliveryMethod = "smtp"
		m.err = nil
		m.state = SetupStateFromAddress

		if m.config.SMTPUsername != "" && m.fromAddressInput.Value() == "" {
			m.fromAddressInput.SetValue(m.config.SMTPUsername)
		}

		m.fromAddressInput.Focus()
	case SetupStateFromAddress:
		fromAddr := strings.TrimSpace(m.fromAddressInput.Value())

		if fromAddr == "" && m.config.DeliveryMethod == "smtp" && m.config.SMTPUsername != "" {
			fromAddr = m.config.SMTPUsername
			m.fromAddressInput.SetValue(fromAddr)
		}

		if fromAddr == "" {
			m.err = fmt.Errorf("please enter a from address")
			return m, nil
		}

		if !strings.Contains(fromAddr, "@") || !strings.Contains(fromAddr, ".") {
			m.err = fmt.Errorf("please enter a valid email address")
			return m, nil
		}

		m.config.FromAddress = fromAddr
		m.err = nil

		if m.config.DeliveryMethod == "smtp" {
			m.fromAddressInput.Blur()

			if m.config.SMTPUsername != "" {
				m.autoDetectIMAPSettings(m.config.SMTPUsername)
			}
			m.state = SetupStateIMAPHost
			m.imapHostInput.Focus()
		} else {

			if err := saveTOMLConfigFromSetup(m.config); err != nil {
				m.err = err
			} else {
				m.state = SetupStateComplete
			}
		}
	case SetupStateIMAPHost:
		host := strings.TrimSpace(m.imapHostInput.Value())
		if host == "" {
			m.err = fmt.Errorf("Please enter the IMAP host")
			return m, nil
		}

		m.config.IMAPHost = host
		m.err = nil
		m.state = SetupStateIMAPPort
		m.imapPortInput.Focus()
	case SetupStateIMAPPort:
		portStr := strings.TrimSpace(m.imapPortInput.Value())
		port := 993

		if portStr != "" {
			if _, err := fmt.Sscanf(portStr, "%d", &port); err != nil {
				m.err = fmt.Errorf("Please enter a valid port number")
				return m, nil
			}
		}

		m.config.IMAPPort = port
		m.err = nil
		m.state = SetupStateIMAPUsername
		m.imapUsernameInput.Focus()
	case SetupStateIMAPUsername:
		username := strings.TrimSpace(m.imapUsernameInput.Value())
		if username == "" {

			if m.config.SMTPUsername != "" {
				username = m.config.SMTPUsername
				m.imapUsernameInput.SetValue(username)
			} else {
				m.err = fmt.Errorf("Please enter IMAP username")
				return m, nil
			}
		}

		m.config.IMAPUsername = username
		m.err = nil
		m.state = SetupStateIMAPPassword
		m.imapPasswordInput.Focus()
	case SetupStateIMAPPassword:
		password := strings.TrimSpace(m.imapPasswordInput.Value())
		if password == "" {

			if m.config.SMTPPassword != "" {
				password = m.config.SMTPPassword
				m.imapPasswordInput.SetValue(password)
			} else {
				m.err = fmt.Errorf("Please enter IMAP password")
				return m, nil
			}
		}

		m.config.IMAPPassword = password
		m.err = nil
		m.state = SetupStateIMAPEncryption
		m.imapEncryptInput.Focus()
	case SetupStateIMAPEncryption:
		encryption := strings.TrimSpace(m.imapEncryptInput.Value())
		if encryption == "" {
			encryption = "ssl"
		}

		validEncryptions := []string{"ssl", "starttls", "tls", "none"}
		isValid := false
		for _, valid := range validEncryptions {
			if strings.ToLower(encryption) == valid {
				isValid = true
				break
			}
		}

		if !isValid {
			m.err = fmt.Errorf("Please enter a valid encryption method: ssl, starttls, tls, or none")
			return m, nil
		}

		m.config.IMAPEncryption = strings.ToLower(encryption)
		m.err = nil

		if err := saveTOMLConfigFromSetup(m.config); err != nil {
			m.err = err
		} else {
			m.state = SetupStateComplete
		}
	case SetupStateComplete:
		m.quitting = true
		return m, tea.Quit
	}
	return m, nil
}

func (m SetupModel) View() string {
	if m.quitting {
		return ""
	}

	var s strings.Builder

	switch m.state {
	case SetupStateWelcome:
		s.WriteString(m.renderWelcome())
	case SetupStateDeliveryMethod:
		s.WriteString(m.renderDeliveryMethod())
	case SetupStateResendKey:
		s.WriteString(m.renderResendKey())
	case SetupStateSMTPHost:
		s.WriteString(m.renderSMTPHost())
	case SetupStateSMTPPort:
		s.WriteString(m.renderSMTPPort())
	case SetupStateSMTPUsername:
		s.WriteString(m.renderSMTPUsername())
	case SetupStateSMTPPassword:
		s.WriteString(m.renderSMTPPassword())
	case SetupStateSMTPEncryption:
		s.WriteString(m.renderSMTPEncryption())
	case SetupStateFromAddress:
		s.WriteString(m.renderFromAddress())
	case SetupStateIMAPHost:
		s.WriteString(m.renderIMAPHost())
	case SetupStateIMAPPort:
		s.WriteString(m.renderIMAPPort())
	case SetupStateIMAPUsername:
		s.WriteString(m.renderIMAPUsername())
	case SetupStateIMAPPassword:
		s.WriteString(m.renderIMAPPassword())
	case SetupStateIMAPEncryption:
		s.WriteString(m.renderIMAPEncryption())
	case SetupStateComplete:
		s.WriteString(m.renderComplete())
	}

	s.WriteString("\n\n")
	s.WriteString(m.help.View(m.keymap))

	if m.err != nil {
		s.WriteString("\n\n")
		s.WriteString(errorStyle.Render(m.err.Error()))
	}

	return paddedStyle.Render(s.String())
}

func (m SetupModel) renderWelcome() string {
	title := activeLabelStyle.Render("Welcome to GoMail Setup!")

	content := textStyle.Render(`
GoMail needs to be configured before you can send emails.
This wizard will help you set up your email delivery method.

You can choose between:
• Resend.com (recommended for developers)
• SMTP (works with Gmail, Outlook, etc.)

Press enter to continue or ctrl+c to exit.`)

	return title + "\n\n" + content
}

func (m SetupModel) renderDeliveryMethod() string {
	title := activeLabelStyle.Render("Choose Email Delivery Method")

	var options strings.Builder

	if m.selectedMethod == 0 {
		options.WriteString(activeTextStyle.Render("→ Resend.com"))
		options.WriteString(commentStyle.Render(" (API-based, fast and reliable)"))
	} else {
		options.WriteString(textStyle.Render("  Resend.com"))
		options.WriteString(commentStyle.Render(" (API-based, fast and reliable)"))
	}

	options.WriteString("\n")

	if m.selectedMethod == 1 {
		options.WriteString(activeTextStyle.Render("→ SMTP"))
		options.WriteString(commentStyle.Render(" (works with Gmail, Outlook, etc.)"))
	} else {
		options.WriteString(textStyle.Render("  SMTP"))
		options.WriteString(commentStyle.Render(" (works with Gmail, Outlook, etc.)"))
	}

	return title + "\n\n" + options.String()
}

func (m SetupModel) renderResendKey() string {
	title := activeLabelStyle.Render("Resend API Key")

	info := commentStyle.Render("Get your API key from: ") + linkStyle.Render("https://resend.com/api-keys")
	info += "\n" + commentStyle.Render("Your API key will be stored securely.")

	m.resendKeyInput.Prompt = "API Key: "

	return title + "\n\n" + info + "\n\n" + m.resendKeyInput.View()
}

func (m SetupModel) renderSMTPHost() string {
	title := activeLabelStyle.Render("SMTP Configuration - Server Host")

	info := commentStyle.Render("Enter your SMTP server hostname:")
	info += "\n" + commentStyle.Render("Gmail: smtp.gmail.com | Outlook: smtp-mail.outlook.com")

	m.smtpHostInput.Prompt = "SMTP Host: "

	return title + "\n\n" + info + "\n\n" + m.smtpHostInput.View()
}

func (m SetupModel) renderSMTPPort() string {
	title := activeLabelStyle.Render("SMTP Configuration - Port")

	info := commentStyle.Render("Enter SMTP port (usually 587 for STARTTLS or 465 for SSL)")

	m.smtpPortInput.Prompt = "SMTP Port: "

	return title + "\n\n" + info + "\n\n" + m.smtpPortInput.View()
}

func (m SetupModel) renderSMTPUsername() string {
	title := activeLabelStyle.Render("SMTP Configuration - Username")

	info := commentStyle.Render("Enter your full email address (this will be used for both SMTP and IMAP)")
	info += "\n" + commentStyle.Render("Example: yourname@gmail.com")

	if m.config.SMTPHost != "" {
		info += "\n\n" + commentStyle.Render("✓ SMTP settings auto-detected for: ") + textStyle.Render(m.config.SMTPHost)
	}

	m.smtpUsernameInput.Prompt = "Email Address: "

	return title + "\n\n" + info + "\n\n" + m.smtpUsernameInput.View()
}

func (m SetupModel) renderSMTPPassword() string {
	title := activeLabelStyle.Render("SMTP Configuration - Password")

	info := commentStyle.Render("For Gmail, use an App Password:")
	info += "\n" + linkStyle.Render("https://support.google.com/accounts/answer/185833")
	info += "\n" + commentStyle.Render("Your password will be stored securely.")

	m.smtpPasswordInput.Prompt = "Password: "

	return title + "\n\n" + info + "\n\n" + m.smtpPasswordInput.View()
}

func (m SetupModel) renderSMTPEncryption() string {
	title := activeLabelStyle.Render("SMTP Configuration - Encryption")

	info := commentStyle.Render("Encryption method (starttls, ssl, or none)")
	info += "\n" + commentStyle.Render("Recommended: starttls")

	m.smtpEncryptInput.Prompt = "Encryption: "

	return title + "\n\n" + info + "\n\n" + m.smtpEncryptInput.View()
}

func (m SetupModel) renderFromAddress() string {
	title := activeLabelStyle.Render("Default From Address")

	info := commentStyle.Render("This will be your default sender address")

	if m.config.DeliveryMethod == "smtp" && m.config.SMTPUsername != "" {
		suggestion := m.config.SMTPUsername
		info += "\n" + commentStyle.Render("Suggested: ") + textStyle.Render(suggestion)
	} else if m.config.DeliveryMethod == "resend" {

		info += "\n" + commentStyle.Render("Note: For Resend, make sure this email is verified in your Resend dashboard")
	}

	m.fromAddressInput.Prompt = "From Address: "

	return title + "\n\n" + info + "\n\n" + m.fromAddressInput.View()
}

func (m SetupModel) renderIMAPConfig() string {
	title := activeLabelStyle.Render("Configure IMAP for Inbox")

	info := textStyle.Render(`To view your inbox, GoMail needs IMAP settings.

For Gmail, Outlook, Yahoo, and other popular providers, we can auto-detect
the correct IMAP settings using your email address and password.

If auto-detection doesn't work, you can configure IMAP manually.`)

	options := "\n\n"
	if m.selectedMethod == 0 {
		options += activeTextStyle.Render("→ Auto-detect IMAP settings")
		options += commentStyle.Render(" (recommended for Gmail, Outlook, Yahoo)")
	} else {
		options += textStyle.Render("  Auto-detect IMAP settings")
	}

	options += "\n"
	if m.selectedMethod == 1 {
		options += activeTextStyle.Render("→ Manual configuration")
		options += commentStyle.Render(" (for custom or corporate email servers)")
	} else {
		options += textStyle.Render("  Manual configuration")
	}

	options += "\n"
	if m.selectedMethod == 2 {
		options += activeTextStyle.Render("→ Skip inbox configuration")
		options += commentStyle.Render(" (compose-only mode)")
	} else {
		options += textStyle.Render("  Skip inbox configuration")
	}

	navigation := "\n\n" + commentStyle.Render("Use ↑/↓ to select, Enter to confirm")

	return title + "\n\n" + info + options + navigation
}

func (m SetupModel) renderIMAPHost() string {
	title := activeLabelStyle.Render("IMAP Server Host")

	info := textStyle.Render("Enter the IMAP server hostname:")
	info += "\n" + commentStyle.Render("Gmail: imap.gmail.com | Outlook: outlook.office365.com")

	if m.config.IMAPHost != "" && m.imapHostInput.Value() == "" {
		info += "\n" + commentStyle.Render("Auto-detected: ") + textStyle.Render(m.config.IMAPHost)
		m.imapHostInput.SetValue(m.config.IMAPHost)
	}

	m.imapHostInput.Prompt = "IMAP Host: "

	return title + "\n\n" + info + "\n\n" + m.imapHostInput.View()
}

func (m SetupModel) renderIMAPPort() string {
	title := activeLabelStyle.Render("IMAP Server Port")

	info := textStyle.Render("Enter the IMAP server port:")
	info += "\n" + commentStyle.Render("Default: 993 for SSL, 143 for STARTTLS")

	if m.config.IMAPPort != 0 && m.imapPortInput.Value() == "" {
		portStr := fmt.Sprintf("%d", m.config.IMAPPort)
		info += "\n" + commentStyle.Render("Auto-detected: ") + textStyle.Render(portStr)
		m.imapPortInput.SetValue(portStr)
	}

	m.imapPortInput.Prompt = "IMAP Port: "

	return title + "\n\n" + info + "\n\n" + m.imapPortInput.View()
}

func (m SetupModel) renderIMAPUsername() string {
	title := activeLabelStyle.Render("IMAP Configuration - Username")

	info := commentStyle.Render("Enter your IMAP username (usually your full email address)")

	if m.config.SMTPUsername != "" && m.imapUsernameInput.Value() == "" {
		info += "\n" + commentStyle.Render("Suggested: ") + textStyle.Render(m.config.SMTPUsername)
		m.imapUsernameInput.SetValue(m.config.SMTPUsername)
	}

	m.imapUsernameInput.Prompt = "IMAP Username: "

	return title + "\n\n" + info + "\n\n" + m.imapUsernameInput.View()
}

func (m SetupModel) renderIMAPPassword() string {
	title := activeLabelStyle.Render("IMAP Configuration - Password")

	info := commentStyle.Render("Enter your IMAP password")
	info += "\n" + commentStyle.Render("For Gmail, use the same App Password as SMTP")

	if m.config.SMTPPassword != "" && m.imapPasswordInput.Value() == "" {
		info += "\n" + commentStyle.Render("Note: Using the same password as SMTP")
		m.imapPasswordInput.SetValue(m.config.SMTPPassword)
	}

	m.imapPasswordInput.Prompt = "IMAP Password: "

	return title + "\n\n" + info + "\n\n" + m.imapPasswordInput.View()
}

func (m SetupModel) renderIMAPEncryption() string {
	title := activeLabelStyle.Render("IMAP Encryption")

	info := textStyle.Render("Choose encryption method for IMAP connection:")
	info += "\n" + commentStyle.Render("Options: ssl, starttls, tls, none")

	if m.config.IMAPEncryption != "" && m.imapEncryptInput.Value() == "ssl" {
		info += "\n" + commentStyle.Render("Auto-detected: ") + textStyle.Render(m.config.IMAPEncryption)
		m.imapEncryptInput.SetValue(m.config.IMAPEncryption)
	}

	m.imapEncryptInput.Prompt = "Encryption: "

	return title + "\n\n" + info + "\n\n" + m.imapEncryptInput.View()
}

func (m SetupModel) renderComplete() string {
	title := activeLabelStyle.Render("Setup Complete!")

	var method string
	if m.config.DeliveryMethod == "resend" {
		method = "Resend.com"
	} else {
		method = "SMTP"
	}

	content := textStyle.Render(fmt.Sprintf(`Configuration saved successfully!

Delivery Method: %s
From Address: %s

You can now use GoMail to send emails.
Your configuration is stored in: %s

Press enter to exit.`, method, m.config.FromAddress, getTOMLConfigPath()))

	return title + "\n\n" + content
}

func saveTOMLConfigFromSetup(setupConfig Config) error {
	tomlConfig := &TOMLConfig{
		App: AppConfig{
			DefaultFrom: setupConfig.FromAddress,
			UnsafeHTML:  false,
		},
		Email: EmailConfig{
			DeliveryMethod: setupConfig.DeliveryMethod,
		},
		Storage: StorageConfig{
			RetentionDays:      30,
			CacheRetentionDays: 7,
			AutoSaveDrafts:     true,
			AutoSaveInterval:   30,
		},
		UI: UIConfig{
			Theme:       "auto",
			ShowCcBcc:   false,
			CompactMode: false,
		},
	}

	if setupConfig.DeliveryMethod == "resend" {
		tomlConfig.Email.Resend = ResendConfig{
			APIKey: setupConfig.ResendAPIKey,
		}
	} else if setupConfig.DeliveryMethod == "smtp" {
		tomlConfig.Email.SMTP = SMTPConfig{
			Host:       setupConfig.SMTPHost,
			Port:       setupConfig.SMTPPort,
			Username:   setupConfig.SMTPUsername,
			Password:   setupConfig.SMTPPassword,
			Encryption: setupConfig.SMTPEncryption,
		}

		if setupConfig.IMAPHost != "" {
			tomlConfig.Email.IMAP = IMAPConfig{
				Host:       setupConfig.IMAPHost,
				Port:       setupConfig.IMAPPort,
				Username:   setupConfig.IMAPUsername,
				Password:   setupConfig.IMAPPassword,
				Encryption: setupConfig.IMAPEncryption,
				AutoDetect: false,
			}
		} else {

			tomlConfig.Email.IMAP = IMAPConfig{
				AutoDetect: false,
			}
		}
	}

	return SaveTOMLConfig(tomlConfig)
}

func getConfigPath() string {
	configDir, _ := os.UserConfigDir()
	return filepath.Join(configDir, "gomail", "config.json")
}

func saveConfig(config Config) error {
	configPath := getConfigPath()
	configDir := filepath.Dir(configPath)

	if err := os.MkdirAll(configDir, 0755); err != nil {
		return fmt.Errorf("creating config directory: %w", err)
	}

	data, err := json.MarshalIndent(config, "", "  ")
	if err != nil {
		return fmt.Errorf("marshaling config: %w", err)
	}

	if err := os.WriteFile(configPath, data, 0600); err != nil {
		return fmt.Errorf("writing config file: %w", err)
	}

	return nil
}

func loadConfig() (*Config, error) {
	configPath := getConfigPath()

	data, err := os.ReadFile(configPath)
	if err != nil {
		if os.IsNotExist(err) {
			return nil, nil
		}
		return nil, fmt.Errorf("reading config file: %w", err)
	}

	var config Config
	if err := json.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("parsing config file: %w", err)
	}

	return &config, nil
}

func isConfigured() bool {
	config, err := loadConfig()
	if err != nil || config == nil {
		return false
	}

	switch config.DeliveryMethod {
	case "resend":
		return config.ResendAPIKey != "" && config.FromAddress != ""
	case "smtp":
		return config.SMTPHost != "" && config.SMTPUsername != "" &&
			config.SMTPPassword != "" && config.FromAddress != ""
	default:
		return false
	}
}

func applyConfig(config *Config) {
	if config == nil {
		return
	}

	switch config.DeliveryMethod {
	case "resend":
		resendAPIKey = config.ResendAPIKey
	case "smtp":
		smtpHost = config.SMTPHost
		smtpPort = config.SMTPPort
		smtpUsername = config.SMTPUsername
		smtpPassword = config.SMTPPassword
		smtpEncryption = config.SMTPEncryption
	}

	if from == "" && config.FromAddress != "" {
		from = config.FromAddress
	}
}
