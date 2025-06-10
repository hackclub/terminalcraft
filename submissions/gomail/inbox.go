package main

import (
	"bytes"
	"crypto/sha256"
	"crypto/tls"
	"fmt"
	stdhtml "html"
	"io"
	"mime"
	"mime/multipart"
	"net"
	"regexp"
	"sort"
	"strings"
	"sync"
	"time"

	"github.com/emersion/go-imap/v2"
	"github.com/emersion/go-imap/v2/imapclient"
	"github.com/emersion/go-message"
	"github.com/microcosm-cc/bluemonday"
	"github.com/yuin/goldmark"
	"github.com/yuin/goldmark/extension"
	"github.com/yuin/goldmark/parser"
	gmhtml "github.com/yuin/goldmark/renderer/html"
	"golang.org/x/net/html"
)

type InboxEmail struct {
	UID        uint32
	Subject    string
	From       string
	Date       time.Time
	Size       uint32
	Flags      []string
	IsUnread   bool
	IsAnswered bool
	IsFlagged  bool
	Body       string
}

type InboxManager struct {
	client        *imapclient.Client
	host          string
	port          int
	username      string
	password      string
	encryption    string
	insecure      bool
	connected     bool
	dbManager     *DatabaseManager
	lastCacheTime time.Time
	cacheTimeout  time.Duration
	pool          *ConnectionPool
}

var PredefinedIMAPServers = map[string]struct {
	Host       string
	Port       int
	Encryption string
}{
	"gmail.com":      {Host: "imap.gmail.com", Port: 993, Encryption: "ssl"},
	"googlemail.com": {Host: "imap.gmail.com", Port: 993, Encryption: "ssl"},
	"outlook.com":    {Host: "imap-mail.outlook.com", Port: 993, Encryption: "ssl"},
	"hotmail.com":    {Host: "imap-mail.outlook.com", Port: 993, Encryption: "ssl"},
	"live.com":       {Host: "imap-mail.outlook.com", Port: 993, Encryption: "ssl"},
	"yahoo.com":      {Host: "imap.mail.yahoo.com", Port: 993, Encryption: "ssl"},
	"ymail.com":      {Host: "imap.mail.yahoo.com", Port: 993, Encryption: "ssl"},
	"aol.com":        {Host: "imap.aol.com", Port: 993, Encryption: "ssl"},
	"icloud.com":     {Host: "imap.mail.me.com", Port: 993, Encryption: "ssl"},
	"me.com":         {Host: "imap.mail.me.com", Port: 993, Encryption: "ssl"},
	"mac.com":        {Host: "imap.mail.me.com", Port: 993, Encryption: "ssl"},
	"protonmail.com": {Host: "127.0.0.1", Port: 1143, Encryption: "starttls"},
	"fastmail.com":   {Host: "imap.fastmail.com", Port: 993, Encryption: "ssl"},
	"zoho.com":       {Host: "imap.zoho.com", Port: 993, Encryption: "ssl"},
}

func NewInboxManager() *InboxManager {
	return &InboxManager{
		cacheTimeout: 5 * time.Minute,
	}
}

func (im *InboxManager) SetDatabaseManager(dbManager *DatabaseManager) {
	im.dbManager = dbManager
}

func (im *InboxManager) isCacheFresh() bool {
	if im.lastCacheTime.IsZero() {
		return false
	}
	return time.Since(im.lastCacheTime) < im.cacheTimeout
}

func (im *InboxManager) updateCacheTime() {
	im.lastCacheTime = time.Now()
}

