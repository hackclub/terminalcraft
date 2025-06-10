package main

import (
	"fmt"
	"os"
	"path/filepath"
	"runtime/debug"
	"strconv"
	"time"

	"github.com/pelletier/go-toml/v2"
)

type TOMLConfig struct {
	App AppConfig `toml:"app"`

	Email EmailConfig `toml:"email"`

	Storage StorageConfig `toml:"storage"`

	UI UIConfig `toml:"ui"`
}

type AppConfig struct {
	DefaultFrom string `toml:"default_from"`
	Signature   string `toml:"signature"`
	UnsafeHTML  bool   `toml:"unsafe_html"`
}

type EmailConfig struct {
	DeliveryMethod string       `toml:"delivery_method"`
	SMTP           SMTPConfig   `toml:"smtp"`
	Resend         ResendConfig `toml:"resend"`
	IMAP           IMAPConfig   `toml:"imap"`
}

type SMTPConfig struct {
	Host               string `toml:"host"`
	Port               int    `toml:"port"`
	Username           string `toml:"username"`
	Password           string `toml:"password"`
	Encryption         string `toml:"encryption"`
	InsecureSkipVerify bool   `toml:"insecure_skip_verify"`
}

type ResendConfig struct {
	APIKey string `toml:"api_key"`
}

type StorageConfig struct {
	RetentionDays      int `toml:"retention_days"`
	CacheRetentionDays int `toml:"cache_retention_days"`

	AutoSaveDrafts   bool `toml:"auto_save_drafts"`
	AutoSaveInterval int  `toml:"auto_save_interval_seconds"`
}

type UIConfig struct {
	Theme       string `toml:"theme"`
	ShowCcBcc   bool   `toml:"show_cc_bcc"`
	CompactMode bool   `toml:"compact_mode"`
}

type IMAPConfig struct {
	Host               string `toml:"host"`
	Port               int    `toml:"port"`
	Username           string `toml:"username"`
	Password           string `toml:"password"`
	Encryption         string `toml:"encryption"`
	InsecureSkipVerify bool   `toml:"insecure_skip_verify"`
	AutoDetect         bool   `toml:"auto_detect"`
}

func getConfigDir() string {
	homeDir, _ := os.UserHomeDir()
	return filepath.Join(homeDir, ".gomail")
}

func getTOMLConfigPath() string {
	return filepath.Join(getConfigDir(), "config.toml")
}

func getDefaultTOMLConfig() TOMLConfig {
	return TOMLConfig{
		App: AppConfig{
			DefaultFrom: "",
			Signature:   "",
			UnsafeHTML:  false,
		},
		Email: EmailConfig{
			DeliveryMethod: "smtp",
			SMTP: SMTPConfig{
				Host:               "smtp.gmail.com",
				Port:               587,
				Username:           "",
				Password:           "",
				Encryption:         "starttls",
				InsecureSkipVerify: false,
			},
			Resend: ResendConfig{
				APIKey: "",
			},
		},
		Storage: StorageConfig{
			RetentionDays:      365,
			CacheRetentionDays: 30,
			AutoSaveDrafts:     true,
			AutoSaveInterval:   30,
		},
		UI: UIConfig{
			Theme:       "auto",
			ShowCcBcc:   false,
			CompactMode: false,
		},
	}
}

func LoadTOMLConfig() (*TOMLConfig, error) {
	configPath := getTOMLConfigPath()

	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		defaultConfig := getDefaultTOMLConfig()
		if err := SaveTOMLConfig(&defaultConfig); err != nil {
			return nil, fmt.Errorf("creating default config: %w", err)
		}
		return &defaultConfig, nil
	}

	data, err := os.ReadFile(configPath)
	if err != nil {
		return nil, fmt.Errorf("reading config file: %w", err)
	}

	var config TOMLConfig
	if err := toml.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("parsing TOML config: %w", err)
	}

	return &config, nil
}

