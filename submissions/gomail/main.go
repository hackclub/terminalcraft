package main

import (
	"errors"
	"fmt"
	"io"
	"os"
	"runtime/debug"
	"strconv"
	"strings"

	tea "github.com/charmbracelet/bubbletea"
	mcobra "github.com/muesli/mango-cobra"
	"github.com/muesli/roff"
	"github.com/resendlabs/resend-go"
	"github.com/spf13/cobra"
)

const (
	EnvUnsafeHTML             = "GOMAIL_UNSAFE_HTML"
	EnvResendAPIKey           = "RESEND_API_KEY"
	EnvFromAddress            = "GOMAIL_FROM"
	EnvSignature              = "GOMAIL_SIGNATURE"
	EnvSMTPHost               = "GOMAIL_SMTP_HOST"
	EnvSMTPPort               = "GOMAIL_SMTP_PORT"
	EnvSMTPUsername           = "GOMAIL_SMTP_USERNAME"
	EnvSMTPPassword           = "GOMAIL_SMTP_PASSWORD"
	EnvSMTPEncryption         = "GOMAIL_SMTP_ENCRYPTION"
	EnvSMTPInsecureSkipVerify = "GOMAIL_SMTP_INSECURE_SKIP_VERIFY"
)

var (
	from                   string
	to                     []string
	cc                     []string
	bcc                    []string
	subject                string
	body                   string
	attachments            []string
	preview                bool
	unsafe                 bool
	signature              string
	smtpHost               string
	smtpPort               int
	smtpUsername           string
	smtpPassword           string
	smtpEncryption         string
	smtpInsecureSkipVerify bool
	resendAPIKey           string
)

func determineDeliveryMethod() DeliveryMethod {
	hasResend := resendAPIKey != ""
	hasSMTP := smtpUsername != "" && smtpPassword != ""

	switch {
	case hasResend && hasSMTP:
		return DeliveryMethodUnknown
	case hasResend:
		return DeliveryMethodResend
	case hasSMTP:
		if from == "" {
			from = smtpUsername
		}
		return DeliveryMethodSMTP
	default:
		return DeliveryMethodNone
	}
}

func displayUnknownDeliveryMethodError() {
	fmt.Printf("\n  %s Unknown delivery method.\n", errorHeaderStyle.String())
	fmt.Printf("\n  You have set both %s and %s delivery methods.", inlineCodeStyle.Render(EnvResendAPIKey), inlineCodeStyle.Render("GOMAIL_SMTP_*"))
	fmt.Printf("\n  Set only one of these environment variables.\n\n")
}

func isStdinAvailable() bool {
	stat, err := os.Stdin.Stat()
	return err == nil && (stat.Mode()&os.ModeCharDevice) == 0
}

