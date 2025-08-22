package main

import (
	"database/sql"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

type SentEmail struct {
	ID           int       `json:"id"`
	From         string    `json:"from"`
	To           string    `json:"to"`
	Cc           string    `json:"cc,omitempty"`
	Bcc          string    `json:"bcc,omitempty"`
	Subject      string    `json:"subject"`
	Body         string    `json:"body"`
	Attachments  string    `json:"attachments,omitempty"`
	Method       string    `json:"method"`
	Status       string    `json:"status"`
	ErrorMessage string    `json:"error_message,omitempty"`
	SentAt       time.Time `json:"sent_at"`
	CreatedAt    time.Time `json:"created_at"`
}

type CacheEntry struct {
	ID        int       `json:"id"`
	Type      string    `json:"type"`
	Name      string    `json:"name"`
	From      string    `json:"from"`
	To        string    `json:"to"`
	Cc        string    `json:"cc,omitempty"`
	Bcc       string    `json:"bcc,omitempty"`
	Subject   string    `json:"subject"`
	Body      string    `json:"body"`
	Tags      string    `json:"tags,omitempty"`
	UpdatedAt time.Time `json:"updated_at"`
	CreatedAt time.Time `json:"created_at"`
}

type ConfigurationEntry struct {
	ID          int       `json:"id"`
	ConfigKey   string    `json:"config_key"`
	OldValue    string    `json:"old_value,omitempty"`
	NewValue    string    `json:"new_value"`
	ChangeType  string    `json:"change_type"`
	Source      string    `json:"source"`
	Description string    `json:"description,omitempty"`
	ChangedAt   time.Time `json:"changed_at"`
	CreatedAt   time.Time `json:"created_at"`
}

type AppEvent struct {
	ID          int       `json:"id"`
	EventType   string    `json:"event_type"`
	Source      string    `json:"source"`
	Description string    `json:"description"`
	Metadata    string    `json:"metadata,omitempty"`
	CreatedAt   time.Time `json:"created_at"`
}

type CachedInboxEmail struct {
	ID         int       `json:"id"`
	UID        uint32    `json:"uid"`
	Account    string    `json:"account"`
	Subject    string    `json:"subject"`
	From       string    `json:"from"`
	Date       time.Time `json:"date"`
	Size       uint32    `json:"size"`
	Flags      string    `json:"flags"`
	IsUnread   bool      `json:"is_unread"`
	IsAnswered bool      `json:"is_answered"`
	IsFlagged  bool      `json:"is_flagged"`
	Body       string    `json:"body"`
	FetchedAt  time.Time `json:"fetched_at"`
	CreatedAt  time.Time `json:"created_at"`
}

type ConfigurationStats struct {
	TotalConfigurations int
	LastConfigured      *time.Time
	ConfiguredToday     int
	MostActiveKey       string
	RecentChanges       []ConfigurationEntry
}

type DatabaseManager struct {
	db *sql.DB
}

func NewDatabaseManager() (*DatabaseManager, error) {
	dbPath := getDatabasePath()
	dbDir := filepath.Dir(dbPath)

	if err := os.MkdirAll(dbDir, 0755); err != nil {
		return nil, fmt.Errorf("creating database directory: %w", err)
	}

	db, err := sql.Open("sqlite3", dbPath)
	if err != nil {
		return nil, fmt.Errorf("opening database: %w", err)
	}

	dm := &DatabaseManager{db: db}
	if err := dm.initializeDatabase(); err != nil {
		db.Close()
		return nil, fmt.Errorf("initializing database: %w", err)
	}

	return dm, nil
}

func (dm *DatabaseManager) Close() error {
	if dm.db != nil {
		return dm.db.Close()
	}
	return nil
}

func getDatabasePath() string {
	homeDir, _ := os.UserHomeDir()
	return filepath.Join(homeDir, ".gomail", "gomail.db")
}

func (dm *DatabaseManager) initializeDatabase() error {

	sentEmailsSchema := `
	CREATE TABLE IF NOT EXISTS sent_emails (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		from_address TEXT NOT NULL,
		to_addresses TEXT NOT NULL,
		cc_addresses TEXT,
		bcc_addresses TEXT,
		subject TEXT NOT NULL,
		body TEXT NOT NULL,
		attachments TEXT,
		method TEXT NOT NULL,
		status TEXT NOT NULL DEFAULT 'sent',
		error_message TEXT,
		sent_at DATETIME NOT NULL,
		created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
	);`

	if _, err := dm.db.Exec(sentEmailsSchema); err != nil {
		return fmt.Errorf("creating sent_emails table: %w", err)
	}

	cacheSchema := `
	CREATE TABLE IF NOT EXISTS cache (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		type TEXT NOT NULL, -- 'draft', 'template', 'snippet'
		name TEXT NOT NULL,
		from_address TEXT,
		to_addresses TEXT,
		cc_addresses TEXT,
		bcc_addresses TEXT,
		subject TEXT,
		body TEXT,
		tags TEXT,
		updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
		created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
		UNIQUE(type, name)
	);`

	if _, err := dm.db.Exec(cacheSchema); err != nil {
		return fmt.Errorf("creating cache table: %w", err)
	}

	configHistorySchema := `
	CREATE TABLE IF NOT EXISTS configuration_history (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		config_key TEXT NOT NULL,
		old_value TEXT,
		new_value TEXT,
		change_type TEXT NOT NULL, -- 'create', 'update', 'delete', 'reset'
		source TEXT NOT NULL, -- 'ui', 'cli', 'file', 'migration'
		description TEXT,
		changed_at DATETIME NOT NULL,
		created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
	);`

	if _, err := dm.db.Exec(configHistorySchema); err != nil {
		return fmt.Errorf("creating configuration_history table: %w", err)
	}

	appEventsSchema := `
	CREATE TABLE IF NOT EXISTS app_events (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		event_type TEXT NOT NULL, -- 'app_start', 'config_change', 'reconfigure', 'migration', 'error'
		source TEXT NOT NULL, -- 'ui', 'cli', 'system'
		description TEXT NOT NULL,
		metadata TEXT, -- JSON metadata
		created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
	);`

	if _, err := dm.db.Exec(appEventsSchema); err != nil {
		return fmt.Errorf("creating app_events table: %w", err)
	}

	cachedInboxSchema := `
	CREATE TABLE IF NOT EXISTS cached_inbox_emails (
		id INTEGER PRIMARY KEY AUTOINCREMENT,
		uid INTEGER NOT NULL,
		account TEXT NOT NULL,
		subject TEXT NOT NULL,
		from_address TEXT NOT NULL,
		date DATETIME NOT NULL,
		size INTEGER NOT NULL,
		flags TEXT, -- JSON array of flags
		is_unread BOOLEAN NOT NULL DEFAULT 0,
		is_answered BOOLEAN NOT NULL DEFAULT 0,
		is_flagged BOOLEAN NOT NULL DEFAULT 0,
		body TEXT, -- Cached body content
		fetched_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
		created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
		UNIQUE(account, uid)
	);`

	if _, err := dm.db.Exec(cachedInboxSchema); err != nil {
		return fmt.Errorf("creating cached_inbox_emails table: %w", err)
	}

	indexes := []string{
		"CREATE INDEX IF NOT EXISTS idx_sent_emails_sent_at ON sent_emails(sent_at);",
		"CREATE INDEX IF NOT EXISTS idx_sent_emails_from ON sent_emails(from_address);",
		"CREATE INDEX IF NOT EXISTS idx_sent_emails_subject ON sent_emails(subject);",
		"CREATE INDEX IF NOT EXISTS idx_cache_type ON cache(type);",
		"CREATE INDEX IF NOT EXISTS idx_cache_updated_at ON cache(updated_at);",
		"CREATE INDEX IF NOT EXISTS idx_config_history_key ON configuration_history(config_key);",
		"CREATE INDEX IF NOT EXISTS idx_config_history_changed_at ON configuration_history(changed_at);",
		"CREATE INDEX IF NOT EXISTS idx_app_events_type ON app_events(event_type);",
		"CREATE INDEX IF NOT EXISTS idx_app_events_created_at ON app_events(created_at);",
		"CREATE INDEX IF NOT EXISTS idx_cached_inbox_emails_fetched_at ON cached_inbox_emails(fetched_at);",
		"CREATE INDEX IF NOT EXISTS idx_cached_inbox_emails_account ON cached_inbox_emails(account);",
		"CREATE INDEX IF NOT EXISTS idx_cached_inbox_emails_subject ON cached_inbox_emails(subject);",
	}

	for _, indexSQL := range indexes {
		if _, err := dm.db.Exec(indexSQL); err != nil {
			return fmt.Errorf("creating index: %w", err)
		}
	}

	return nil
}

func (dm *DatabaseManager) SaveSentEmail(email SentEmail) error {
	query := `
	INSERT INTO sent_emails (
		from_address, to_addresses, cc_addresses, bcc_addresses,
		subject, body, attachments, method, status, error_message, sent_at
	) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`

	_, err := dm.db.Exec(query,
		email.From, email.To, email.Cc, email.Bcc,
		email.Subject, email.Body, email.Attachments,
		email.Method, email.Status, email.ErrorMessage, email.SentAt,
	)

	if err != nil {
		return fmt.Errorf("saving sent email: %w", err)
	}

	return nil
}

func (dm *DatabaseManager) GetSentEmails(limit, offset int, fromDate *time.Time) ([]SentEmail, error) {
	query := `
	SELECT id, from_address, to_addresses, cc_addresses, bcc_addresses,
		   subject, body, attachments, method, status, error_message,
		   sent_at, created_at
	FROM sent_emails`

	args := []interface{}{}

	if fromDate != nil {
		query += " WHERE sent_at >= ?"
		args = append(args, fromDate)
	}

	query += " ORDER BY sent_at DESC"

	if limit > 0 {
		query += " LIMIT ?"
		args = append(args, limit)

		if offset > 0 {
			query += " OFFSET ?"
			args = append(args, offset)
		}
	}

	rows, err := dm.db.Query(query, args...)
	if err != nil {
		return nil, fmt.Errorf("querying sent emails: %w", err)
	}
	defer rows.Close()

	var emails []SentEmail
	for rows.Next() {
		var email SentEmail
		err := rows.Scan(
			&email.ID, &email.From, &email.To, &email.Cc, &email.Bcc,
			&email.Subject, &email.Body, &email.Attachments,
			&email.Method, &email.Status, &email.ErrorMessage,
			&email.SentAt, &email.CreatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("scanning sent email: %w", err)
		}
		emails = append(emails, email)
	}

	return emails, nil
}

func (dm *DatabaseManager) SaveCacheEntry(entry CacheEntry) error {
	query := `
	INSERT OR REPLACE INTO cache (
		type, name, from_address, to_addresses, cc_addresses, bcc_addresses,
		subject, body, tags, updated_at
	) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`

	_, err := dm.db.Exec(query,
		entry.Type, entry.Name, entry.From, entry.To, entry.Cc, entry.Bcc,
		entry.Subject, entry.Body, entry.Tags, time.Now(),
	)

	if err != nil {
		return fmt.Errorf("saving cache entry: %w", err)
	}

	return nil
}

func (dm *DatabaseManager) GetCacheEntries(entryType string) ([]CacheEntry, error) {
	query := `
	SELECT id, type, name, from_address, to_addresses, cc_addresses, bcc_addresses,
		   subject, body, tags, updated_at, created_at
	FROM cache
	WHERE type = ?
	ORDER BY updated_at DESC`

	rows, err := dm.db.Query(query, entryType)
	if err != nil {
		return nil, fmt.Errorf("querying cache entries: %w", err)
	}
	defer rows.Close()

	var entries []CacheEntry
	for rows.Next() {
		var entry CacheEntry
		err := rows.Scan(
			&entry.ID, &entry.Type, &entry.Name, &entry.From, &entry.To,
			&entry.Cc, &entry.Bcc, &entry.Subject, &entry.Body, &entry.Tags,
			&entry.UpdatedAt, &entry.CreatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("scanning cache entry: %w", err)
		}
		entries = append(entries, entry)
	}

	return entries, nil
}

func (dm *DatabaseManager) GetCacheEntry(entryType, name string) (*CacheEntry, error) {
	query := `
	SELECT id, type, name, from_address, to_addresses, cc_addresses, bcc_addresses,
		   subject, body, tags, updated_at, created_at
	FROM cache
	WHERE type = ? AND name = ?`

	var entry CacheEntry
	err := dm.db.QueryRow(query, entryType, name).Scan(
		&entry.ID, &entry.Type, &entry.Name, &entry.From, &entry.To,
		&entry.Cc, &entry.Bcc, &entry.Subject, &entry.Body, &entry.Tags,
		&entry.UpdatedAt, &entry.CreatedAt,
	)

	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil
		}
		return nil, fmt.Errorf("getting cache entry: %w", err)
	}

	return &entry, nil
}

