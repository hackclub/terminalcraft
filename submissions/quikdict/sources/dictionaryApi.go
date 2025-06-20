package sources

import (
	"github.com/tidwall/gjson"
	"quikdict/utils"
)

const apiUrl = "https://api.dictionaryapi.dev/api/v2/entries/en/"

func GetFromDictionaryAPI(word string) (utils.WordInfo, error) {
	var wordInfo utils.WordInfo

	// Get json
	bytes, err := utils.GetHttp(apiUrl+word, "GET", nil, nil)
	if err != nil {
		return wordInfo, err
	}

	wordInfo.Word = word

	// Get the first (and only) element of array
	json := gjson.GetBytes(bytes, "0")

	// Get phonetics
	for _, pho := range json.Get("phonetics").Array() {
		ipa := pho.Get("text").String()
		if ipa != "" { // && !slices.Contains(wordInfo.Phonetics, ipa) {
			wordInfo.Phonetics = append(wordInfo.Phonetics, ipa)
		}
	}

	// Get meanings
	for _, el := range json.Get("meanings").Array() {
		var meaning utils.Meaning
		meaning.PartOfSpeech = el.Get("partOfSpeech").String()

		for _, def := range el.Get("definitions").Array() {
			meaning.Definitions = append(meaning.Definitions, utils.Definition{
				Definition: def.Get("definition").String(),
				Example:    def.Get("example").String(),
			})
		}

		for _, syn := range el.Get("synonyms").Array() {
			meaning.Synonyms = append(meaning.Synonyms, syn.String())
		}

		for _, ant := range el.Get("antonyms").Array() {
			meaning.Antonyms = append(meaning.Antonyms, ant.String())
		}

		wordInfo.Meanings = append(wordInfo.Meanings, meaning)
	}

	// Get sources
	for _, source := range json.Get("sourceUrls").Array() {
		wordInfo.Sources = append(wordInfo.Sources, source.String())
	}

	return wordInfo, nil
}
