# mnemo

Mnemo (pronounced Nemo) is a CLI application built to remember snips of information under various categories and even encrypt them sometimes.

Think of it as notes but in your terminal. You can store commands, keys, random pieces of frequently used text, etc in your `mnemo`.

## 📦 Installation

### With Golang

```sh
go install github.com/kkrishguptaa/mnemo
```

### Without Golang

1. Download the release file from the [latest release](https://github.com/kkrishguptaa/mnemo/releases/latest)
  ![kkrishguptaa/mnemo's github releases](https://github.com/user-attachments/assets/72c56637-bef7-48ee-80d4-902bd828c55f)
1. Place it in any folder under `$PATH`

## ✌️ Usage

### Snips

```sh
# To create a snip
mnemo snip create key "value"

# To encrypt the snip
mnemo snip create key "value" -p "password-for-encryption"

# To list all available snips
mnemo snip # or mnemo snip list
# If you have a lot of snips, you can pipe the output to less or more
mnemo snip | less

# To read an encrypted snip
mnemo snip read key -p "password-for-decryption"
```

### Stores

```sh
# Stores are collections/categories of snips. Say you want to hold all your docker quick-bits together in one collection of snips rather than have them jumbled up together
# By default all snips are stored in a store called "default".

# To list all your stores you can type
mnemo store list # or mnemo ls

# To create a snip store
mnemo store create "storeName"

# To clear (remove all snips) from a store
mnemo store clear "storeName"

# NOTE: clear does not delete the store, it just removes all the snips, you can use mnemo store delete to delete it
mnemo store delete "storeName"

# To list snips for a particular store, you use a flag.
mnemo snip -s docker

# You can run all mnemo snip functions with the -s flag to have them work with your store.
```

### Configuration

Mnemo reads a configuration file named `$HOME/.mnemo.yml`. It has 2 keys both are prepopulated.

```yml
# The name of the default store with snips without stores.
default_store: default
# Path of mnemo's working directory (it stores all data here)
path: /home/username/.mnemo
```

NOTE: You cannot override the `default_store` using a flag, however you can use `-s` to change the working store always.

You can override the `path` using the flag `-P`, `-p` is reserved for password, please keep in mind.