func (im *InboxManager) ConfigureFromTOML(config *TOMLConfig) error {
	if config == nil {
		return fmt.Errorf("no configuration provided")
	}

	imapConfig := config.Email.IMAP
	smtpConfig := config.Email.SMTP

	if imapConfig.Host != "" && imapConfig.Username != "" && imapConfig.Password != "" {

		im.host = imapConfig.Host
		im.port = imapConfig.Port
		if im.port == 0 {
			im.port = 993
		}
		im.username = imapConfig.Username
		im.password = imapConfig.Password
		im.encryption = imapConfig.Encryption
		if im.encryption == "" {
			im.encryption = "ssl"
		}
		im.insecure = imapConfig.InsecureSkipVerify
		return nil
	}

	if imapConfig.AutoDetect && smtpConfig.Username != "" && smtpConfig.Password != "" {

		if strings.Contains(smtpConfig.Username, "@") {
			err := im.ConfigureFromEmail(smtpConfig.Username, smtpConfig.Password)
			if err != nil {
				return fmt.Errorf("auto-detect failed: %w", err)
			}
			return nil
		} else {
			return fmt.Errorf("SMTP username is not a valid email address for auto-detection")
		}
	}

	return fmt.Errorf("IMAP not configured - either configure manually or enable auto-detect with valid SMTP email settings")
}

func (im *InboxManager) ConfigureFromEmail(email, password string) error {
	im.username = email
	im.password = password

	parts := strings.Split(email, "@")
	if len(parts) != 2 {
		return fmt.Errorf("invalid email address format")
	}
	domain := strings.ToLower(parts[1])

	if config, exists := PredefinedIMAPServers[domain]; exists {
		im.host = config.Host
		im.port = config.Port
		im.encryption = config.Encryption
		return nil
	}

	possibleHosts := []string{
		"imap." + domain,
		"mail." + domain,
		domain,
	}

	for _, host := range possibleHosts {
		if im.testIMAPConnection(host, 993, "ssl") {
			im.host = host
			im.port = 993
			im.encryption = "ssl"
			return nil
		}
		if im.testIMAPConnection(host, 143, "starttls") {
			im.host = host
			im.port = 143
			im.encryption = "starttls"
			return nil
		}
	}

	return fmt.Errorf("could not auto-detect IMAP settings for domain: %s", domain)
}

func (im *InboxManager) SetManualConfig(host string, port int, encryption, username, password string) {
	im.host = host
	im.port = port
	im.encryption = encryption
	im.username = username
	im.password = password
}

func (im *InboxManager) testIMAPConnection(host string, port int, encryption string) bool {
	address := net.JoinHostPort(host, fmt.Sprintf("%d", port))

	var conn net.Conn
	var err error

	if encryption == "ssl" {
		conn, err = tls.Dial("tcp", address, &tls.Config{
			InsecureSkipVerify: true,
			ServerName:         host,
		})
	} else {
		conn, err = net.Dial("tcp", address)
	}

	if err != nil {
		return false
	}

	conn.Close()
	return true
}

func (im *InboxManager) Connect() error {
	if im.connected && im.client != nil {
		return nil
	}

	im.initializeConnectionPool()

	if im.pool != nil {
		client, err := im.pool.GetConnection()
		if err == nil {
			im.client = client
			im.connected = true
			return nil
		}

	}

	var client *imapclient.Client
	var err error

	address := net.JoinHostPort(im.host, fmt.Sprintf("%d", im.port))

	options := &imapclient.Options{}
	if im.encryption == "ssl" || im.encryption == "starttls" {
		options.TLSConfig = &tls.Config{
			InsecureSkipVerify: im.insecure,
			ServerName:         im.host,
		}
	}

	switch strings.ToLower(im.encryption) {
	case "ssl", "tls":
		client, err = imapclient.DialTLS(address, options)
	case "starttls":
		client, err = imapclient.DialStartTLS(address, options)
	case "none":
		client, err = imapclient.DialInsecure(address, options)
	default:
		client, err = imapclient.DialTLS(address, options)
	}

	if err != nil {
		return fmt.Errorf("connecting to IMAP server %s: %w", address, err)
	}

	if err := client.Login(im.username, im.password).Wait(); err != nil {
		client.Close()
		return fmt.Errorf("IMAP login failed: %w", err)
	}

	im.client = client
	im.connected = true
	return nil
}

