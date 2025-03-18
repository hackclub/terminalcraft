package cli

import (
	"errors"
	"fmt"
	"os"
	"quikdict/utils"
)

func Parse(args []string) (utils.Params, error) {
	var params utils.Params
	params.Mode = utils.ModeDictionary
	skip := false
	for i, arg := range args {
		if skip {
			skip = false
			continue
		}
		switch arg {
		case "-tr", "--translate":
			if len(args) == i+1 || len(args[i+1]) != 2 || !utils.IsLetter(args[i+1]) {
				return utils.Params{}, errors.New("invalid language code")
			}
			params.Translation = args[i+1]
			params.Mode = utils.ModeTranslate
			skip = true

		case "-th", "--thesaurus":
			params.Mode = utils.ModeThesaurus

		case "-h", "--help":
			fmt.Println(HelpStr)
			os.Exit(0)

		case "-s", "--serve":
			params.Host = true

		default:
			params.Word = arg
		}
	}
	if params.Word == "" && !params.Host {
		return utils.Params{}, errors.New("no word was provided")
	}
	return params, nil
}
