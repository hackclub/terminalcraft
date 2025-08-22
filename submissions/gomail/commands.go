package main

import (
	"fmt"
	"strconv"
	"strings"
	"time"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/resendlabs/resend-go"
	"github.com/spf13/cobra"
)

var HistoryCmd = &cobra.Command{
	Use:   "history",
	Short: "Show sent email history",
	Long:  `Display a list of previously sent emails with details like recipients, subject, and send time.`,
	RunE: func(cmd *cobra.Command, args []string) error {
		limit, _ := cmd.Flags().GetInt("limit")
		days, _ := cmd.Flags().GetInt("days")
		showFailed, _ := cmd.Flags().GetBool("failed")

		db, err := NewDatabaseManager()
		if err != nil {
			return fmt.Errorf("opening database: %w", err)
		}
		defer db.Close()

		var fromDate *time.Time
		if days > 0 {
			date := time.Now().AddDate(0, 0, -days)
			fromDate = &date
		}

		emails, err := db.GetSentEmails(limit, 0, fromDate)
		if err != nil {
			return fmt.Errorf("retrieving email history: %w", err)
		}

		if len(emails) == 0 {
			fmt.Println(commentStyle.Render("No emails found in history."))
			return nil
		}

		fmt.Printf("%s\n\n", activeLabelStyle.Render("📧 Email History"))

		for _, email := range emails {

			if showFailed && email.Status != "failed" {
				continue
			}

			if !showFailed && email.Status == "failed" {
				continue
			}

			displayEmailRecord(email)
			fmt.Println()
		}

		return nil
	},
}

var StatsCmd = &cobra.Command{
	Use:   "stats",
	Short: "Show email statistics",
	Long:  `Display statistics about sent emails, including total count, success rate, and recent activity.`,
	RunE: func(cmd *cobra.Command, args []string) error {
		db, err := NewDatabaseManager()
		if err != nil {
			return fmt.Errorf("opening database: %w", err)
		}
		defer db.Close()

		stats, err := db.GetSentEmailStats()
		if err != nil {
			return fmt.Errorf("retrieving statistics: %w", err)
		}

		fmt.Printf("%s\n\n", activeLabelStyle.Render("📊 Email Statistics"))

		totalSent := stats["total_sent"].(int)
		totalFailed := stats["total_failed"].(int)
		sentToday := stats["sent_today"].(int)

		fmt.Printf("Total sent: %s\n", textStyle.Foreground(successColor).Render(strconv.Itoa(totalSent)))
		fmt.Printf("Failed: %s\n", textStyle.Foreground(errorColor).Render(strconv.Itoa(totalFailed)))
		fmt.Printf("Sent today: %s\n", activeTextStyle.Render(strconv.Itoa(sentToday)))

		if totalSent+totalFailed > 0 {
			successRate := float64(totalSent) / float64(totalSent+totalFailed) * 100
			fmt.Printf("Success rate: %s\n", textStyle.Render(fmt.Sprintf("%.1f%%", successRate)))
		}

		if lastSent, ok := stats["last_sent"].(time.Time); ok {
			fmt.Printf("Last sent: %s\n", textStyle.Render(lastSent.Format("2006-01-02 15:04:05")))
		}

		return nil
	},
}

var DraftsCmd = &cobra.Command{
	Use:   "drafts",
	Short: "Manage email drafts",
	Long:  `Save, list, load, and delete email drafts.`,
}

var SaveDraftCmd = &cobra.Command{
	Use:   "save [name]",
	Short: "Save current email as a draft",
	Long:  `Save the current email content as a draft with the specified name.`,
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		name := args[0]

		if from == "" || to == nil || subject == "" || body == "" {
			return fmt.Errorf("email fields must be provided to save as draft")
		}

		db, err := NewDatabaseManager()
		if err != nil {
			return fmt.Errorf("opening database: %w", err)
		}
		defer db.Close()

		draft := CacheEntry{
			Type:    "draft",
			Name:    name,
			From:    from,
			To:      strings.Join(to, ","),
			Cc:      strings.Join(cc, ","),
			Bcc:     strings.Join(bcc, ","),
			Subject: subject,
			Body:    body,
		}

		if err := db.SaveCacheEntry(draft); err != nil {
			return fmt.Errorf("saving draft: %w", err)
		}

		fmt.Printf("Draft '%s' saved successfully.\n", name)
		return nil
	},
}

