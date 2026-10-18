package filehandler

import (
	"fmt"
	"regexp"
	"strings"
	"time"
)

func TagValidator(tagString string) bool {
	tagString = strings.TrimSpace(tagString)
	if tagString == "" {
		return false
	}
	validPattern := regexp.MustCompile(`^(#\w+)(\s+#\w+)*$`)
	return validPattern.MatchString(tagString)
}

func ExtractTags(content string) []string {
	tagPattern := regexp.MustCompile(`#\w+`)
	tags := tagPattern.FindAllString(content, -1)
	for i, tag := range tags {
		tags[i] = strings.TrimPrefix(tag, "#")
	}
	return tags
}

func ParseInput(input string) []string {
	parts := strings.SplitN(input, "~", 2)
	if len(parts) != 2 {
		return []string{"", ""}
	}
	title := parts[0]
	dateStr := strings.TrimSuffix(parts[1], ".md")

	dateFields := strings.Fields(dateStr)
	if len(dateFields) < 5 {
		fmt.Println("Date string format is invalid")
		return []string{title, ""}
	}

	layout := "2006-01-02 15:04:05.999999 -0700"
	datetimeStr := fmt.Sprintf("%s %s %s", dateFields[0], dateFields[1], dateFields[2])
	t, err := time.Parse(layout, datetimeStr)
	if err != nil {
		fmt.Println("Parse error:", err)
		return []string{title, ""}
	}

	day := fmt.Sprintf("%02d", t.Day())
	month := t.Month().String()
	year := fmt.Sprintf("%d", t.Year())
	hour := t.Format("03")
	minute := t.Format("04")
	second := t.Format("05")
	ampm := t.Format("PM")
	timeStr := fmt.Sprintf("%s:%s:%s", hour, minute, second)
	timezone := dateFields[3]
	offset := dateFields[2]

	result := []string{day, month, year, timeStr, ampm, timezone, offset}
	dateString := strings.Join(result, " ")
	return []string{title, dateString}
}