func (dm *DatabaseManager) DeleteCacheEntry(entryType, name string) error {
	query := "DELETE FROM cache WHERE type = ? AND name = ?"
	_, err := dm.db.Exec(query, entryType, name)
	if err != nil {
		return fmt.Errorf("deleting cache entry: %w", err)
	}

	return nil
}

func (dm *DatabaseManager) LogConfigurationChange(configKey, oldValue, newValue, changeType, source, description string) error {
	query := `
	INSERT INTO configuration_history (
		config_key, old_value, new_value, change_type, source, description, changed_at
	) VALUES (?, ?, ?, ?, ?, ?, ?)`

	_, err := dm.db.Exec(query, configKey, oldValue, newValue, changeType, source, description, time.Now())
	if err != nil {
		return fmt.Errorf("logging configuration change: %w", err)
	}

	return nil
}

func (dm *DatabaseManager) LogAppEvent(eventType, source, description, metadata string) error {
	query := `
	INSERT INTO app_events (event_type, source, description, metadata)
	VALUES (?, ?, ?, ?)`

	_, err := dm.db.Exec(query, eventType, source, description, metadata)
	if err != nil {
		return fmt.Errorf("logging app event: %w", err)
	}

	return nil
}

func (dm *DatabaseManager) GetConfigurationHistory(limit int, configKey string) ([]ConfigurationEntry, error) {
	query := `
	SELECT id, config_key, old_value, new_value, change_type, source, description, changed_at, created_at
	FROM configuration_history`

	args := []interface{}{}

	if configKey != "" {
		query += " WHERE config_key = ?"
		args = append(args, configKey)
	}

	query += " ORDER BY changed_at DESC"

	if limit > 0 {
		query += " LIMIT ?"
		args = append(args, limit)
	}

	rows, err := dm.db.Query(query, args...)
	if err != nil {
		return nil, fmt.Errorf("querying configuration history: %w", err)
	}
	defer rows.Close()

	var entries []ConfigurationEntry
	for rows.Next() {
		var entry ConfigurationEntry
		var oldValue, newValue, description sql.NullString

		err := rows.Scan(
			&entry.ID, &entry.ConfigKey, &oldValue, &newValue,
			&entry.ChangeType, &entry.Source, &description,
			&entry.ChangedAt, &entry.CreatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("scanning configuration entry: %w", err)
		}

		entry.OldValue = oldValue.String
		entry.NewValue = newValue.String
		entry.Description = description.String

		entries = append(entries, entry)
	}

	return entries, nil
}

