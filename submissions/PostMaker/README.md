# PostMaker

**PostMaker** is a terminal-based API client inspired by Postman, for developers who prefer the command line. It supports sending HTTP requests, managing collections, variables, history, assertions, chaining, diffing, templates, import/export, and more.

###### Project title credit (even though it's not that good): [MintyEcho](https://github.com/MintyEcho)

## Features

- Send HTTP requests (GET, POST, PUT, DELETE, etc.)
- Save requests to collections or as global aliases
- Send saved requests by alias (from collections or global aliases)
- Use variables in URLs, headers, and bodies
- View and replay request history
- Pretty-print and syntax highlight JSON and HTML responses and headers
- Assertions for status codes and response content, with optional script execution
- Chain requests from a file
- Diff responses from history or files
- Manage collections, global aliases, and variables (add, remove, clear)
- Import/export requests as cURL commands
- Authentication helpers (Bearer, Basic)
- Output responses to files (with auto-naming for batch requests)
- Templates: Save and reuse request templates with placeholders
- Import/export all data (collections, aliases, variables, templates)
- View and manage templates
- Interactive request builder
- View global aliases
- Cat files (view file contents in terminal)
- Script runner: Run custom Python scripts after assertions pass (edit scripts in `scripts/` directory)
- Toggle debug mode
- Reset all data files
- Trigger test errors (debug mode only)

#### ***NOTE: PLEASE use a Terminal/Terminal emulator that supports color, I put a lot of effort into making this look pretty***

## Getting started

Checkout the [installation](INSTALLATION.md) and [usage](USAGE.md) pages for instructions on how to get started.

---

## Example Workflow

```sh
setvar base_url https://jsonplaceholder.typicode.com
request -m GET -u "{{base_url}}/posts/1"
save -c demo -a getpost -m GET -u "{{base_url}}/posts/1"
send -a getpost -c demo
save -a globalget -m GET -u "{{base_url}}/posts/2"
send -a globalget
history
replay 0
diff 0 1
collections -c demo
collections -del demo:getpost
removeglobal globalget
vars -cl
importcurl "curl -X POST https://api.example.com/data -H 'Authorization: Bearer token' -d '{\"key\": \"value\"}'" -a myalias
exportcurl -a myalias
template save -n t1 -m GET -u "{{base_url}}/posts/{{id}}"
template use t1
export -t all -f backup.json
import -f backup.json
```

---

## Tips

- Use variables for anything that repeats (base URLs, tokens, IDs).
- Use collections and global aliases to organize and reuse requests.
- Use history and diff to debug and compare responses.
- Use assertions to automate API checks.
- Use output files to save responses for further analysis.
- Use `importcurl` and `exportcurl` to work with cURL commands.
- Use templates for requests with placeholders.
- Use the script runner for automation or advanced workflows.
- Use `interactive` for guided request building.
- **Edit scripts in the `scripts/` directory to customize what happens after assertions pass.**

---

**Enjoy using PostMaker!**