var ListDraftsCmd = &cobra.Command{
	Use:   "list",
	Short: "List all saved drafts",
	Long:  `Display a list of all saved email drafts.`,
	RunE: func(cmd *cobra.Command, args []string) error {
		db, err := NewDatabaseManager()
		if err != nil {
			return fmt.Errorf("opening database: %w", err)
		}
		defer db.Close()

		drafts, err := db.GetCacheEntries("draft")
		if err != nil {
			return fmt.Errorf("retrieving drafts: %w", err)
		}

		if len(drafts) == 0 {
			fmt.Println(commentStyle.Render("No drafts found."))
			return nil
		}

		fmt.Printf("%s\n\n", activeLabelStyle.Render("📝 Saved Drafts"))

		for _, draft := range drafts {
			fmt.Printf("%s\n", activeTextStyle.Render(draft.Name))
			fmt.Printf("  Subject: %s\n", textStyle.Render(draft.Subject))
			fmt.Printf("  To: %s\n", textStyle.Render(draft.To))
			fmt.Printf("  Updated: %s\n", commentStyle.Render(draft.UpdatedAt.Format("2006-01-02 15:04")))
			fmt.Println()
		}

		return nil
	},
}

var LoadDraftCmd = &cobra.Command{
	Use:   "load [name]",
	Short: "Load a saved draft",
	Long:  `Load a saved draft and start the compose interface with the draft content.`,
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		name := args[0]

		db, err := NewDatabaseManager()
		if err != nil {
			return fmt.Errorf("opening database: %w", err)
		}
		defer db.Close()

		draft, err := db.GetCacheEntry("draft", name)
		if err != nil {
			return fmt.Errorf("retrieving draft: %w", err)
		}

		if draft == nil {
			return fmt.Errorf("draft '%s' not found", name)
		}

		from = draft.From
		to = strings.Split(draft.To, ",")
		if draft.Cc != "" {
			cc = strings.Split(draft.Cc, ",")
		}
		if draft.Bcc != "" {
			bcc = strings.Split(draft.Bcc, ",")
		}
		subject = draft.Subject
		body = draft.Body

		deliveryMethod := determineDeliveryMethod()

		config, err := LoadTOMLConfig()
		if err != nil {
			return fmt.Errorf("loading configuration: %w", err)
		}

		p := tea.NewProgram(NewModel(resend.SendEmailRequest{
			From:    from,
			To:      to,
			Cc:      cc,
			Bcc:     bcc,
			Subject: subject,
			Text:    body,
		}, deliveryMethod, config))

		_, err = p.Run()
		return err
	},
}

var DeleteDraftCmd = &cobra.Command{
	Use:   "delete [name]",
	Short: "Delete a saved draft",
	Long:  `Delete a saved draft by name.`,
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		name := args[0]

		db, err := NewDatabaseManager()
		if err != nil {
			return fmt.Errorf("opening database: %w", err)
		}
		defer db.Close()

		if err := db.DeleteCacheEntry("draft", name); err != nil {
			return fmt.Errorf("deleting draft: %w", err)
		}

		fmt.Printf("Draft '%s' deleted successfully.\n", name)
		return nil
	},
}