func (im *InboxManager) Close() error {
	if im.client != nil {
		var err error

		if im.pool != nil {
			im.pool.ReturnConnection(im.client)
		} else {
			err = im.client.Close()
		}

		im.client = nil
		im.connected = false
		return err
	}
	return nil
}

func (im *InboxManager) Shutdown() {
	if im.client != nil {
		im.client.Close()
		im.client = nil
		im.connected = false
	}
	if im.pool != nil {
		im.pool.Close()
		im.pool = nil
	}
}

func (im *InboxManager) FetchInboxEmails(limit int, offset int) ([]InboxEmail, error) {

	if im.dbManager != nil {
		cachedEmails, err := im.dbManager.GetCachedInboxEmails(im.username, limit, offset)
		if err == nil && len(cachedEmails) > 0 {

			if im.isCacheFresh() {
				return cachedEmails, nil
			}
		}
	}

	emails, err := im.fetchFromServer(limit, offset)
	if err != nil {

		if im.dbManager != nil {
			cachedEmails, cacheErr := im.dbManager.GetCachedInboxEmails(im.username, limit, offset)
			if cacheErr == nil && len(cachedEmails) > 0 {
				return cachedEmails, nil
			}
		}
		return nil, err
	}

	if im.dbManager != nil {
		go func() {

			if saveErr := im.dbManager.SaveInboxEmails(im.username, emails); saveErr != nil {

				fmt.Printf("Warning: Failed to cache inbox emails: %v\n", saveErr)
			}
		}()
	}

	im.updateCacheTime()

	return emails, nil
}

func (im *InboxManager) fetchFromServer(limit int, offset int) ([]InboxEmail, error) {
	if err := im.Connect(); err != nil {
		return nil, err
	}

	mailbox, err := im.client.Select("INBOX", nil).Wait()
	if err != nil {
		return nil, fmt.Errorf("selecting INBOX: %w", err)
	}

	if mailbox.NumMessages == 0 {
		return []InboxEmail{}, nil
	}

	totalMessages := int(mailbox.NumMessages)
	start := totalMessages - offset - limit + 1
	end := totalMessages - offset

	if start < 1 {
		start = 1
	}
	if end < 1 {
		end = 1
	}
	if end > totalMessages {
		end = totalMessages
	}
	if start > totalMessages {
		start = totalMessages
	}
	if start > end {
		return []InboxEmail{}, nil
	}

	fmt.Printf("Debug: totalMessages=%d, start=%d, end=%d, offset=%d, limit=%d\n",
		totalMessages, start, end, offset, limit)

	seqSet := imap.SeqSetNum(uint32(start))
	if start != end {
		seqSet.AddRange(uint32(start), uint32(end))
	}

	fetchOptions := &imap.FetchOptions{
		Flags:      true,
		Envelope:   true,
		RFC822Size: true,
		UID:        true,
	}

	messages, err := im.client.Fetch(seqSet, fetchOptions).Collect()
	if err != nil {
		return nil, fmt.Errorf("fetching messages: %w", err)
	}

	var emails []InboxEmail
	for _, msg := range messages {
		if msg.Envelope == nil {
			continue
		}

		email := InboxEmail{
			UID:     uint32(msg.UID),
			Subject: msg.Envelope.Subject,
			Date:    msg.Envelope.Date,
			Size:    uint32(msg.RFC822Size),
		}

		if len(msg.Envelope.From) > 0 {
			from := msg.Envelope.From[0]
			if from.Name != "" {
				email.From = fmt.Sprintf("%s <%s@%s>", from.Name, from.Mailbox, from.Host)
			} else {
				email.From = fmt.Sprintf("%s@%s", from.Mailbox, from.Host)
			}
		}

		email.IsUnread = true
		for _, flag := range msg.Flags {
			switch flag {
			case imap.FlagSeen:
				email.IsUnread = false
			case imap.FlagAnswered:
				email.IsAnswered = true
			case imap.FlagFlagged:
				email.IsFlagged = true
			}
			email.Flags = append(email.Flags, string(flag))
		}

		emails = append(emails, email)
	}

	sort.Slice(emails, func(i, j int) bool {
		return emails[i].Date.After(emails[j].Date)
	})

	return emails, nil
}