func (dm *DatabaseManager) GetAppEvents(limit int, eventType string) ([]AppEvent, error) {
	query := `
	SELECT id, event_type, source, description, metadata, created_at
	FROM app_events`

	args := []interface{}{}

	if eventType != "" {
		query += " WHERE event_type = ?"
		args = append(args, eventType)
	}

	query += " ORDER BY created_at DESC"

	if limit > 0 {
		query += " LIMIT ?"
		args = append(args, limit)
	}

	rows, err := dm.db.Query(query, args...)
	if err != nil {
		return nil, fmt.Errorf("querying app events: %w", err)
	}
	defer rows.Close()

	var events []AppEvent
	for rows.Next() {
		var event AppEvent
		var metadata sql.NullString

		err := rows.Scan(
			&event.ID, &event.EventType, &event.Source,
			&event.Description, &metadata, &event.CreatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("scanning app event: %w", err)
		}

		event.Metadata = metadata.String
		events = append(events, event)
	}

	return events, nil
}

func (dm *DatabaseManager) GetConfigurationStats() (*ConfigurationStats, error) {
	stats := &ConfigurationStats{}

	err := dm.db.QueryRow("SELECT COUNT(*) FROM configuration_history").Scan(&stats.TotalConfigurations)
	if err != nil {
		return nil, fmt.Errorf("getting total configurations: %w", err)
	}

	var lastConfigured sql.NullTime
	err = dm.db.QueryRow("SELECT MAX(changed_at) FROM configuration_history").Scan(&lastConfigured)
	if err != nil {
		return nil, fmt.Errorf("getting last configured time: %w", err)
	}
	if lastConfigured.Valid {
		stats.LastConfigured = &lastConfigured.Time
	}

	today := time.Now().Format("2006-01-02")
	err = dm.db.QueryRow("SELECT COUNT(*) FROM configuration_history WHERE DATE(changed_at) = ?", today).Scan(&stats.ConfiguredToday)
	if err != nil {
		return nil, fmt.Errorf("getting today's configurations: %w", err)
	}

	var mostActive sql.NullString
	err = dm.db.QueryRow(`
		SELECT config_key 
		FROM configuration_history 
		GROUP BY config_key 
		ORDER BY COUNT(*) DESC 
		LIMIT 1`).Scan(&mostActive)
	if err != nil && err != sql.ErrNoRows {
		return nil, fmt.Errorf("getting most active config key: %w", err)
	}
	stats.MostActiveKey = mostActive.String

	recentChanges, err := dm.GetConfigurationHistory(10, "")
	if err != nil {
		return nil, fmt.Errorf("getting recent changes: %w", err)
	}
	stats.RecentChanges = recentChanges

	return stats, nil
}