var CleanupCmd = &cobra.Command{
	Use:   "cleanup",
	Short: "Clean up old emails and drafts",
	Long:  `Remove old sent emails and drafts based on retention policy.`,
	RunE: func(cmd *cobra.Command, args []string) error {
		emailDays, _ := cmd.Flags().GetInt("email-days")
		draftDays, _ := cmd.Flags().GetInt("draft-days")

		db, err := NewDatabaseManager()
		if err != nil {
			return fmt.Errorf("opening database: %w", err)
		}
		defer db.Close()

		if err := db.CleanupOldEntries(emailDays, draftDays); err != nil {
			return fmt.Errorf("cleaning up old entries: %w", err)
		}

		fmt.Println("Cleanup completed successfully.")
		return nil
	},
}

var ConfigCmd = &cobra.Command{
	Use:   "config",
	Short: "Manage GoMail configuration",
	Long:  `Configure GoMail settings, view configuration history, and manage application preferences.`,
}

var ConfigSetCmd = &cobra.Command{
	Use:   "set <key> <value>",
	Short: "Set a configuration value",
	Long:  `Set a configuration value. Key should be in dot notation (e.g., app.default_from, email.smtp.host).`,
	Args:  cobra.ExactArgs(2),
	RunE: func(cmd *cobra.Command, args []string) error {
		key := args[0]
		value := args[1]
		description, _ := cmd.Flags().GetString("description")

		cm, err := NewConfigurationManager()
		if err != nil {
			return fmt.Errorf("initializing configuration manager: %w", err)
		}
		defer cm.Close()

		oldValue, _ := cm.GetConfigurationValue(key)

		if err := cm.UpdateConfiguration(key, oldValue, value, "cli", description); err != nil {
			return fmt.Errorf("updating configuration: %w", err)
		}

		fmt.Printf("%s Configuration updated successfully\n", successStyle.Render("✓"))
		fmt.Printf("Key: %s\n", activeTextStyle.Render(key))
		if oldValue != "" {
			fmt.Printf("Old value: %s\n", textStyle.Render(oldValue))
		}
		fmt.Printf("New value: %s\n", activeTextStyle.Render(value))

		return nil
	},
}

var ConfigGetCmd = &cobra.Command{
	Use:   "get <key>",
	Short: "Get a configuration value",
	Long:  `Get a configuration value by key. Key should be in dot notation.`,
	Args:  cobra.ExactArgs(1),
	RunE: func(cmd *cobra.Command, args []string) error {
		key := args[0]

		cm, err := NewConfigurationManager()
		if err != nil {
			return fmt.Errorf("initializing configuration manager: %w", err)
		}
		defer cm.Close()

		value, err := cm.GetConfigurationValue(key)
		if err != nil {
			return fmt.Errorf("getting configuration: %w", err)
		}

		fmt.Printf("%s: %s\n", labelStyle.Render(key), activeTextStyle.Render(value))
		return nil
	},
}