func SaveTOMLConfig(config *TOMLConfig) error {
	configPath := getTOMLConfigPath()
	configDir := filepath.Dir(configPath)

	if err := os.MkdirAll(configDir, 0755); err != nil {
		return fmt.Errorf("creating config directory: %w", err)
	}

	data, err := toml.Marshal(config)
	if err != nil {
		return fmt.Errorf("marshaling TOML config: %w", err)
	}

	if err := os.WriteFile(configPath, data, 0600); err != nil {
		return fmt.Errorf("writing config file: %w", err)
	}

	return nil
}

func MigrateLegacyConfig() error {
	legacyConfigPath := getConfigPath()
	tomlConfigPath := getTOMLConfigPath()

	if _, err := os.Stat(tomlConfigPath); err == nil {
		return nil
	}

	if _, err := os.Stat(legacyConfigPath); os.IsNotExist(err) {
		return nil
	}

	legacyConfig, err := loadConfig()
	if err != nil {
		return fmt.Errorf("loading legacy config: %w", err)
	}

	if legacyConfig == nil {
		return nil
	}

	tomlConfig := getDefaultTOMLConfig()

	tomlConfig.App.DefaultFrom = legacyConfig.FromAddress

	switch legacyConfig.DeliveryMethod {
	case "smtp":
		tomlConfig.Email.DeliveryMethod = "smtp"
		tomlConfig.Email.SMTP.Host = legacyConfig.SMTPHost
		tomlConfig.Email.SMTP.Port = legacyConfig.SMTPPort
		tomlConfig.Email.SMTP.Username = legacyConfig.SMTPUsername
		tomlConfig.Email.SMTP.Password = legacyConfig.SMTPPassword
		tomlConfig.Email.SMTP.Encryption = legacyConfig.SMTPEncryption
	case "resend":
		tomlConfig.Email.DeliveryMethod = "resend"
		tomlConfig.Email.Resend.APIKey = legacyConfig.ResendAPIKey
	}

	if err := SaveTOMLConfig(&tomlConfig); err != nil {
		return fmt.Errorf("saving migrated TOML config: %w", err)
	}

	backupPath := legacyConfigPath + ".bak"
	if err := os.Rename(legacyConfigPath, backupPath); err != nil {
		return fmt.Errorf("backing up legacy config: %w", err)
	}

	fmt.Printf("Configuration migrated from JSON to TOML format.\n")
	fmt.Printf("Legacy config backed up to: %s\n", backupPath)

	return nil
}

func ApplyTOMLConfig(config *TOMLConfig) {

	if from == "" && config.App.DefaultFrom != "" {
		from = config.App.DefaultFrom
	}

	if signature == "" && config.App.Signature != "" {
		signature = config.App.Signature
	}

	if !unsafe {
		unsafe = config.App.UnsafeHTML
	}

	switch config.Email.DeliveryMethod {
	case "smtp":
		if smtpHost == "" {
			smtpHost = config.Email.SMTP.Host
		}
		if smtpPort == 0 {
			smtpPort = config.Email.SMTP.Port
		}
		if smtpUsername == "" {
			smtpUsername = config.Email.SMTP.Username
		}
		if smtpPassword == "" {
			smtpPassword = config.Email.SMTP.Password
		}
		if smtpEncryption == "" {
			smtpEncryption = config.Email.SMTP.Encryption
		}
		smtpInsecureSkipVerify = config.Email.SMTP.InsecureSkipVerify
	case "resend":
		if resendAPIKey == "" {
			resendAPIKey = config.Email.Resend.APIKey
		}
	}
}

