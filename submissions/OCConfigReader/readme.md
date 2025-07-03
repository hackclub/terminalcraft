# OCConfigReader
Reads a config.plist, and provides some quick diagnostic info. It also detects potentionally problematic stuff.

## How to run
This project depends on floxlist(I made it, it's not a 3rd-party library) and xmlParser(license and source is attached) (included on the repo)
Then, you can run `lua main.lua path/to/config.plist`

## About other two attached files
normal.plist is my main config.plist(with no issues), while preb-ocat.plist is heavily modified prebuilt/premade one(Credit is attached) made to trigger more issues.