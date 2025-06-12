package configuration

import (
	"fmt"
	"io"
	"net/http"
	"os"

	"gopkg.in/yaml.v3"
)

// Tree node based file structure
type Directory struct {
	Name        string
	Description string
	Actions     []Action
	Subsections map[string]*Directory
	Parent      *Directory
}

type Action struct {
	Name        string
	Description string
	ScriptPath  string `yaml:"script_path"`
}

var Root Directory

// recursive function for setting parents (tree based data structure)
func setParentPointers(parent *Directory, subdirs map[string]*Directory) {
	for _, dir := range subdirs {
		dir.Parent = parent
		setParentPointers(dir, dir.Subsections)
	}
}

func LoadDirectories() {
	homeDir, err := os.UserHomeDir()
	if err != nil {
		fmt.Printf("%s\n", err)
	}

	data, err := os.ReadFile(homeDir + "/Documents/ssu/directories.yaml")
	if err != nil {
		fmt.Printf("%s\n", err)
	}

	//load yaml into root
	yamlErr := yaml.Unmarshal(data, &Root)
	if yamlErr != nil {
		fmt.Printf("%s\n", yamlErr)
	}

	setParentPointers(&Root, Root.Subsections)
}

func DownloadFile(url string, filepath string) error {
	//create the file
	out, err := os.Create(filepath)
	if err != nil {
		return err
	}
	defer out.Close()

	resp, err := http.Get(url)
	if err != nil {
		return err
	}
	//waits until the file is fully downloaded
	defer resp.Body.Close()

	//write the file
	_, err = io.Copy(out, resp.Body)
	if err != nil {
		return err
	}

	return nil
}