var ConfigListCmd = &cobra.Command{
	Use:   "list",
	Short: "List all configuration values",
	Long:  `Display all current configuration values organized by section.`,
	RunE: func(cmd *cobra.Command, args []string) error {
		config, err := LoadTOMLConfig()
		if err != nil {
			return fmt.Errorf("loading configuration: %w", err)
		}

		fmt.Printf("%s\n\n", activeLabelStyle.Render("🔧 GoMail Configuration"))

		fmt.Printf("%s\n", labelStyle.Render("Application Settings:"))
		fmt.Printf("  default_from: %s\n", textStyle.Render(config.App.DefaultFrom))
		fmt.Printf("  signature: %s\n", textStyle.Render(config.App.Signature))
		fmt.Printf("  unsafe_html: %s\n", textStyle.Render(strconv.FormatBool(config.App.UnsafeHTML)))
		fmt.Println()

		fmt.Printf("%s\n", labelStyle.Render("Email Settings:"))
		fmt.Printf("  delivery_method: %s\n", textStyle.Render(config.Email.DeliveryMethod))
		fmt.Printf("  smtp.host: %s\n", textStyle.Render(config.Email.SMTP.Host))
		fmt.Printf("  smtp.port: %s\n", textStyle.Render(strconv.Itoa(config.Email.SMTP.Port)))
		fmt.Printf("  smtp.username: %s\n", textStyle.Render(config.Email.SMTP.Username))
		fmt.Printf("  smtp.password: %s\n", textStyle.Render(maskPassword(config.Email.SMTP.Password)))
		fmt.Printf("  smtp.encryption: %s\n", textStyle.Render(config.Email.SMTP.Encryption))
		fmt.Printf("  smtp.insecure_skip_verify: %s\n", textStyle.Render(strconv.FormatBool(config.Email.SMTP.InsecureSkipVerify)))
		fmt.Printf("  resend.api_key: %s\n", textStyle.Render(maskPassword(config.Email.Resend.APIKey)))
		fmt.Println()

		fmt.Printf("%s\n", labelStyle.Render("Storage Settings:"))
		fmt.Printf("  retention_days: %s\n", textStyle.Render(strconv.Itoa(config.Storage.RetentionDays)))
		fmt.Printf("  cache_retention_days: %s\n", textStyle.Render(strconv.Itoa(config.Storage.CacheRetentionDays)))
		fmt.Printf("  auto_save_drafts: %s\n", textStyle.Render(strconv.FormatBool(config.Storage.AutoSaveDrafts)))
		fmt.Printf("  auto_save_interval_seconds: %s\n", textStyle.Render(strconv.Itoa(config.Storage.AutoSaveInterval)))
		fmt.Println()

		fmt.Printf("%s\n", labelStyle.Render("UI Settings:"))
		fmt.Printf("  theme: %s\n", textStyle.Render(config.UI.Theme))
		fmt.Printf("  show_cc_bcc: %s\n", textStyle.Render(strconv.FormatBool(config.UI.ShowCcBcc)))
		fmt.Printf("  compact_mode: %s\n", textStyle.Render(strconv.FormatBool(config.UI.CompactMode)))

		return nil
	},
}

var ConfigHistoryCmd = &cobra.Command{
	Use:   "history",
	Short: "Show configuration change history",
	Long:  `Display a history of configuration changes with timestamps and sources.`,
	RunE: func(cmd *cobra.Command, args []string) error {
		limit, _ := cmd.Flags().GetInt("limit")
		key, _ := cmd.Flags().GetString("key")

		cm, err := NewConfigurationManager()
		if err != nil {
			return fmt.Errorf("initializing configuration manager: %w", err)
		}
		defer cm.Close()

		history, err := cm.GetConfigurationHistory(limit, key)
		if err != nil {
			return fmt.Errorf("getting configuration history: %w", err)
		}

		if len(history) == 0 {
			fmt.Println(commentStyle.Render("No configuration changes found."))
			return nil
		}

		fmt.Printf("%s\n\n", activeLabelStyle.Render("📝 Configuration History"))

		for _, entry := range history {
			fmt.Printf("%s %s\n",
				textStyle.Foreground(primaryColor).Render("•"),
				activeTextStyle.Render(entry.ConfigKey))

			fmt.Printf("  Changed: %s\n", textStyle.Render(entry.ChangedAt.Format("2006-01-02 15:04:05")))
			fmt.Printf("  Source: %s\n", textStyle.Render(entry.Source))
			fmt.Printf("  Type: %s\n", textStyle.Render(entry.ChangeType))

			if entry.OldValue != "" {
				fmt.Printf("  Old: %s\n", textStyle.Render(entry.OldValue))
			}
			fmt.Printf("  New: %s\n", activeTextStyle.Render(entry.NewValue))

			if entry.Description != "" {
				fmt.Printf("  Description: %s\n", commentStyle.Render(entry.Description))
			}

			fmt.Println()
		}

		return nil
	},
}

