# snip-run

**snip-run** is a way to neatly organize your small programs and random code snippets
the dir structure nudges you to tidy all the related files up, rather than letting them plague your ~

## features

* pretty, self-explained interface (thanks to `prompt_toolkit`)
* quickly add common "modifiers" like a file for stderr or timing the snippet
* automatically select a file for things like logs

## diary.py

* appends an entry to a text file
* basically a test snippet to show that snip-run works
* features over `>>`:
* uses snip-run file structure (`--name` option to change the txt file used)
* `--editor` option for writing longer entries
* automatically separate entries by day
* mark entries with time
* `--feel` option to mark entries with a simple HWF-like mood
