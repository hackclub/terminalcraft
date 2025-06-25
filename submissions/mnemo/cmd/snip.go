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
	"path"
	"strings"

	"github.com/charmbracelet/lipgloss"
	"github.com/kkrishguptaa/mnemo/lib"
	"github.com/kkrishguptaa/mnemo/util"
	"github.com/spf13/cobra"
	"github.com/spf13/viper"
)

// snipCmd represents the snip command
var snipCmd = &cobra.Command{
	Use:     "snip",
	Short:   "Manage your snippets",
	Run:     listSnippets,
	Args:    cobra.NoArgs,
	GroupID: "mnemo",
}

func listSnippets(cmd *cobra.Command, args []string) {
	// This function will list all snippets in the specified store.
	store, _ := cmd.Flags().GetString("store")

	if store == "" {
		store = viper.GetString("default_store")
	}

	Store := lib.FetchStore(path.Join(util.ErrorHandler(cmd.Flags().GetString("path")), "stores"), store, viper.GetString("default_store"))

	for _, snippet := range Store.Data {
		if snippet.Encrypted {
			println(
				lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("205")).Render(snippet.Id),
				":",
				lipgloss.NewStyle().Foreground(lipgloss.Color("8")).
					Render("encrypted, use 'mnemo snip read "+snippet.Id+"' to view the value"))
			continue
		}

		println(lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("205")).Render(snippet.Id), ":", snippet.Value)
	}
}

func CreateSnip(cmd *cobra.Command, args []string) {
	store, _ := cmd.Flags().GetString("store")
	if store == "" {
		store = viper.GetString("default_store")
	}

	encrypted := false

	password, _ := cmd.Flags().GetString("password")

	if password != "" {
		encrypted = true
	}

	key := args[0]
	value := strings.Join(args[1:], " ")

	if key == "" || value == "" {
		cmd.Help()
		return
	}

	Store := lib.FetchStore(path.Join(util.ErrorHandler(cmd.Flags().GetString("path")), "stores"), store, viper.GetString("default_store"))

	if encrypted {
		value = lib.Encrypt(value, password)
	}

	snippet := lib.Snippet{
		Id:        key,
		Value:     value,
		Encrypted: encrypted,
	}

	Store.Data = append(Store.Data, snippet)

	lib.WriteStore(path.Join(util.ErrorHandler(cmd.Flags().GetString("path")), "stores"), store, Store.Data)

	util.SuccessPrinter("Snippet created successfully in store: " + store)
}

func ReadSnip(cmd *cobra.Command, args []string) {
	store, _ := cmd.Flags().GetString("store")
	if store == "" {
		store = viper.GetString("default_store")
	}

	if len(args) != 1 {
		cmd.Help()
		return
	}

	key := args[0]

	Store := lib.FetchStore(path.Join(util.ErrorHandler(cmd.Flags().GetString("path")), "stores"), store, viper.GetString("default_store"))

	for _, snippet := range Store.Data {
		if snippet.Id == key {
			if snippet.Encrypted {
				password, _ := cmd.Flags().GetString("password")
				if password == "" {
					util.ErrorPrinter(fmt.Errorf("snippet with key '%s' is encrypted, please provide a password using the '-p' flag", key))
					return
				}

				value := lib.Decrypt(snippet.Value, password)

				println(value)
			} else {
				println(snippet.Value)
			}
			return
		}
	}

	util.ErrorPrinter(fmt.Errorf("snippet with key '%s' not found in store '%s'", key, store))
}

func DeleteSnip(cmd *cobra.Command, args []string) {
	store, _ := cmd.Flags().GetString("store")
	if store == "" {
		store = viper.GetString("default_store")
	}

	if len(args) != 1 {
		cmd.Help()
		return
	}

	key := args[0]

	Store := lib.FetchStore(path.Join(util.ErrorHandler(cmd.Flags().GetString("path")), "stores"), store, viper.GetString("default_store"))

	snips := []lib.Snippet{}

	for _, snippet := range Store.Data {
		if snippet.Id != key {
			snips = append(snips, snippet)
		}
	}

	if len(snips) == len(Store.Data) {
		util.ErrorPrinter(fmt.Errorf("snippet with key '%s' not found in store '%s'", key, store))
		return
	}

	lib.WriteStore(path.Join(util.ErrorHandler(cmd.Flags().GetString("path")), "stores"), store, snips)

	util.SuccessPrinter(fmt.Sprintf("Snippet with key '%s' deleted successfully from store '%s'", key, store))
}

func init() {
	var listSnipsCmd = &cobra.Command{
		Use:     "list",
		Short:   "List all snippets in the specified store",
		Aliases: []string{"ls"},
		Run:     listSnippets,
	}
	snipCmd.AddCommand(listSnipsCmd)

	var createSnipCmd = &cobra.Command{
		Use:   "create [key] [value]",
		Short: "Create a new snippet in the specified store",
		Long:  `Create a new snippet with the specified key and value in the specified store. If the store does not exist, it will be created.`,
		Args:  cobra.ExactArgs(2),
		Run:   CreateSnip,
	}
	ApplySnipPasswordFlag(createSnipCmd)
	snipCmd.AddCommand(createSnipCmd)

	var readSnipCmd = &cobra.Command{
		Use:   "read [key]",
		Short: "Read a snippet from the specified store",
		Long:  `Read a snippet with the specified key from the specified store. If the snippet is encrypted, you will need to provide the password using the '-p' flag.`,
		Args:  cobra.ExactArgs(1),
		Run:   ReadSnip,
	}
	ApplySnipPasswordFlag(readSnipCmd)
	snipCmd.AddCommand(readSnipCmd)

	var deleteSnipCmd = &cobra.Command{
		Use:   "delete [key]",
		Short: "Delete a snippet from the specified store",
		Long:  `Delete a snippet with the specified key from the specified store.`,
		Args:  cobra.ExactArgs(1),
		Run:   DeleteSnip,
	}
	snipCmd.AddCommand(deleteSnipCmd)

	rootCmd.AddCommand(snipCmd)

}

func ApplySnipPasswordFlag(cmd *cobra.Command) {
	cmd.Flags().StringP("password", "p", "", "Password for the snippet (if it is encrypted)")
}
