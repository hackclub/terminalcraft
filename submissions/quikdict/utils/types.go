package utils

type Definition struct {
	Definition string
	Example    string
}

type Meaning struct {
	PartOfSpeech string
	Definitions  []Definition
	Synonyms     []string
	Antonyms     []string
}

type WordInfo struct {
	Word      string
	Phonetics []string
	Meanings  []Meaning
	Sources   []string
}

type Params struct {
	Word        string
	Mode        Mode
	Translation string
	Host        bool
}

type Mode int

const (
	ModeDictionary Mode = iota
	ModeThesaurus
	ModeTranslate
)