func UpdateTOMLConfigFromFlags(config *TOMLConfig) {

	if from != "" {
		config.App.DefaultFrom = from
	}
	if signature != "" {
		config.App.Signature = signature
	}
	config.App.UnsafeHTML = unsafe

	if smtpHost != "" {
		config.Email.SMTP.Host = smtpHost
		config.Email.DeliveryMethod = "smtp"
	}
	if smtpPort != 0 {
		config.Email.SMTP.Port = smtpPort
	}
	if smtpUsername != "" {
		config.Email.SMTP.Username = smtpUsername
		config.Email.DeliveryMethod = "smtp"
	}
	if smtpPassword != "" {
		config.Email.SMTP.Password = smtpPassword
	}
	if smtpEncryption != "" {
		config.Email.SMTP.Encryption = smtpEncryption
	}

	if resendAPIKey != "" {
		config.Email.Resend.APIKey = resendAPIKey
		config.Email.DeliveryMethod = "resend"
	}
}

func ValidateTOMLConfig(config *TOMLConfig) error {

	switch config.Email.DeliveryMethod {
	case "smtp":
		if config.Email.SMTP.Host == "" {
			return fmt.Errorf("SMTP host is required when using SMTP delivery")
		}
		if config.Email.SMTP.Port <= 0 || config.Email.SMTP.Port > 65535 {
			return fmt.Errorf("SMTP port must be between 1 and 65535")
		}
		if config.Email.SMTP.Username == "" {
			return fmt.Errorf("SMTP username is required")
		}
		if config.Email.SMTP.Password == "" {
			return fmt.Errorf("SMTP password is required")
		}
		if config.Email.SMTP.Encryption != "" &&
			config.Email.SMTP.Encryption != "starttls" &&
			config.Email.SMTP.Encryption != "ssl" &&
			config.Email.SMTP.Encryption != "none" {
			return fmt.Errorf("SMTP encryption must be 'starttls', 'ssl', or 'none'")
		}
	case "resend":
		if config.Email.Resend.APIKey == "" {
			return fmt.Errorf("Resend API key is required when using Resend delivery")
		}
	default:
		return fmt.Errorf("delivery method must be 'smtp' or 'resend'")
	}

	if config.Storage.RetentionDays < 0 {
		return fmt.Errorf("retention days must be non-negative")
	}
	if config.Storage.CacheRetentionDays < 0 {
		return fmt.Errorf("cache retention days must be non-negative")
	}
	if config.Storage.AutoSaveInterval < 5 {
		return fmt.Errorf("auto-save interval must be at least 5 seconds")
	}

	if config.UI.Theme != "auto" && config.UI.Theme != "light" && config.UI.Theme != "dark" {
		return fmt.Errorf("UI theme must be 'auto', 'light', or 'dark'")
	}

	return nil
}

func GetEnvironmentOverrides(config *TOMLConfig) {

	if envFrom := os.Getenv(EnvFromAddress); envFrom != "" {
		config.App.DefaultFrom = envFrom
	}

	if envSignature := os.Getenv(EnvSignature); envSignature != "" {
		config.App.Signature = envSignature
	}

	if envUnsafe := os.Getenv(EnvUnsafeHTML); envUnsafe == "true" {
		config.App.UnsafeHTML = true
	}

	if envSMTPHost := os.Getenv(EnvSMTPHost); envSMTPHost != "" {
		config.Email.SMTP.Host = envSMTPHost
		config.Email.DeliveryMethod = "smtp"
	}

	if envSMTPPort := os.Getenv(EnvSMTPPort); envSMTPPort != "" {
		if port, err := strconv.Atoi(envSMTPPort); err == nil {
			config.Email.SMTP.Port = port
		}
	}

	if envSMTPUsername := os.Getenv(EnvSMTPUsername); envSMTPUsername != "" {
		config.Email.SMTP.Username = envSMTPUsername
		config.Email.DeliveryMethod = "smtp"
	}

	if envSMTPPassword := os.Getenv(EnvSMTPPassword); envSMTPPassword != "" {
		config.Email.SMTP.Password = envSMTPPassword
	}

	if envSMTPEncryption := os.Getenv(EnvSMTPEncryption); envSMTPEncryption != "" {
		config.Email.SMTP.Encryption = envSMTPEncryption
	}

	if envInsecureSkipVerify := os.Getenv(EnvSMTPInsecureSkipVerify); envInsecureSkipVerify == "true" {
		config.Email.SMTP.InsecureSkipVerify = true
	}

	if envResendAPIKey := os.Getenv(EnvResendAPIKey); envResendAPIKey != "" {
		config.Email.Resend.APIKey = envResendAPIKey
		config.Email.DeliveryMethod = "resend"
	}
}

