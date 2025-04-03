package sources

import (
	"github.com/tidwall/gjson"
	"net/http"
	"quikdict/utils"
	"strings"
)

func Translate(word string, dest string) (string, string, error) {
	trans, err := utils.GetHttp("https://translate-pa.googleapis.com/v1/translateHtml", "POST", http.Header{
		"X-Goog-API-Key": []string{"AIzaSyATBXajvzQLTDHEQbcpq0Ihe0vWDHmO520"},
		"Content-Type":   []string{"application/json+protobuf"},
	}, strings.NewReader("[[[\""+word+"\"],\"auto\",\""+dest+"\"],\"wt_lib\"]"))
	if err != nil {
		return "", "", err
	}

	json := gjson.ParseBytes(trans)

	return json.Get("0.0").String(), json.Get("1.0").String(), nil
}