func (im *InboxManager) FetchEmailBody(uid uint32) (string, error) {

	if body, exists := getCachedEmailBody(uid); exists {
		return body, nil
	}

	if im.dbManager != nil {
		if cachedEmail, err := im.dbManager.GetCachedInboxEmailByUID(im.username, uid); err == nil && cachedEmail != nil && cachedEmail.Body != "" {

			setCachedEmailBody(uid, cachedEmail.Body)
			return cachedEmail.Body, nil
		}
	}

	body, err := im.fetchEmailBodyFromServer(uid)
	if err != nil {
		return "", err
	}

	setCachedEmailBody(uid, body)

	if im.dbManager != nil {
		go func() {
			if saveErr := im.dbManager.UpdateInboxEmailBody(im.username, uid, body); saveErr != nil {
				fmt.Printf("Warning: Failed to cache email body: %v\n", saveErr)
			}
		}()
	}

	return body, nil
}

func (im *InboxManager) fetchEmailBodyFromServer(uid uint32) (string, error) {
	if err := im.Connect(); err != nil {
		return "", err
	}

	_, err := im.client.Select("INBOX", nil).Wait()
	if err != nil {
		return "", fmt.Errorf("selecting INBOX: %w", err)
	}

	uidSet := imap.UIDSetNum(imap.UID(uid))

	searchCriteria := &imap.SearchCriteria{
		UID: []imap.UIDSet{uidSet},
	}

	searchData, err := im.client.Search(searchCriteria, nil).Wait()
	if err != nil {
		return "", fmt.Errorf("searching for email UID %d: %w", uid, err)
	}

	seqNums := searchData.AllSeqNums()
	if len(seqNums) == 0 {
		return "", fmt.Errorf("email with UID %d not found", uid)
	}

	seqSet := imap.SeqSetNum(seqNums[0])

	fetchOptions := &imap.FetchOptions{
		BodySection: []*imap.FetchItemBodySection{
			{Specifier: imap.PartSpecifierNone},
		},
		UID:      true,
		Envelope: true,
	}

	messages, err := im.client.Fetch(seqSet, fetchOptions).Collect()
	if err != nil {
		return "", fmt.Errorf("fetching email body: %w", err)
	}

	if len(messages) == 0 {
		return "", fmt.Errorf("email with UID %d not found", uid)
	}

	msg := messages[0]

	bodySection := msg.FindBodySection(&imap.FetchItemBodySection{
		Specifier: imap.PartSpecifierNone,
	})

	if len(bodySection) == 0 {
		return "", fmt.Errorf("email body not available")
	}

	rawEmail := bytes.NewReader(bodySection)
	entity, err := message.Read(rawEmail)
	if err != nil {
		return "", fmt.Errorf("parsing email message: %w", err)
	}

	body, err := im.extractEmailBody(entity)
	if err != nil {
		return "", fmt.Errorf("extracting email body: %w", err)
	}

	return body, nil
}

func (im *InboxManager) extractEmailBody(entity *message.Entity) (string, error) {

	contentType, params, err := mime.ParseMediaType(entity.Header.Get("Content-Type"))
	if err != nil {
		contentType = "text/plain"
	}

	switch {
	case strings.HasPrefix(contentType, "multipart/"):
		return im.handleMultipartEmail(entity, params)
	case contentType == "text/html":
		return im.handleHTMLEmail(entity)
	case contentType == "text/plain":
		return im.handlePlainTextEmail(entity)
	default:

		return im.handlePlainTextEmail(entity)
	}
}

