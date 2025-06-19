# snip-run

**snip-run** is a way to neatly organize your small programs and random code snippets
the dir structure nudges you to tidy all the related files up, rather than letting them plague your ~

## features

* pretty, self-explained interface (thanks to `prompt_toolkit`)
* quickly add common "modifiers" like a file for stderr or timing the snippet
* automatically select a file for things like logs

## setup
* if not already installed, run `pip install prompt_toolkit`
* //linux users: make sure `python` runs python3 (or python2), using aliases or the `python-is-python3` package
* download `snip-run.py` to a directory of your choice
* create a `snip-files` dir in the same directory
* optionally, create `snip-files/_data` and `snip-files/_output` dirs
* add python snippets to the snip-files dir or a subdir
* optionally, download `diary.py` or `input.py` to snip-files for testing
* run `python snip-run.py` and use the TUI to select snippet to run and additional modifiers

## diary.py

* appends an entry to a text file
* basically a test snippet to show that snip-run works
* features over `>>`:
* uses snip-run file structure (`--name` option to change the txt file used)
* `--editor` option for writing longer entries
* automatically separate entries by day
* mark entries with time
* `--feel` option to mark entries with a simple HWF-like mood
