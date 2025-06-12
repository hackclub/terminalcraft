# Usage

## Commands

- `request` — Make an HTTP request
- `save` — Save a request to a collection or as a global alias
- `send` — Send a saved request by alias (searches global aliases first, then collections)
- `collections` — List, view, or manage collections and items
- `globalaliases` — List all global aliases or show a specific alias (`-a myalias`)
- `vars` — View, remove, or clear variables
- `setvar` — Set a variable
- `history` — View or clear request history
- `replay` — Replay a request from history
- `chain` — Run a chain of requests from a file
- `diff` — Diff two responses (from history or files)
- `importcurl` — Import a cURL command as a saved request
- `exportcurl` — Export a saved request as a cURL command
- `removeglobal` — Remove a global alias
- `template` — Manage request templates (save, list, use, delete)
- `export` — Export data (collections, aliases, variables, templates, or all)
- `import` — Import data from a file
- `cat` — View the contents of a file
- `interactive` — Interactive request builder
- `clear` — Clear the screen
- `dt` — Toggle debug mode
- `reset` — Reset all data files
- `cause-error` — Trigger a test error (debug mode only)
- `exit` — Exit the program

Type `help` in the program for a summary of all commands.

---

### Making a Request

```sh
request -m GET -u https://jsonplaceholder.typicode.com/posts/1
```

**Options and Expected Output:**

- `-m, --method` (required) — HTTP method  
  *Example:* `-m POST`  
  *Expected output:* Sends a POST request.

- `-u, --url` (required) — Request URL (can be a file with URLs)  
  *Example:* `-u https://api.example.com/data`  
  *Expected output:* Sends request to the specified URL.

- `-hd, --headers` — Headers as JSON string or `@file.json`  
  *Example:* `-hd '{"Authorization": "Bearer token"}'`  
  *Expected output:* Adds headers to the request.

- `-d, --data` — Body as JSON string or `@file.json`  
  *Example:* `-d '{"key": "value"}'`  
  *Expected output:* Sends JSON body.

- `-o, --output` — Output response to file  
  *Example:* `-o output.txt`  
  *Expected output:* Writes the response to `output.txt`.

- `--only` — Output only `body`, `headers`, or `status`  
  *Example:* `--only body`  
  *Expected output:* Prints only the response body.

- `--auth` — Authentication helper: `"bearer TOKEN"` or `"basic USER:PASS"`  
  *Example:* `--auth "bearer mytoken"`  
  *Expected output:* Adds Authorization header.

- `--assert` — Assertion, e.g. `status=200` or `body_contains=foo`  
  *Example:* `--assert status=200`  
  *Expected output:* Prints assertion result after request.

- `-p, --preview` — Preview request before sending  
  *Example:* `-p`  
  *Expected output:* Shows request details and asks for confirmation.

- `-fv, --fillvars` — Fill placeholders in the request (prompt for variables)  
  *Example:* `-fv`  
  *Expected output:* Prompts for variable values used in the request.

**Examples:**
```sh
request -m POST -u https://api.example.com/data -hd '{"Authorization": "Bearer token"}' -d '{"key": "value"}'
request -m GET -u urls.txt
request -m GET -u https://api.example.com/data --auth "bearer mytoken"
request -m GET -u https://api.example.com/data --auth "basic user:pass"
request -m GET -u https://api.example.com/data --assert status=200
request -m GET -u https://api.example.com/data --only body
request -m GET -u https://api.example.com/data -p
request -m GET -u "https://api.example.com/{{endpoint}}" -fv
```

---

### Assertions and Script Runner

You can add assertions to requests to automatically check the response.  
**Supported assertions:**
- `status=CODE` — Check if the response status code matches.
- `body_contains=STRING` — Check if the response body contains a substring.

**You can also run a custom script if the assertion passes.**  
Scripts are located in the `scripts/` directory (e.g., `scripts/1.py` to `scripts/5.py`).  
You can edit these scripts to perform any custom action.

**Syntax:**
```sh
request -m GET -u https://api.example.com/data --assert status=200,1
```
- The number after the comma specifies which script to run (1-5).
- **Important:** There must be **no space** between the assertion condition and the comma/script number.  
  For example: `--assert status=200,1` is correct, but `--assert status=200, 1` will not work.

**Expected output:**
- If the assertion passes:  
  `Assertion passed: status=200`  
  Then, the specified script (e.g., `scripts/1.py`) will be executed.
- If the assertion fails:  
  `Assertion failed: status=404 (expected 200)`

**You can edit the scripts in the `scripts/` directory to customize what happens when an assertion passes.**

**Examples:**
```sh
request -m GET -u https://jsonplaceholder.typicode.com/posts/1 --assert status=200,1
request -m GET -u https://jsonplaceholder.typicode.com/posts/1 --assert body_contains=title,2
```