func (im *InboxManager) handleMultipartEmail(entity *message.Entity, params map[string]string) (string, error) {
	boundary := params["boundary"]
	if boundary == "" {
		return "", fmt.Errorf("multipart message without boundary")
	}

	mr := multipart.NewReader(entity.Body, boundary)

	var htmlContent, plainContent string
	var attachments []string

	for {
		part, err := mr.NextPart()
		if err == io.EOF {
			break
		}
		if err != nil {
			return "", fmt.Errorf("reading multipart: %w", err)
		}

		partContentType := part.Header.Get("Content-Type")
		mediaType, _, err := mime.ParseMediaType(partContentType)
		if err != nil {
			mediaType = "text/plain"
		}

		switch mediaType {
		case "text/html":
			htmlBytes, err := io.ReadAll(part)
			if err != nil {
				continue
			}
			htmlContent = string(htmlBytes)
		case "text/plain":
			plainBytes, err := io.ReadAll(part)
			if err != nil {
				continue
			}
			plainContent = string(plainBytes)
		default:

			disposition := part.Header.Get("Content-Disposition")
			if strings.Contains(disposition, "attachment") {
				filename := extractFilename(disposition)
				if filename != "" {
					attachments = append(attachments, fmt.Sprintf("[Attachment: %s]", filename))
				}
			}
		}
	}

	var result strings.Builder

	if htmlContent != "" {

		processedHTML, err := im.processHTMLContent(htmlContent)
		if err == nil {
			result.WriteString(processedHTML)
		} else {

			plainFromHTML, err := htmlToText(htmlContent)
			if err == nil {
				result.WriteString(plainFromHTML)
			} else {
				result.WriteString(htmlContent)
			}
		}
	} else if plainContent != "" {

		processedPlain, err := im.processPlainTextContent(plainContent)
		if err == nil {
			result.WriteString(processedPlain)
		} else {
			result.WriteString(plainContent)
		}
	}

	if len(attachments) > 0 {
		result.WriteString("\n\n--- Attachments ---\n")
		for _, attachment := range attachments {
			result.WriteString(attachment + "\n")
		}
	}

	if result.Len() == 0 {
		return "No readable content found in this email.", nil
	}

	return result.String(), nil
}

func (im *InboxManager) handleHTMLEmail(entity *message.Entity) (string, error) {
	htmlBytes, err := io.ReadAll(entity.Body)
	if err != nil {
		return "", fmt.Errorf("reading HTML content: %w", err)
	}

	htmlContent := string(htmlBytes)
	return im.processHTMLContent(htmlContent)
}

func (im *InboxManager) handlePlainTextEmail(entity *message.Entity) (string, error) {
	plainBytes, err := io.ReadAll(entity.Body)
	if err != nil {
		return "", fmt.Errorf("reading plain text content: %w", err)
	}

	plainContent := string(plainBytes)
	return im.processPlainTextContent(plainContent)
}

func (im *InboxManager) processHTMLContent(htmlContent string) (string, error) {

	if cached, exists := getCachedHTMLProcessing(htmlContent); exists {
		return cached, nil
	}

	policy := bluemonday.UGCPolicy()
	policy.AllowElements("br", "p", "div", "span", "strong", "em", "u", "i", "b", "a", "ul", "ol", "li", "blockquote", "pre", "code", "h1", "h2", "h3", "h4", "h5", "h6", "table", "thead", "tbody", "tr", "td", "th")
	policy.AllowAttrs("href").OnElements("a")
	policy.AllowAttrs("src", "alt").OnElements("img")

	sanitizedHTML := policy.Sanitize(htmlContent)

	plainText, err := htmlToText(sanitizedHTML)
	if err != nil {
		return "", fmt.Errorf("converting HTML to text: %w", err)
	}

	setCachedHTMLProcessing(htmlContent, plainText)

	return plainText, nil
}

func (im *InboxManager) processPlainTextContent(plainContent string) (string, error) {

	if im.looksLikeMarkdown(plainContent) {

		md := goldmark.New(
			goldmark.WithExtensions(extension.GFM),
			goldmark.WithParserOptions(
				parser.WithAutoHeadingID(),
			),
			goldmark.WithRendererOptions(
				gmhtml.WithHardWraps(),
				gmhtml.WithXHTML(),
			),
		)

		var buf bytes.Buffer
		if err := md.Convert([]byte(plainContent), &buf); err == nil {

			return im.processHTMLContent(buf.String())
		}
	}

	return plainContent, nil
}