type ConfigurationManager struct {
	db *DatabaseManager
}

func NewConfigurationManager() (*ConfigurationManager, error) {
	db, err := NewDatabaseManager()
	if err != nil {
		return nil, fmt.Errorf("creating database manager: %w", err)
	}

	return &ConfigurationManager{db: db}, nil
}

func (cm *ConfigurationManager) Close() error {
	if cm.db != nil {
		return cm.db.Close()
	}
	return nil
}

func (cm *ConfigurationManager) UpdateConfiguration(key, oldValue, newValue, source, description string) error {

	config, err := LoadTOMLConfig()
	if err != nil {
		return fmt.Errorf("loading current config: %w", err)
	}

	if err := cm.applyConfigChange(config, key, newValue); err != nil {
		return fmt.Errorf("applying config change: %w", err)
	}

	if err := SaveTOMLConfig(config); err != nil {
		return fmt.Errorf("saving config: %w", err)
	}

	changeType := "update"
	if oldValue == "" {
		changeType = "create"
	}

	if err := cm.db.LogConfigurationChange(key, oldValue, newValue, changeType, source, description); err != nil {
		return fmt.Errorf("logging config change: %w", err)
	}

	eventDesc := fmt.Sprintf("Configuration '%s' updated via %s", key, source)
	if err := cm.db.LogAppEvent("config_change", source, eventDesc, ""); err != nil {

		fmt.Printf("Warning: Failed to log app event: %v\n", err)
	}

	return nil
}

func (cm *ConfigurationManager) applyConfigChange(config *TOMLConfig, key, value string) error {
	switch key {

	case "app.default_from":
		config.App.DefaultFrom = value
	case "app.signature":
		config.App.Signature = value
	case "app.unsafe_html":
		config.App.UnsafeHTML = value == "true"

	case "email.delivery_method":
		config.Email.DeliveryMethod = value
	case "email.smtp.host":
		config.Email.SMTP.Host = value
	case "email.smtp.port":
		if port, err := strconv.Atoi(value); err == nil {
			config.Email.SMTP.Port = port
		} else {
			return fmt.Errorf("invalid port number: %s", value)
		}
	case "email.smtp.username":
		config.Email.SMTP.Username = value
	case "email.smtp.password":
		config.Email.SMTP.Password = value
	case "email.smtp.encryption":
		config.Email.SMTP.Encryption = value
	case "email.smtp.insecure_skip_verify":
		config.Email.SMTP.InsecureSkipVerify = value == "true"
	case "email.resend.api_key":
		config.Email.Resend.APIKey = value

	case "storage.retention_days":
		if days, err := strconv.Atoi(value); err == nil {
			config.Storage.RetentionDays = days
		} else {
			return fmt.Errorf("invalid retention days: %s", value)
		}
	case "storage.cache_retention_days":
		if days, err := strconv.Atoi(value); err == nil {
			config.Storage.CacheRetentionDays = days
		} else {
			return fmt.Errorf("invalid cache retention days: %s", value)
		}
	case "storage.auto_save_drafts":
		config.Storage.AutoSaveDrafts = value == "true"
	case "storage.auto_save_interval_seconds":
		if interval, err := strconv.Atoi(value); err == nil {
			config.Storage.AutoSaveInterval = interval
		} else {
			return fmt.Errorf("invalid auto save interval: %s", value)
		}

	case "ui.theme":
		if value != "auto" && value != "light" && value != "dark" {
			return fmt.Errorf("invalid theme: %s (must be 'auto', 'light', or 'dark')", value)
		}
		config.UI.Theme = value
	case "ui.show_cc_bcc":
		config.UI.ShowCcBcc = value == "true"
	case "ui.compact_mode":
		config.UI.CompactMode = value == "true"

	default:
		return fmt.Errorf("unknown configuration key: %s", key)
	}

	return nil
}

