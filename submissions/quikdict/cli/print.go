package cli

import (
	"quikdict/modes"
	"quikdict/sources"
	"quikdict/utils"
)

func Print(args utils.Params, tw int) error {
	switch args.Mode {
	case utils.ModeDictionary:
		info, err := sources.GetFromDictionaryAPI(args.Word)
		if err != nil {
			return err
		}
		print(modes.GetDictionary(info, tw))
	case utils.ModeThesaurus:
		info, err := sources.GetFromDictionaryAPI(args.Word)
		if err != nil {
			return err
		}
		print(modes.GetThesaurus(info, tw))
	case utils.ModeTranslate:
		tran, og, err := sources.Translate(args.Word, args.Translation)
		if err != nil {
			return err
		}
		print(modes.GetTranslation(args.Word, tran, og, args.Translation))
	}
	return nil
}