var rootCmd = &cobra.Command{
	Use:   "gomail",
	Short: "Send emails from your terminal with ease",
	Long:  `GoMail is an efficient terminal-based email client for sending emails with support for SMTP and Resend.`,
	RunE: func(cmd *cobra.Command, args []string) error {

		if err := MigrateLegacyConfig(); err != nil {
			return fmt.Errorf("migrating configuration: %w", err)
		}

		config, err := LoadTOMLConfig()
		if err != nil {
			return fmt.Errorf("loading configuration: %w", err)
		}

		cm, err := NewConfigurationManager()
		if err != nil {

			fmt.Printf("Warning: Could not initialize configuration tracking: %v\n", err)
		} else {
			defer cm.Close()

			if err := cm.LogAppStart("cli"); err != nil {

				fmt.Printf("Warning: Could not log application start: %v\n", err)
			}
		}

		GetEnvironmentOverrides(config)

		UpdateTOMLConfigFromFlags(config)

		ApplyTOMLConfig(config)

		if config.Email.DeliveryMethod == "" ||
			(config.Email.DeliveryMethod == "smtp" && config.Email.SMTP.Username == "") ||
			(config.Email.DeliveryMethod == "resend" && config.Email.Resend.APIKey == "") {

			if determineDeliveryMethod() == DeliveryMethodNone {

				setupModel := NewSetupModel()
				p := tea.NewProgram(setupModel)
				_, err := p.Run()
				if err != nil {
					return fmt.Errorf("setup wizard failed: %w", err)
				}

				config, err = LoadTOMLConfig()
				if err != nil {
					return fmt.Errorf("loading configuration after setup: %w", err)
				}
				ApplyTOMLConfig(config)
			}
		}

		deliveryMethod := determineDeliveryMethod()

		switch deliveryMethod {
		case DeliveryMethodNone:

			break
		case DeliveryMethodUnknown:
			displayUnknownDeliveryMethodError()
			cmd.SilenceUsage = true
			cmd.SilenceErrors = true
			return errors.New("unknown delivery method")
		}

		if body == "" && isStdinAvailable() {
			stdinContent, err := io.ReadAll(os.Stdin)
			if err != nil {
				return err
			}
			body = string(stdinContent)
		}

		if signature != "" {
			body += "\n\n" + signature
		}

		if len(to) > 0 && from != "" && subject != "" && body != "" && !preview {

			if deliveryMethod == DeliveryMethodNone {
				cmd.SilenceUsage = true
				cmd.SilenceErrors = true
				fmt.Printf("\n  %s No email delivery method configured.\n", errorHeaderStyle.String())
				fmt.Printf("\n  To send emails, configure either:\n")
				fmt.Printf("  • %s for Resend.com API\n", inlineCodeStyle.Render("RESEND_API_KEY"))
				fmt.Printf("  • %s for SMTP delivery\n\n", inlineCodeStyle.Render("GOMAIL_SMTP_*"))
				fmt.Printf("  Or run with %s to preview the email without sending.\n\n", inlineCodeStyle.Render("--preview"))
				return errors.New("no delivery method configured")
			}

			var err error
			switch deliveryMethod {
			case DeliveryMethodSMTP:
				err = sendSMTPEmail(to, cc, bcc, from, subject, body, attachments)
			case DeliveryMethodResend:
				err = sendResendEmail(to, cc, bcc, from, subject, body, attachments)
			default:
				err = fmt.Errorf("unknown delivery method")
			}
			if err != nil {
				cmd.SilenceUsage = true
				cmd.SilenceErrors = true
				fmt.Println(errorStyle.Render(err.Error()))
				return err
			}
			fmt.Print(emailSummary(to, subject))
			return nil
		}

		p := tea.NewProgram(NewModel(resend.SendEmailRequest{
			From:        from,
			To:          to,
			Bcc:         bcc,
			Cc:          cc,
			Subject:     subject,
			Text:        body,
			Attachments: createResendAttachments(attachments),
		}, deliveryMethod, config))

		m, err := p.Run()
		if err != nil {
			return err
		}
		mm := m.(Model)
		if !mm.abort {
			fmt.Print(emailSummary(strings.Split(mm.To.Value(), ToSeparator), mm.Subject.Value()))
		}
		return nil
	},
}

var (
	Version   string
	CommitSHA string
)

var ManCmd = &cobra.Command{
	Use:    "man",
	Short:  "Generate man page",
	Long:   `Generate the man page for GoMail`,
	Args:   cobra.NoArgs,
	Hidden: true,
	RunE: func(_ *cobra.Command, _ []string) error {
		page, err := mcobra.NewManPage(1, rootCmd)
		if err != nil {
			return err
		}

		page = page.WithSection("Copyright", "© 2025 GoMail Contributors.\n"+"Released under MIT License.")
		fmt.Println(page.Build(roff.NewDocument()))
		return nil
	},
}

var SetupCmd = &cobra.Command{
	Use:   "setup",
	Short: "Run the setup wizard",
	Long:  `Run the setup wizard to configure GoMail for sending emails.`,
	Args:  cobra.NoArgs,
	RunE: func(_ *cobra.Command, _ []string) error {
		setupModel := NewSetupModel()
		p := tea.NewProgram(setupModel)
		_, err := p.Run()
		if err != nil {
			return fmt.Errorf("setup wizard failed: %w", err)
		}
		return nil
	},
}

