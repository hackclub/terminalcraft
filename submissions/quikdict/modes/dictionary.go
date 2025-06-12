package modes

import (
	"fmt"
	"quikdict/utils"
	"strings"
)

func GetDictionary(info utils.WordInfo, tw int) string {
	text := bold.Sprint(info.Word)
	// print phonetics in a dark color with brackets and the phonetics in italic
	if len(info.Phonetics) > 0 {
		text += dark.Sprintf(" [%s]\n", strings.Join(info.Phonetics, ", "))
	} else {
		text += "\n"
	}

	// print meaning
	for _, meaning := range info.Meanings {
		// print part of speech in green
		text += figureColor.Sprintf("%s\n", meaning.PartOfSpeech)

		defLen := len(meaning.Definitions)
		for i, def := range meaning.Definitions {

			// print definition
			if i != defLen-1 {
				// print with continuing box characters if not the last definition
				text += fmt.Sprintf(" %s %s\n", dark.Sprint(continueBox), utils.WordWrap(def.Definition, tw-4-margin, dark.Sprint(line)))
				if def.Example != "" {
					text += darkItalic.Sprintf("%s %s %s\n", line, endBox, utils.WordWrap(def.Example, tw-8-margin, line+s(4)))
				}

			} else {
				// print with ending box characters if the last definition
				text += fmt.Sprintf(" %s %s\n", dark.Sprint(endBox), utils.WordWrap(def.Definition, tw-4-margin, s(4)))
				if def.Example != "" {
					text += darkItalic.Sprintf("%s%s %s\n", s(5), endBox, utils.WordWrap(def.Example, tw-8-margin, s(8)))
				}
			}
		}
		// new line to better separate figure of speech
		text += "\n"
	}
	text += dark.Sprintf("Source: %s\n", strings.Join(info.Sources, ", "))
	return text
}