func (dm *DatabaseManager) GetSentEmailStats() (map[string]interface{}, error) {
	stats := make(map[string]interface{})

	var totalSent int
	err := dm.db.QueryRow("SELECT COUNT(*) FROM sent_emails WHERE status = 'sent'").Scan(&totalSent)
	if err != nil {
		return nil, fmt.Errorf("getting total sent emails: %w", err)
	}
	stats["total_sent"] = totalSent

	var totalFailed int
	err = dm.db.QueryRow("SELECT COUNT(*) FROM sent_emails WHERE status = 'failed'").Scan(&totalFailed)
	if err != nil {
		return nil, fmt.Errorf("getting total failed emails: %w", err)
	}
	stats["total_failed"] = totalFailed

	var sentToday int
	today := time.Now().Format("2006-01-02")
	err = dm.db.QueryRow("SELECT COUNT(*) FROM sent_emails WHERE DATE(sent_at) = ? AND status = 'sent'", today).Scan(&sentToday)
	if err != nil {
		return nil, fmt.Errorf("getting emails sent today: %w", err)
	}
	stats["sent_today"] = sentToday

	var lastSent sql.NullTime
	err = dm.db.QueryRow("SELECT MAX(sent_at) FROM sent_emails WHERE status = 'sent'").Scan(&lastSent)
	if err != nil && err != sql.ErrNoRows {
		return nil, fmt.Errorf("getting last sent time: %w", err)
	}
	if lastSent.Valid {
		stats["last_sent"] = lastSent.Time
	}

	return stats, nil
}

