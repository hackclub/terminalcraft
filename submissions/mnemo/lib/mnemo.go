package lib

import (
	"crypto/sha256"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"os"
	"path"
	"strings"

	"github.com/gtank/cryptopasta"
	"github.com/kkrishguptaa/mnemo/util"
)

type Store struct {
	Name string    `json:"name"`
	Data []Snippet `json:"data"`
}

type Snippet struct {
	Id        string `json:"id"`
	Value     string `json:"value"`
	Encrypted bool   `json:"encrypted"`
}

func Encrypt(value string, password string) string {
	password = strings.TrimSpace(password)
	hash := sha256.Sum256([]byte(password))
	cipher := util.ErrorHandler(cryptopasta.Encrypt([]byte(value), &hash))

	return base64.StdEncoding.EncodeToString(cipher)
}

func Decrypt(value string, password string) string {
	password = strings.TrimSpace(password)
	hash := sha256.Sum256([]byte(password))

	decoded, err := base64.StdEncoding.DecodeString(value)
	util.ErrorPrinter(err) // or panic(err), or your own handler

	decrypted := util.ErrorHandler(cryptopasta.Decrypt(decoded, &hash))
	return string(decrypted)
}

func FetchStore(stores string, name string, defaultStore string) Store {
	file := path.Join(stores, name+".json")

	if _, err := os.Stat(stores); os.IsNotExist(err) {
		util.ErrorPrinter(os.MkdirAll(stores, 0755))
	}

	if _, err := os.Stat(file); os.IsNotExist(err) {
		if name != defaultStore {
			util.ErrorPrinter(fmt.Errorf("store %s does not exist", name))
			return Store{}
		}

		CreateStore(stores, name, defaultStore)
	}

	bytes := util.ErrorHandler(os.ReadFile(file))

	store := Store{Name: name}
	util.ErrorPrinter(json.Unmarshal(bytes, &store))

	return store
}

func CreateStore(stores string, name string, defaultStore string) Store {
	if name == "" {
		util.ErrorPrinter(fmt.Errorf("store name cannot be empty"))
		return Store{}
	}

	if _, err := os.Stat(stores); os.IsNotExist(err) {
		util.ErrorPrinter(os.MkdirAll(stores, 0755))
	}

	file := path.Join(stores, name+".json")

	if _, err := os.Stat(file); !os.IsNotExist(err) {
		util.ErrorPrinter(fmt.Errorf("store %s already exists", name))
		return Store{}
	}

	store := Store{Name: name, Data: []Snippet{}}
	bytes, err := json.Marshal(store)
	util.ErrorPrinter(err)

	util.ErrorPrinter(os.WriteFile(file, bytes, 0644))

	return store
}

func ListStores(stores string, defaultStore string) []string {
	if _, err := os.Stat(stores); os.IsNotExist(err) {
		util.ErrorPrinter(os.MkdirAll(stores, 0755))
	}

	files, err := os.ReadDir(stores)
	util.ErrorPrinter(err)

	var storeNames []string
	for _, file := range files {
		if !file.IsDir() && path.Ext(file.Name()) == ".json" {
			storeNames = append(storeNames, file.Name()[:len(strings.Split(file.Name(), ".")[0])])
		}
	}

	return storeNames
}

func WriteStore(stores string, name string, snippets []Snippet) {
	file := path.Join(stores, name+".json")

	store := Store{Name: name, Data: snippets}

	bytes := util.ErrorHandler(json.Marshal(store))

	util.ErrorPrinter(os.WriteFile(file, bytes, 0644))
}

func DeleteStore(stores string, name string) {
	file := path.Join(stores, name+".json")

	if _, err := os.Stat(file); os.IsNotExist(err) {
		util.ErrorPrinter(fmt.Errorf("store %s does not exist", name))
		return
	}

	util.ErrorPrinter(os.Remove(file))
}