func init() {
	rootCmd.AddCommand(ManCmd)
	rootCmd.AddCommand(SetupCmd)

	rootCmd.Flags().StringSliceVar(&bcc, "bcc", []string{}, "BCC recipients")
	rootCmd.Flags().StringSliceVar(&cc, "cc", []string{}, "CC recipients")
	rootCmd.Flags().StringSliceVarP(&attachments, "attach", "a", []string{}, "Email attachments")
	rootCmd.Flags().StringSliceVarP(&to, "to", "t", []string{}, "Recipients")
	rootCmd.Flags().StringVarP(&body, "body", "b", "", "Email content")

	envFrom := os.Getenv(EnvFromAddress)
	rootCmd.Flags().StringVarP(&from, "from", "f", envFrom, "Email sender"+commentStyle.Render("($"+EnvFromAddress+")"))
	rootCmd.Flags().StringVarP(&subject, "subject", "s", "", "Email subject")
	rootCmd.Flags().BoolVar(&preview, "preview", false, "Preview email before sending")

	envUnsafe := os.Getenv(EnvUnsafeHTML) == "true"
	rootCmd.Flags().BoolVarP(&unsafe, "unsafe", "u", envUnsafe, "Enable unsafe HTML and extended markdown features"+commentStyle.Render("($"+EnvUnsafeHTML+")"))

	envSignature := os.Getenv(EnvSignature)
	rootCmd.Flags().StringVarP(&signature, "signature", "x", envSignature, "Email signature"+commentStyle.Render("($"+EnvSignature+")"))

	envSMTPHost := os.Getenv(EnvSMTPHost)
	rootCmd.Flags().StringVarP(&smtpHost, "smtp.host", "H", envSMTPHost, "SMTP server host"+commentStyle.Render("($"+EnvSMTPHost+")"))

	envSMTPPort, _ := strconv.Atoi(os.Getenv(EnvSMTPPort))
	if envSMTPPort == 0 {
		envSMTPPort = 587
	}
	rootCmd.Flags().IntVarP(&smtpPort, "smtp.port", "P", envSMTPPort, "SMTP server port"+commentStyle.Render("($"+EnvSMTPPort+")"))

	envSMTPUsername := os.Getenv(EnvSMTPUsername)
	rootCmd.Flags().StringVarP(&smtpUsername, "smtp.username", "U", envSMTPUsername, "SMTP username"+commentStyle.Render("($"+EnvSMTPUsername+")"))

	envSMTPPassword := os.Getenv(EnvSMTPPassword)
	rootCmd.Flags().StringVarP(&smtpPassword, "smtp.password", "p", envSMTPPassword, "SMTP password"+commentStyle.Render("($"+EnvSMTPPassword+")"))

	envSMTPEncryption := os.Getenv(EnvSMTPEncryption)
	rootCmd.Flags().StringVarP(&smtpEncryption, "smtp.encryption", "e", envSMTPEncryption, "SMTP encryption (starttls, ssl, none)"+commentStyle.Render("($"+EnvSMTPEncryption+")"))

	envInsecureSkipVerify := os.Getenv(EnvSMTPInsecureSkipVerify) == "true"
	rootCmd.Flags().BoolVarP(&smtpInsecureSkipVerify, "smtp.insecure", "i", envInsecureSkipVerify, "Skip TLS verification"+commentStyle.Render("($"+EnvSMTPInsecureSkipVerify+")"))

	envResendAPIKey := os.Getenv(EnvResendAPIKey)
	rootCmd.Flags().StringVarP(&resendAPIKey, "resend.key", "r", envResendAPIKey, "Resend.com API key"+commentStyle.Render("($"+EnvResendAPIKey+")"))

	rootCmd.CompletionOptions.HiddenDefaultCmd = true

	if len(CommitSHA) >= 7 {
		vt := rootCmd.VersionTemplate()
		rootCmd.SetVersionTemplate(vt[:len(vt)-1] + " (" + CommitSHA[0:7] + ")\n")
	}
	if Version == "" {
		if info, ok := debug.ReadBuildInfo(); ok && info.Main.Sum != "" {
			Version = info.Main.Version
		} else {
			Version = "unknown (built from source)"
		}
	}
	rootCmd.Version = Version
}

func main() {
	err := rootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}
