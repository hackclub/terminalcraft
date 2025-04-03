package server

import (
	"fmt"
	"net/http"
	"quikdict/modes"
	"quikdict/sources"
	"quikdict/utils"
)

func Host(port int) error {
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		param, err := parseQueries(r)
		if err != nil {
			http.Error(w, err.Error(), http.StatusBadRequest)
			return
		}

		switch param.Mode {
		case utils.ModeDictionary:
			info, err := sources.GetFromDictionaryAPI(param.Word)
			if err != nil {
				http.Error(w, err.Error(), http.StatusBadRequest)
				return
			}
			_, err = fmt.Fprint(w, modes.GetDictionary(info, 80))
			if err != nil {
				http.Error(w, err.Error(), http.StatusBadRequest)
				return
			}
		case utils.ModeThesaurus:
			info, err := sources.GetFromDictionaryAPI(param.Word)
			if err != nil {
				http.Error(w, err.Error(), http.StatusBadRequest)
				return
			}
			_, err = fmt.Fprint(w, modes.GetThesaurus(info, 80))
			if err != nil {
				http.Error(w, err.Error(), http.StatusBadRequest)
				return
			}
		case utils.ModeTranslate:
			tran, og, err := sources.Translate(param.Word, param.Translation)
			if err != nil {
				http.Error(w, err.Error(), http.StatusBadRequest)
				return
			}
			_, err = fmt.Fprint(w, modes.GetTranslation(param.Word, tran, og, param.Translation))
			if err != nil {
				http.Error(w, err.Error(), http.StatusBadRequest)
				return
			}
		}
	})
	fmt.Printf("Started server on http://localhost:%d", port)
	return http.ListenAndServe(fmt.Sprintf(":%d", port), nil)
}
