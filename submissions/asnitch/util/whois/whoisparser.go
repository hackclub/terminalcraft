package whois

import (
	"strings"
)

type WhoisData map[string]interface{}

func ParseWhoisResult(result string) WhoisData {
	whoisData := make(WhoisData)

	lines := strings.Split(result, "\n")
	var blocks []string
	var currentBlock []string

	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" {
			if len(currentBlock) > 0 {
				blocks = append(blocks, strings.Join(currentBlock, "\n"))
				currentBlock = nil
			}
			continue
		}
		currentBlock = append(currentBlock, line)
	}

	if len(currentBlock) > 0 {
		blocks = append(blocks, strings.Join(currentBlock, "\n"))
	}

	for _, block := range blocks {
		blockMap := parseBlock(block)
		var blockKey string

		// currently just this, but i can add the rest like as-sets when i add more to the app
		objects := []string{"role", "route", "inetnum"}

		for _, object := range objects {
			if _, ok := blockMap[object]; ok {
				blockKey = object
				break
			}
		}

		// if there is already an entry for this key, merge the blocks.
		if existing, exists := whoisData[blockKey]; exists {
			whoisData[blockKey] = appendToObject(existing, blockMap)
		} else {
			whoisData[blockKey] = blockMap
		}
	}

	// return nothing if the first map is empty, or the map inside the first map is empty
	// map[] or map[:map[]] are returned as nil
	if len(whoisData) == 0 {
		return nil
	}
	if len(whoisData) == 1 {
		for _, v := range whoisData {
			if v == nil || len(v.(map[string]any)) == 0 {
				return nil
			}
		}
	}

	return whoisData
}

// converts the string block into a map
func parseBlock(block string) map[string]any {
	result := make(map[string]any)
	lines := strings.Split(block, "\n")
	var currentKey string

	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" {
			continue
		}
		parts := strings.SplitN(line, ":", 2)
		if len(parts) == 2 {
			key := strings.TrimSpace(parts[0])
			value := strings.TrimSpace(parts[1])
			currentKey = key
			// if the key already exists, append to it.
			if existing, exists := result[key]; exists {
				result[key] = appendToObject(existing, value)
			} else {
				result[key] = value
			}
		} else if currentKey != "" {
			result[currentKey] = appendToObject(result[currentKey], line)
		}
	}

	return result
}

func appendToObject(existing any, value any) any {
	switch v := existing.(type) {
	case []any:
		return append(v, value)
	case []string:
		var res []any
		for _, s := range v {
			res = append(res, s)
		}
		res = append(res, value)
		return res
	case string:
		return []any{v, value}
	case map[string]any:
		// in case of merging two blockmaps
		return []any{v, value}
	default:
		return []any{v, value}
	}
}