func (im *InboxManager) looksLikeMarkdown(content string) bool {
	markdownIndicators := []string{
		"#", "##", "###",
		"**", "__",
		"*", "_",
		"```", "`",
		"- ", "* ", "+ ",
		"[", "](", "![",
		">",
	}

	for _, indicator := range markdownIndicators {
		if strings.Contains(content, indicator) {
			return true
		}
	}
	return false
}

func extractFilename(disposition string) string {
	_, params, err := mime.ParseMediaType(disposition)
	if err != nil {
		return ""
	}
	return params["filename"]
}

func (im *InboxManager) MarkAsRead(uid uint32) error {
	if err := im.Connect(); err != nil {
		return err
	}

	return nil
}

func (im *InboxManager) IsConfigured() bool {
	return im.username != "" && im.password != "" && im.host != ""
}

func htmlToText(htmlContent string) (string, error) {
	if htmlContent == "" {
		return "", nil
	}

	doc, err := html.Parse(strings.NewReader(htmlContent))
	if err != nil {
		return "", fmt.Errorf("failed to parse HTML: %w", err)
	}

	var buf strings.Builder
	var extractText func(*html.Node)

	extractText = func(n *html.Node) {
		if n.Type == html.TextNode {
			text := strings.TrimSpace(n.Data)
			if text != "" {
				buf.WriteString(text)
				buf.WriteString(" ")
			}
		}

		if n.Type == html.ElementNode {
			switch n.Data {
			case "p", "div", "br", "h1", "h2", "h3", "h4", "h5", "h6":
				buf.WriteString("\n")
			case "li":
				buf.WriteString("\n• ")
			}
		}

		for c := n.FirstChild; c != nil; c = c.NextSibling {
			extractText(c)
		}

		if n.Type == html.ElementNode {
			switch n.Data {
			case "p", "div", "h1", "h2", "h3", "h4", "h5", "h6":
				buf.WriteString("\n")
			}
		}
	}

	extractText(doc)

	text := buf.String()

	re := regexp.MustCompile(`\s+`)
	text = re.ReplaceAllString(text, " ")

	re = regexp.MustCompile(`\n\s*\n\s*\n`)
	text = re.ReplaceAllString(text, "\n\n")

	text = stdhtml.UnescapeString(text)

	return strings.TrimSpace(text), nil
}

type ConnectionPool struct {
	connections chan *imapclient.Client
	maxSize     int
	config      ConnectionConfig
}

type ConnectionConfig struct {
	Host       string
	Port       int
	Username   string
	Password   string
	Encryption string
	Insecure   bool
}

func NewConnectionPool(config ConnectionConfig, maxSize int) *ConnectionPool {
	return &ConnectionPool{
		connections: make(chan *imapclient.Client, maxSize),
		maxSize:     maxSize,
		config:      config,
	}
}

func (cp *ConnectionPool) GetConnection() (*imapclient.Client, error) {
	select {
	case client := <-cp.connections:

		if client != nil {

			if _, err := client.Capability().Wait(); err == nil {
				return client, nil
			}

			client.Close()
		}
	default:

	}

	return cp.createConnection()
}

func (cp *ConnectionPool) ReturnConnection(client *imapclient.Client) {
	if client == nil {
		return
	}

	select {
	case cp.connections <- client:

	default:

		client.Close()
	}
}

