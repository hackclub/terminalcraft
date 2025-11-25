package gowebspy

import (
	"regexp"
	"strings"
	"time"
)

type FilterOptions struct {
	MinStatusCode        int
	MaxStatusCode        int
	ServerContains       string
	HeaderKeyMustExist   []string
	HeaderValueMatches   map[string]string
	MinResponseTime      time.Duration
	MaxResponseTime      time.Duration
	SSLMustBeValid       bool
	SSLMinDaysRemaining  int
	ContentTypeMustMatch string
	IPMustMatch          string
	RequireIPv6          bool
	ExcludePattern       string
	IncludePattern       string
}

func NewFilterOptions() *FilterOptions {
	return &FilterOptions{
		MinStatusCode:       0,
		MaxStatusCode:       999,
		HeaderValueMatches:  make(map[string]string),
		MinResponseTime:     0,
		MaxResponseTime:     time.Hour,
		SSLMustBeValid:      false,
		SSLMinDaysRemaining: 0,
	}
}

func ApplyFilter(info *WebsiteInfo, opts *FilterOptions) bool {
	if opts.MinStatusCode > 0 && info.StatusCode < opts.MinStatusCode {
		return false
	}
	if opts.MaxStatusCode < 999 && info.StatusCode > opts.MaxStatusCode {
		return false
	}
	
	if opts.ServerContains != "" && !strings.Contains(strings.ToLower(info.ServerInfo), strings.ToLower(opts.ServerContains)) {
		return false
	}
	
	if info.ResponseTime < opts.MinResponseTime || info.ResponseTime > opts.MaxResponseTime {
		return false
	}
	
	for _, headerKey := range opts.HeaderKeyMustExist {
		if _, exists := info.Headers[headerKey]; !exists {
			return false
		}
	}
	
	for key, pattern := range opts.HeaderValueMatches {
		values, exists := info.Headers[key]
		if !exists {
			return false
		}
		
		matched := false
		for _, value := range values {
			if strings.Contains(value, pattern) {
				matched = true
				break
			}
		}
		
		if !matched {
			return false
		}
	}
	
	if info.SSLInfo != nil {
		if opts.SSLMustBeValid && !info.SSLInfo.Valid {
			return false
		}
		
		if opts.SSLMinDaysRemaining > 0 {
			// Fixed: Use time.Until instead of t.Sub(time.Now())
			daysLeft := int(time.Until(info.SSLInfo.Expiry).Hours() / 24)
			if daysLeft < opts.SSLMinDaysRemaining {
				return false
			}
		}
	} else if opts.SSLMustBeValid {
		return false
	}
	
	if opts.ContentTypeMustMatch != "" && !strings.Contains(info.ContentType, opts.ContentTypeMustMatch) {
		return false
	}
	
	if opts.IPMustMatch != "" {
		found := false
		for _, ip := range info.IP {
			if strings.Contains(ip, opts.IPMustMatch) {
				found = true
				break
			}
		}
		if !found {
			return false
		}
	}
	
	if opts.RequireIPv6 {
		hasIPv6 := false
		for _, ip := range info.IP {
			if strings.Contains(ip, ":") {
				hasIPv6 = true
				break
			}
		}
		if !hasIPv6 {
			return false
		}
	}
	
	if opts.ExcludePattern != "" {
		re, err := regexp.Compile(opts.ExcludePattern)
		if err == nil && (re.MatchString(info.Title) || re.MatchString(info.MetaDescription)) {
			return false
		}
	}
	
	if opts.IncludePattern != "" {
		re, err := regexp.Compile(opts.IncludePattern)
		if err == nil && !re.MatchString(info.Title) && !re.MatchString(info.MetaDescription) {
			return false
		}
	}
	
	return true
}

func BatchFilter(websites []*WebsiteInfo, opts *FilterOptions) []*WebsiteInfo {
	var filtered []*WebsiteInfo
	
	for _, site := range websites {
		if ApplyFilter(site, opts) {
			filtered = append(filtered, site)
		}
	}
	
	return filtered
}