func (dm *DatabaseManager) SaveInboxEmails(account string, emails []InboxEmail) error {
	tx, err := dm.db.Begin()
	if err != nil {
		return fmt.Errorf("beginning transaction: %w", err)
	}
	defer tx.Rollback()

	stmt, err := tx.Prepare(`
		INSERT OR REPLACE INTO cached_inbox_emails 
		(uid, account, subject, from_address, date, size, flags, is_unread, is_answered, is_flagged, body, fetched_at)
		VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
	`)
	if err != nil {
		return fmt.Errorf("preparing statement: %w", err)
	}
	defer stmt.Close()

	for _, email := range emails {

		flagsJSON := ""
		if len(email.Flags) > 0 {
			flagsJSON = strings.Join(email.Flags, ",")
		}

		_, err = stmt.Exec(
			email.UID,
			account,
			email.Subject,
			email.From,
			email.Date,
			email.Size,
			flagsJSON,
			email.IsUnread,
			email.IsAnswered,
			email.IsFlagged,
			email.Body,
			time.Now(),
		)
		if err != nil {
			return fmt.Errorf("inserting inbox email UID %d: %w", email.UID, err)
		}
	}

	return tx.Commit()
}

func (dm *DatabaseManager) GetCachedInboxEmails(account string, limit, offset int) ([]InboxEmail, error) {
	query := `
		SELECT uid, subject, from_address, date, size, flags, is_unread, is_answered, is_flagged, body
		FROM cached_inbox_emails 
		WHERE account = ?
		ORDER BY date DESC
		LIMIT ? OFFSET ?
	`

	rows, err := dm.db.Query(query, account, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("querying cached inbox emails: %w", err)
	}
	defer rows.Close()

	var emails []InboxEmail
	for rows.Next() {
		var email InboxEmail
		var flagsStr string

		err := rows.Scan(
			&email.UID,
			&email.Subject,
			&email.From,
			&email.Date,
			&email.Size,
			&flagsStr,
			&email.IsUnread,
			&email.IsAnswered,
			&email.IsFlagged,
			&email.Body,
		)
		if err != nil {
			return nil, fmt.Errorf("scanning inbox email: %w", err)
		}

		if flagsStr != "" {
			email.Flags = strings.Split(flagsStr, ",")
		}

		emails = append(emails, email)
	}

	if err = rows.Err(); err != nil {
		return nil, fmt.Errorf("iterating inbox emails: %w", err)
	}

	return emails, nil
}

