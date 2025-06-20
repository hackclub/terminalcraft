/*
Copyright © 2025 Krish Gupta <m.krishggupta@icloud.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
*/
package cmd

import (
	"fmt"
	"os"
	"path"
	"strings"

	"github.com/kkrishguptaa/mnemo/util"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

// rootCmd represents the base command when called without any subcommands

var rootCmd = &cobra.Command{
	Use:   "mnemo",
	Short: "Think snippets, think mnemo",
	Long:  `mnemo lets you store and manage snippets of code, text, and other information in a structured way. You can create, edit, and delete snippets, organize them into categories, and search for them easily. It is designed to help you remember and retrieve important information quickly. It also has support for encryption, allowing you to securely store sensitive information.`,
	RunE: func(cmd *cobra.Command, args []string) error {
		return cmd.Help()
	},
}

func Execute() {
	err := rootCmd.Execute()
	if err != nil {
		os.Exit(1)
	}
}

func init() {
	rootCmd.AddGroup(&cobra.Group{
		ID:    "mnemo",
		Title: "Mnemo Commands",
	})

	home := util.ErrorHandler(os.UserHomeDir())
	defaultDirectory := home + "/.mnemo"

	viper.SetConfigName("mnemo")
	viper.AddConfigPath(home) // Use the home directory for the config file
	viper.SetConfigType("yml")
	if err := viper.ReadInConfig(); err != nil {
		if _, ok := err.(viper.ConfigFileNotFoundError); ok {
			var defaultConfig = []byte(fmt.Sprintf(`
# Mnemo Configuration File
# This file is used to configure Mnemo settings.
# Default store name
default_store: default
# Path to the stores directory
path: %s
`, defaultDirectory))
			if err := os.MkdirAll(defaultDirectory, 0755); err != nil {
				panic(err) // Handle error if directory creation fails
			}
			if err := os.WriteFile(path.Join(home, "mnemo.yml"), defaultConfig, 0644); err != nil {
				panic(err) // Handle error if file creation fails
			}
		} else {
			// Config file was found but another error was produced
			panic(err)
		}
	}
	viper.AutomaticEnv()                                   // read in environment variables that match
	viper.SetEnvPrefix("MNEMO")                            // will be uppercased automatically
	viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_")) // replace dots with underscores in env vars
	viper.SetDefault("default_store", "default")           // Set a default store name
	viper.SetDefault("path", defaultDirectory)             // Set a default path for the stores
	if err := os.MkdirAll(viper.GetString("path"), 0755); err != nil {
		panic(err) // Handle error if directory creation fails
	}

	viper.BindPFlag("default_store", rootCmd.PersistentFlags().Lookup("store"))
	viper.BindPFlag("path", rootCmd.PersistentFlags().Lookup("path"))
	rootCmd.PersistentFlags().StringP("store", "s", viper.GetString("default_store"), "Specify the store to use (default is 'default')")
	rootCmd.PersistentFlags().StringP("path", "P", viper.GetString("path"), "Specify the path to the stores directory")
}
