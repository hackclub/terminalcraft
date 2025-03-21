package configuration

import (
	"fmt"
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
	data, err := os.ReadFile("../../directories.yaml")
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