var ConfigResetCmd = &cobra.Command{
	Use:   "reset",
	Short: "Reset configuration to defaults",
	Long:  `Reset all configuration values to their defaults. This action is logged.`,
	RunE: func(cmd *cobra.Command, args []string) error {
		force, _ := cmd.Flags().GetBool("force")
		description, _ := cmd.Flags().GetString("description")

		if !force {
			fmt.Printf("%s ", textStyle.Render("This will reset all configuration to defaults. Continue? (y/N):"))
			var response string
			fmt.Scanln(&response)
			if strings.ToLower(response) != "y" && strings.ToLower(response) != "yes" {
				fmt.Println(commentStyle.Render("Operation cancelled."))
				return nil
			}
		}

		cm, err := NewConfigurationManager()
		if err != nil {
			return fmt.Errorf("initializing configuration manager: %w", err)
		}
		defer cm.Close()

		if err := cm.ResetConfiguration("cli", description); err != nil {
			return fmt.Errorf("resetting configuration: %w", err)
		}

		fmt.Printf("%s Configuration reset to defaults successfully\n", successStyle.Render("✓"))
		return nil
	},
}

var ConfigStatsCmd = &cobra.Command{
	Use:   "stats",
	Short: "Show configuration statistics",
	Long:  `Display statistics about configuration usage and recent changes.`,
	RunE: func(cmd *cobra.Command, args []string) error {
		cm, err := NewConfigurationManager()
		if err != nil {
			return fmt.Errorf("initializing configuration manager: %w", err)
		}
		defer cm.Close()

		stats, err := cm.GetConfigurationStats()
		if err != nil {
			return fmt.Errorf("getting configuration stats: %w", err)
		}

		fmt.Printf("%s\n\n", activeLabelStyle.Render("📊 Configuration Statistics"))

		fmt.Printf("Total changes: %s\n", activeTextStyle.Render(strconv.Itoa(stats.TotalConfigurations)))
		fmt.Printf("Changes today: %s\n", activeTextStyle.Render(strconv.Itoa(stats.ConfiguredToday)))

		if stats.LastConfigured != nil {
			fmt.Printf("Last changed: %s\n", textStyle.Render(stats.LastConfigured.Format("2006-01-02 15:04:05")))
		}

		if stats.MostActiveKey != "" {
			fmt.Printf("Most changed key: %s\n", activeTextStyle.Render(stats.MostActiveKey))
		}

		if len(stats.RecentChanges) > 0 {
			fmt.Printf("\n%s\n", labelStyle.Render("Recent Changes:"))
			for i, change := range stats.RecentChanges {
				if i >= 5 {
					break
				}
				fmt.Printf("  %s (%s)\n",
					textStyle.Render(change.ConfigKey),
					commentStyle.Render(change.ChangedAt.Format("01/02 15:04")))
			}
		}

		return nil
	},
}

var ReconfigureCmd = &cobra.Command{
	Use:   "reconfigure",
	Short: "Launch setup wizard to reconfigure GoMail",
	Long:  `Launch the interactive setup wizard to reconfigure GoMail settings. This will update your configuration and log the reconfiguration event.`,
	RunE: func(cmd *cobra.Command, args []string) error {

		cm, err := NewConfigurationManager()
		if err != nil {
			return fmt.Errorf("initializing configuration manager: %w", err)
		}
		defer cm.Close()

		if err := cm.db.LogAppEvent("reconfigure", "cli", "Reconfiguration started via CLI", ""); err != nil {
			fmt.Printf("Warning: Could not log reconfiguration event: %v\n", err)
		}

		fmt.Printf("%s\n", activeLabelStyle.Render("🔧 GoMail Reconfiguration"))
		fmt.Printf("This will launch the setup wizard to reconfigure your GoMail settings.\n\n")

		setupModel := NewSetupModel()
		p := tea.NewProgram(setupModel)
		_, err = p.Run()
		if err != nil {

			cm.db.LogAppEvent("reconfigure", "cli", "Reconfiguration failed", fmt.Sprintf(`{"error": "%s"}`, err.Error()))
			return fmt.Errorf("setup wizard failed: %w", err)
		}

		if err := cm.db.LogAppEvent("reconfigure", "cli", "Reconfiguration completed successfully", ""); err != nil {
			fmt.Printf("Warning: Could not log reconfiguration completion: %v\n", err)
		}

		fmt.Printf("\n%s Reconfiguration completed successfully!\n", successStyle.Render("✓"))
		return nil
	},
}

