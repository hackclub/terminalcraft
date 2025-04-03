package server

import (
	"errors"
	"github.com/fatih/color"
	"net/http"
	"quikdict/utils"
	"strings"
)

func parseQueries(r *http.Request) (utils.Params, error) {
	var params utils.Params
	params.Mode = utils.ModeDictionary

	if r.URL.Query().Has("th") {
		params.Mode = utils.ModeThesaurus
	}

	if r.URL.Query().Has("tr") {
		lc := r.URL.Query().Get("tr")
		if len(lc) != 2 || !utils.IsLetter(lc) {
			return utils.Params{}, errors.New("invalid language code")
		}
		params.Mode = utils.ModeTranslate
		params.Translation = lc
	}

	// Disable colors for browsers as they don't get rendered
	if strings.Contains(r.Header.Get("User-Agent"), "curl") {
		color.NoColor = false
	} else {
		color.NoColor = true
	}

	params.Word = r.URL.Path[1:]
	if params.Word == "" {
		return utils.Params{}, errors.New("no word was provided")
	}
	return params, nil
}