func (dm *DatabaseManager) GetCachedInboxEmailCount(account string) (int, error) {
	var count int
	err := dm.db.QueryRow("SELECT COUNT(*) FROM cached_inbox_emails WHERE account = ?", account).Scan(&count)
	if err != nil {
		return 0, fmt.Errorf("getting cached inbox email count: %w", err)
	}
	return count, nil
}

func (dm *DatabaseManager) UpdateInboxEmailBody(account string, uid uint32, body string) error {
	_, err := dm.db.Exec(
		"UPDATE cached_inbox_emails SET body = ?, fetched_at = ? WHERE account = ? AND uid = ?",
		body, time.Now(), account, uid,
	)
	if err != nil {
		return fmt.Errorf("updating inbox email body: %w", err)
	}
	return nil
}

func (dm *DatabaseManager) MarkInboxEmailAsRead(account string, uid uint32) error {
	_, err := dm.db.Exec(
		"UPDATE cached_inbox_emails SET is_unread = 0, fetched_at = ? WHERE account = ? AND uid = ?",
		time.Now(), account, uid,
	)
	if err != nil {
		return fmt.Errorf("marking inbox email as read: %w", err)
	}
	return nil
}

func (dm *DatabaseManager) CleanupOldInboxEmails(account string, retentionDays int) error {
	if retentionDays <= 0 {
		return nil
	}

	cutoffDate := time.Now().AddDate(0, 0, -retentionDays)
	_, err := dm.db.Exec(
		"DELETE FROM cached_inbox_emails WHERE account = ? AND fetched_at < ?",
		account, cutoffDate,
	)
	if err != nil {
		return fmt.Errorf("cleaning up old inbox emails: %w", err)
	}
	return nil
}

func (dm *DatabaseManager) CleanupOldEntries(sentEmailRetentionDays, cacheRetentionDays int) error {

	if sentEmailRetentionDays > 0 {
		cutoffDate := time.Now().AddDate(0, 0, -sentEmailRetentionDays)
		_, err := dm.db.Exec("DELETE FROM sent_emails WHERE sent_at < ?", cutoffDate)
		if err != nil {
			return fmt.Errorf("cleaning up old sent emails: %w", err)
		}
	}

	if cacheRetentionDays > 0 {
		cutoffDate := time.Now().AddDate(0, 0, -cacheRetentionDays)
		_, err := dm.db.Exec("DELETE FROM cache WHERE type = 'draft' AND updated_at < ?", cutoffDate)
		if err != nil {
			return fmt.Errorf("cleaning up old cache entries: %w", err)
		}
	}

	return nil
}

func (dm *DatabaseManager) GetCachedInboxEmailByUID(account string, uid uint32) (*InboxEmail, error) {
	query := `
		SELECT uid, subject, from_address, date, size, flags, is_unread, is_answered, is_flagged, body
		FROM cached_inbox_emails 
		WHERE account = ? AND uid = ?
		LIMIT 1
	`

	row := dm.db.QueryRow(query, account, uid)

	var email InboxEmail
	var flagsStr string

	err := row.Scan(
		&email.UID,
		&email.Subject,
		&email.From,
		&email.Date,
		&email.Size,
		&flagsStr,
		&email.IsUnread,
		&email.IsAnswered,
		&email.IsFlagged,
		&email.Body,
	)

	if err == sql.ErrNoRows {
		return nil, nil
	}

	if err != nil {
		return nil, fmt.Errorf("scanning inbox email: %w", err)
	}

	if flagsStr != "" {
		email.Flags = strings.Split(flagsStr, ",")
	}

	return &email, nil
}