func (cm *ConfigurationManager) ResetConfiguration(source, description string) error {

	defaultConfig := getDefaultTOMLConfig()

	if err := SaveTOMLConfig(&defaultConfig); err != nil {
		return fmt.Errorf("saving default config: %w", err)
	}

	if err := cm.db.LogConfigurationChange("*", "various", "defaults", "reset", source, description); err != nil {
		return fmt.Errorf("logging config reset: %w", err)
	}

	eventDesc := fmt.Sprintf("Configuration reset to defaults via %s", source)
	if err := cm.db.LogAppEvent("reconfigure", source, eventDesc, ""); err != nil {

		fmt.Printf("Warning: Failed to log app event: %v\n", err)
	}

	return nil
}

func (cm *ConfigurationManager) GetConfigurationValue(key string) (string, error) {
	config, err := LoadTOMLConfig()
	if err != nil {
		return "", fmt.Errorf("loading config: %w", err)
	}

	switch key {

	case "app.default_from":
		return config.App.DefaultFrom, nil
	case "app.signature":
		return config.App.Signature, nil
	case "app.unsafe_html":
		return strconv.FormatBool(config.App.UnsafeHTML), nil

	case "email.delivery_method":
		return config.Email.DeliveryMethod, nil
	case "email.smtp.host":
		return config.Email.SMTP.Host, nil
	case "email.smtp.port":
		return strconv.Itoa(config.Email.SMTP.Port), nil
	case "email.smtp.username":
		return config.Email.SMTP.Username, nil
	case "email.smtp.password":
		return config.Email.SMTP.Password, nil
	case "email.smtp.encryption":
		return config.Email.SMTP.Encryption, nil
	case "email.smtp.insecure_skip_verify":
		return strconv.FormatBool(config.Email.SMTP.InsecureSkipVerify), nil
	case "email.resend.api_key":
		return config.Email.Resend.APIKey, nil

	case "storage.retention_days":
		return strconv.Itoa(config.Storage.RetentionDays), nil
	case "storage.cache_retention_days":
		return strconv.Itoa(config.Storage.CacheRetentionDays), nil
	case "storage.auto_save_drafts":
		return strconv.FormatBool(config.Storage.AutoSaveDrafts), nil
	case "storage.auto_save_interval_seconds":
		return strconv.Itoa(config.Storage.AutoSaveInterval), nil

	case "ui.theme":
		return config.UI.Theme, nil
	case "ui.show_cc_bcc":
		return strconv.FormatBool(config.UI.ShowCcBcc), nil
	case "ui.compact_mode":
		return strconv.FormatBool(config.UI.CompactMode), nil

	default:
		return "", fmt.Errorf("unknown configuration key: %s", key)
	}
}

func (cm *ConfigurationManager) GetConfigurationHistory(limit int, configKey string) ([]ConfigurationEntry, error) {
	return cm.db.GetConfigurationHistory(limit, configKey)
}

func (cm *ConfigurationManager) GetConfigurationStats() (*ConfigurationStats, error) {
	return cm.db.GetConfigurationStats()
}

func (cm *ConfigurationManager) LogAppStart(source string) error {
	description := "GoMail application started"
	metadata := fmt.Sprintf(`{"version": "%s", "start_time": "%s"}`,
		getAppVersion(), time.Now().Format(time.RFC3339))

	return cm.db.LogAppEvent("app_start", source, description, metadata)
}

func getAppVersion() string {
	if info, ok := debug.ReadBuildInfo(); ok {
		return info.Main.Version
	}
	return "unknown"
}