func (cp *ConnectionPool) createConnection() (*imapclient.Client, error) {
	address := net.JoinHostPort(cp.config.Host, fmt.Sprintf("%d", cp.config.Port))

	options := &imapclient.Options{}
	if cp.config.Encryption == "ssl" || cp.config.Encryption == "starttls" {
		options.TLSConfig = &tls.Config{
			InsecureSkipVerify: cp.config.Insecure,
			ServerName:         cp.config.Host,
		}
	}

	var client *imapclient.Client
	var err error

	switch strings.ToLower(cp.config.Encryption) {
	case "ssl", "tls":
		client, err = imapclient.DialTLS(address, options)
	case "starttls":
		client, err = imapclient.DialStartTLS(address, options)
	case "none":
		client, err = imapclient.DialInsecure(address, options)
	default:
		client, err = imapclient.DialTLS(address, options)
	}

	if err != nil {
		return nil, fmt.Errorf("connecting to IMAP server %s: %w", address, err)
	}

	if err := client.Login(cp.config.Username, cp.config.Password).Wait(); err != nil {
		client.Close()
		return nil, fmt.Errorf("IMAP login failed: %w", err)
	}

	return client, nil
}

func (cp *ConnectionPool) Close() {
	close(cp.connections)
	for client := range cp.connections {
		if client != nil {
			client.Close()
		}
	}
}

func (im *InboxManager) initializeConnectionPool() {
	if im.pool == nil && im.host != "" && im.username != "" && im.password != "" {
		config := ConnectionConfig{
			Host:       im.host,
			Port:       im.port,
			Username:   im.username,
			Password:   im.password,
			Encryption: im.encryption,
			Insecure:   im.insecure,
		}
		im.pool = NewConnectionPool(config, 3)
	}
}

var htmlProcessingCache = make(map[string]string)
var htmlCacheMutex sync.RWMutex

func getCachedHTMLProcessing(htmlContent string) (string, bool) {

	hash := fmt.Sprintf("%x", sha256.Sum256([]byte(htmlContent)))

	htmlCacheMutex.RLock()
	defer htmlCacheMutex.RUnlock()

	result, exists := htmlProcessingCache[hash]
	return result, exists
}

func setCachedHTMLProcessing(htmlContent, result string) {

	hash := fmt.Sprintf("%x", sha256.Sum256([]byte(htmlContent)))

	htmlCacheMutex.Lock()
	defer htmlCacheMutex.Unlock()

	if len(htmlProcessingCache) > 100 {

		htmlProcessingCache = make(map[string]string)
	}

	htmlProcessingCache[hash] = result
}

var emailBodyCache = make(map[uint32]string)
var emailBodyCacheMutex sync.RWMutex

func getCachedEmailBody(uid uint32) (string, bool) {
	emailBodyCacheMutex.RLock()
	defer emailBodyCacheMutex.RUnlock()

	body, exists := emailBodyCache[uid]
	return body, exists
}

func setCachedEmailBody(uid uint32, body string) {
	emailBodyCacheMutex.Lock()
	defer emailBodyCacheMutex.Unlock()

	if len(emailBodyCache) > 50 {

		count := 0
		for key := range emailBodyCache {
			if count > 25 {
				break
			}
			delete(emailBodyCache, key)
			count++
		}
	}

	emailBodyCache[uid] = body
}

func (im *InboxManager) PrefetchEmailBodies(emails []InboxEmail, maxConcurrent int) {
	if len(emails) == 0 || im.dbManager == nil {
		return
	}

	semaphore := make(chan struct{}, maxConcurrent)

	for _, email := range emails {
		go func(uid uint32) {
			semaphore <- struct{}{}
			defer func() { <-semaphore }()

			cachedEmails, err := im.dbManager.GetCachedInboxEmails(im.username, 1000, 0)
			if err == nil {
				for _, cached := range cachedEmails {
					if cached.UID == uid && cached.Body != "" {
						return
					}
				}
			}

			body, err := im.fetchEmailBodyFromServer(uid)
			if err != nil {
				return
			}

			if saveErr := im.dbManager.UpdateInboxEmailBody(im.username, uid, body); saveErr != nil {
				fmt.Printf("Warning: Failed to cache prefetched email body: %v\n", saveErr)
			}
		}(email.UID)
	}
}
