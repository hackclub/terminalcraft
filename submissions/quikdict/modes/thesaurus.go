package modes

import (
	"fmt"
	"quikdict/utils"
	"strings"
)

func GetThesaurus(info utils.WordInfo, tw int) string {
	printed := false
	text := ""

	for _, meaning := range info.Meanings {
		if len(meaning.Synonyms) == 0 {
			continue
		} else if len(meaning.Synonyms) > 0 && !printed {
			text += bold.Sprintln("Synonyms")
			printed = true
		}

		// print part of speech in green
		text += figureColor.Sprintf("%s\n", meaning.PartOfSpeech)

		synLen := len(meaning.Synonyms)
		for i, syn := range meaning.Synonyms {
			// print definition
			if i != synLen-1 {
				// print with continuing box characters if not the last definition
				text += fmt.Sprintf(" %s %s\n", dark.Sprint(continueBox), utils.WordWrap(syn, tw-4-margin, dark.Sprint(line)))
			} else {
				// print with ending box characters if the last definition
				text += fmt.Sprintf(" %s %s\n", dark.Sprint(endBox), utils.WordWrap(syn, tw-4-margin, s(4)))
			}
		}
		// new line to better separate figure of speech
		text += "\n"
	}

	printed = false
	for _, meaning := range info.Meanings {
		if len(meaning.Antonyms) == 0 {
			continue
		} else if len(meaning.Antonyms) > 0 && !printed {
			text += bold.Sprintln("Antonyms")
			printed = true
		}

		// print part of speech in green
		//goland:noinspection GoUnhandledErrorResult
		text += figureColor.Sprintf("%s\n", meaning.PartOfSpeech)

		antLen := len(meaning.Antonyms)
		for i, ant := range meaning.Antonyms {
			if i != antLen-1 {
				// print with continuing box characters if not the last definition
				text += fmt.Sprintf(" %s %s\n", dark.Sprint(continueBox), utils.WordWrap(ant, tw-4-margin, dark.Sprint(line)))
			} else {
				// print with ending box characters if the last definition
				text += fmt.Sprintf(" %s %s\n", dark.Sprint(endBox), utils.WordWrap(ant, tw-4-margin, s(4)))
			}
		}
		// new line to better separate figure of speech
		text += "\n"
	}
	text += dark.Sprintf("Source: %s\n", strings.Join(info.Sources, ", "))
	return text
}
