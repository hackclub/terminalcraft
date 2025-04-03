package modes

import "fmt"

func GetTranslation(word, translation, origin, destination string) string {
	return fmt.Sprintf("%s %s ⟶ %s %s", word, dark.Sprintf("(%s)", origin), bold.Sprint(translation), dark.Sprintf("(%s)", destination))
}
