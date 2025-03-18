package cli

import (
	"fmt"
	"os"
)

var HelpStr = fmt.Sprintf(`Usage: %s [word] [options]

Options:
  -th, --thesaurus   	Print synonyms and antonyms
  -tr, --translate <LC>	Translate the word to another language, LC is the 2 letter language code (like en, it)
  -h, --help          	Print this help message
  -s, --serve			Launch the server on port 8246`, os.Args[0])