func displayEmailRecord(email SentEmail) {
	statusStyle := textStyle.Foreground(successColor)
	statusText := "✓ Sent"

	if email.Status == "failed" {
		statusStyle = textStyle.Foreground(errorColor)
		statusText = "✗ Failed"
	}

	fmt.Printf("%s %s\n", statusStyle.Render(statusText), textStyle.Render(email.SentAt.Format("2006-01-02 15:04")))
	fmt.Printf("  From: %s\n", textStyle.Render(email.From))
	fmt.Printf("  To: %s\n", textStyle.Render(email.To))

	if email.Cc != "" {
		fmt.Printf("  Cc: %s\n", textStyle.Render(email.Cc))
	}

	fmt.Printf("  Subject: %s\n", activeTextStyle.Render(email.Subject))
	fmt.Printf("  Method: %s\n", commentStyle.Render(email.Method))

	if email.Status == "failed" && email.ErrorMessage != "" {
		fmt.Printf("  Error: %s\n", errorStyle.Render(email.ErrorMessage))
	}

	if email.Attachments != "" {
		attachments := strings.Split(email.Attachments, ";")
		fmt.Printf("  Attachments: %s\n", commentStyle.Render(fmt.Sprintf("%d file(s)", len(attachments))))
	}
}

func init() {

	HistoryCmd.Flags().IntP("limit", "l", 20, "Maximum number of emails to show")
	HistoryCmd.Flags().IntP("days", "d", 0, "Show emails from last N days (0 = all)")
	HistoryCmd.Flags().BoolP("failed", "f", false, "Show only failed emails")

	CleanupCmd.Flags().IntP("email-days", "e", 365, "Remove sent emails older than N days")
	CleanupCmd.Flags().IntP("draft-days", "d", 30, "Remove drafts older than N days")

	ConfigSetCmd.Flags().String("description", "", "Description of the configuration change")
	ConfigHistoryCmd.Flags().Int("limit", 20, "Maximum number of history entries to show")
	ConfigHistoryCmd.Flags().String("key", "", "Filter history by configuration key")
	ConfigResetCmd.Flags().Bool("force", false, "Skip confirmation prompt")
	ConfigResetCmd.Flags().String("description", "", "Description of the reset action")

	ConfigCmd.AddCommand(ConfigSetCmd)
	ConfigCmd.AddCommand(ConfigGetCmd)
	ConfigCmd.AddCommand(ConfigListCmd)
	ConfigCmd.AddCommand(ConfigHistoryCmd)
	ConfigCmd.AddCommand(ConfigResetCmd)
	ConfigCmd.AddCommand(ConfigStatsCmd)

	SaveDraftCmd.Flags().String("tags", "", "Comma-separated tags for the draft")

	DraftsCmd.AddCommand(SaveDraftCmd)
	DraftsCmd.AddCommand(ListDraftsCmd)
	DraftsCmd.AddCommand(LoadDraftCmd)
	DraftsCmd.AddCommand(DeleteDraftCmd)

	rootCmd.AddCommand(HistoryCmd)
	rootCmd.AddCommand(StatsCmd)
	rootCmd.AddCommand(DraftsCmd)
	rootCmd.AddCommand(CleanupCmd)
	rootCmd.AddCommand(ConfigCmd)
	rootCmd.AddCommand(ReconfigureCmd)
}

func maskPassword(password string) string {
	if password == "" {
		return ""
	}
	if len(password) <= 4 {
		return strings.Repeat("*", len(password))
	}
	return password[:2] + strings.Repeat("*", len(password)-4) + password[len(password)-2:]
}