---

### Using Variables

Set a variable:
```sh
setvar base_url https://jsonplaceholder.typicode.com
```
*Expected output:*  
`Variable 'base_url' set.`

View variables:
```sh
vars
```
*Expected output:*  
A JSON object of all variables.

Use variables in requests:
```sh
request -m GET -u "{{base_url}}/posts/1"
```

Remove or clear variables:
```sh
vars -rm base_url
vars -cl
```
*Expected output:*  
Confirmation prompt and removal/clearing of variables.

---

### Collections and Global Aliases

Save a request to a collection:
```sh
save -c mycollection -a myalias -m GET -u https://api.example.com/data
```
*Expected output:*  
`Request saved as 'myalias' in collection 'mycollection'.`

Save as a global alias:
```sh
save -a myalias -m GET -u https://api.example.com/data
```
*Expected output:*  
`Request saved as global alias 'myalias'.`

List collections:
```sh
collections
```
*Expected output:*  
Lists all collections and their aliases.

View a collection:
```sh
collections -c mycollection
```
*Expected output:*  
Lists all requests in the specified collection.

View a specific request:
```sh
collections -c mycollection -a myalias
```
*Expected output:*  
Shows details for the specified alias.

Delete a collection or alias:
```sh
collections -del mycollection
collections -del mycollection:myalias
collections -rm mycollection:myalias
```
*Expected output:*  
Confirmation prompt and deletion.

Remove a global alias:
```sh
removeglobal myalias
```
*Expected output:*  
Confirmation prompt and removal.

Send a global alias:
```sh
send -a myalias
```
*Expected output:*  
Sends the saved request.

---

### Import/Export cURL

Import a cURL command:
```sh
importcurl "curl -X POST https://api.example.com/data -H 'Authorization: Bearer token' -d '{\"key\": \"value\"}'" -a myalias
importcurl "curl https://api.example.com/data" -a myalias -c mycollection
```
*Expected output:*  
Confirmation of import.

Export a saved request as cURL:
```sh
exportcurl -a myalias
exportcurl -a myalias -c mycollection
```
*Expected output:*  
A cURL command string.

---

### History

View history:
```sh
history
history -n 5
history -s posts
```
*Expected output:*  
List of recent requests.

Replay a request:
```sh
replay 0
```
*Expected output:*  
Re-sends the request at index 0 in history.

Clear history:
```sh
history -cl
```
*Expected output:*  
Confirmation prompt and clearing of history.

---

### Chaining Requests

Run a sequence of requests from a JSON file:

**chain.json**
```json
[
  {"method": "GET", "url": "https://jsonplaceholder.typicode.com/posts/1"},
  {"method": "GET", "url": "https://jsonplaceholder.typicode.com/posts/2"}
]
```

```sh
chain chain.json
```
*Expected output:*  
Runs each request in sequence.

---

### Diff Responses

Compare two responses from history or files:
```sh
diff 0 1
diff response1.txt response2.txt
```
*Expected output:*  
Colored diff output in the terminal.

---

### Authentication Helpers

Add authentication:
```sh
request -m GET -u https://api.example.com/data --auth "bearer mytoken"
request -m GET -u https://api.example.com/data --auth "basic user:pass"
```
*Expected output:*  
Adds the appropriate Authorization header.

---

### Output and Highlighting

- All JSON and HTML responses and headers are syntax highlighted.
- Output to file: Use `-o output.txt` to save the response.
- Use `--only` to print only the body, headers, or status.

---

### Templates

Templates let you save and reuse request blueprints with placeholders.

Save a template:
```sh
template save -n mytemplate -m POST -u "https://api.example.com/{{endpoint}}" -hd '{"Authorization":"Bearer {{token}}"}' -d '{"key":"{{value}}"}'
```
*Expected output:*  
`Template 'mytemplate' saved.`

List templates:
```sh
template list
```
*Expected output:*  
Lists all templates.

Use a template:
```sh
template use mytemplate
# You will be prompted for each placeholder value.
```
*Expected output:*  
Prompts for variable values and sends the request.

Delete a template:
```sh
template delete -n mytemplate
```
*Expected output:*  
Confirmation prompt and deletion.

---

### Import/Export Data

Export or import all data (collections, aliases, variables, templates):
```sh
export -t all -f backup.json
export -t collections -f collections.json
export -t aliases -f aliases.json
import -f backup.json
```
*Expected output:*  
Confirmation of export/import.

---

### Interactive Request Builder

Build and send a request interactively:
```sh
interactive
```
*Expected output:*  
Guided prompts for method, URL, headers, and body.

---

### View Global Aliases

```sh
globalaliases
```
*Expected output:*  
Lists all global aliases.

---

### Cat Files

View the contents of a file:
```sh
cat filename.txt
```
*Expected output:*  
Prints the file contents.
