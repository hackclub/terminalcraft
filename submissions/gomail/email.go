package main

import (
	"bytes"
	"crypto/tls"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/resendlabs/resend-go"
	mail "github.com/xhit/go-simple-mail/v2"
	"github.com/yuin/goldmark"
	"github.com/yuin/goldmark/extension"
	renderer "github.com/yuin/goldmark/renderer/html"
)

const ToSeparator = ","

type sendEmailSuccessMsg struct{}

type sendEmailFailureMsg error

func (m Model) sendEmailCmd() tea.Cmd {
	return func() tea.Msg {
		attachmentPaths := make([]string, len(m.Attachments.Items()))
		for i, attachment := range m.Attachments.Items() {
			attachmentPaths[i] = attachment.FilterValue()
		}

		recipients := parseEmailList(m.To.Value())
		ccRecipients := parseEmailList(m.Cc.Value())
		bccRecipients := parseEmailList(m.Bcc.Value())

		sentEmail := SentEmail{
			From:        m.From.Value(),
			To:          m.To.Value(),
			Cc:          m.Cc.Value(),
			Bcc:         m.Bcc.Value(),
			Subject:     m.Subject.Value(),
			Body:        m.Body.Value(),
			Attachments: strings.Join(attachmentPaths, ";"),
			SentAt:      time.Now(),
		}

		var err error
		switch m.DeliveryMethod {
		case DeliveryMethodSMTP:
			sentEmail.Method = "smtp"
			err = sendSMTPEmail(recipients, ccRecipients, bccRecipients, m.From.Value(), m.Subject.Value(), m.Body.Value(), attachmentPaths)
		case DeliveryMethodResend:
			sentEmail.Method = "resend"
			err = sendResendEmail(recipients, ccRecipients, bccRecipients, m.From.Value(), m.Subject.Value(), m.Body.Value(), attachmentPaths)
		case DeliveryMethodNone:
			err = errors.New("no email delivery method configured - please configure either RESEND_API_KEY or SMTP settings")
		default:
			err = errors.New("unsupported delivery method")
		}

		if db, dbErr := NewDatabaseManager(); dbErr == nil {
			defer db.Close()

			if err != nil {
				sentEmail.Status = "failed"
				sentEmail.ErrorMessage = err.Error()
			} else {
				sentEmail.Status = "sent"
			}

			if saveErr := db.SaveSentEmail(sentEmail); saveErr != nil {

				fmt.Fprintf(os.Stderr, "Warning: Failed to save email record: %v\n", saveErr)
			}
		}

		if err != nil {
			if path, storeErr := saveEmailBackup(m.Body.Value()); storeErr == nil {
				err = fmt.Errorf("%w\nEmail backup saved to: %s", err, path)
			}
			return sendEmailFailureMsg(err)
		}
		return sendEmailSuccessMsg{}
	}
}

func parseEmailList(emailStr string) []string {
	if emailStr == "" {
		return nil
	}
	emails := strings.Split(emailStr, ToSeparator)
	result := make([]string, 0, len(emails))
	for _, email := range emails {
		if trimmed := strings.TrimSpace(email); trimmed != "" {
			result = append(result, trimmed)
		}
	}
	return result
}

const (
	gmailSuffix    = "@gmail.com"
	gmailSMTPHost  = "smtp.gmail.com"
	gmailSMTPPort  = 587
	defaultTimeout = 10 * time.Second
)

func sendSMTPEmail(to, cc, bcc []string, from, subject, body string, attachmentPaths []string) error {
	server := mail.NewSMTPClient()

	server.Username = smtpUsername
	server.Password = smtpPassword
	server.Host = smtpHost
	server.Port = smtpPort

	if strings.HasSuffix(server.Username, gmailSuffix) {
		if server.Port == 0 {
			server.Port = gmailSMTPPort
		}
		if server.Host == "" {
			server.Host = gmailSMTPHost
		}
	}

	switch strings.ToLower(smtpEncryption) {
	case "ssl":
		server.Encryption = mail.EncryptionSSLTLS
	case "none":
		server.Encryption = mail.EncryptionNone
	default:
		server.Encryption = mail.EncryptionSTARTTLS
	}

	server.KeepAlive = false
	server.ConnectTimeout = defaultTimeout
	server.SendTimeout = defaultTimeout
	server.TLSConfig = &tls.Config{
		InsecureSkipVerify: smtpInsecureSkipVerify,
		ServerName:         server.Host,
	}

	smtpClient, err := server.Connect()
	if err != nil {
		return fmt.Errorf("connecting to SMTP server: %w", err)
	}

	email := mail.NewMSG()
	email.SetFrom(from).
		AddTo(to...).
		AddCc(cc...).
		AddBcc(bcc...).
		SetSubject(subject)

	htmlBuffer := bytes.NewBufferString("")
	if err := goldmark.Convert([]byte(body), htmlBuffer); err != nil {
		email.SetBody(mail.TextPlain, body)
	} else {
		email.SetBody(mail.TextHTML, htmlBuffer.String())
	}

	for _, attachmentPath := range attachmentPaths {
		email.Attach(&mail.File{
			FilePath: attachmentPath,
			Name:     filepath.Base(attachmentPath),
		})
	}

	if err := email.Send(smtpClient); err != nil {
		return fmt.Errorf("sending email via SMTP: %w", err)
	}

	return nil
}

func sendResendEmail(to, cc, bcc []string, from, subject, body string, attachmentPaths []string) error {
	client := resend.NewClient(resendAPIKey)

	htmlBuffer := bytes.NewBufferString("")

	var markdown goldmark.Markdown
	if unsafe {
		markdown = goldmark.New(
			goldmark.WithRendererOptions(renderer.WithUnsafe()),
			goldmark.WithExtensions(
				extension.Strikethrough,
				extension.Table,
				extension.Linkify,
			),
		)
	} else {
		markdown = goldmark.New()
	}

	_ = markdown.Convert([]byte(body), htmlBuffer)

	request := &resend.SendEmailRequest{
		From:        from,
		To:          to,
		Subject:     subject,
		Cc:          cc,
		Bcc:         bcc,
		Html:        htmlBuffer.String(),
		Text:        body,
		Attachments: createResendAttachments(attachmentPaths),
	}

	if _, err := client.Emails.Send(request); err != nil {
		return fmt.Errorf("sending email via Resend: %w", err)
	}

	return nil
}

func createResendAttachments(paths []string) []resend.Attachment {
	if len(paths) == 0 {
		return nil
	}

	attachments := make([]resend.Attachment, 0, len(paths))
	for _, path := range paths {
		content, err := os.ReadFile(path)
		if err != nil {

			continue
		}
		attachments = append(attachments, resend.Attachment{
			Content:  string(content),
			Filename: filepath.Base(path),
		})
	}

	return attachments
}

func saveEmailBackup(content string) (string, error) {
	tempFile, err := os.CreateTemp("", fmt.Sprintf("gomail-backup-%s-*.txt", time.Now().Format("2006-01-02")))
	if err != nil {
		return "", fmt.Errorf("creating backup file: %w", err)
	}
	defer tempFile.Close()

	if _, err = tempFile.WriteString(content); err != nil {
		return "", fmt.Errorf("writing to backup file %s: %w", tempFile.Name(), err)
	}

	return tempFile.Name(), nil
}
