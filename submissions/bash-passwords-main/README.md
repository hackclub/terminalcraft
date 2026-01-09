# bash-passwords
A password manager of sorts in a bash shell

## Use
To use this download the `passwords.sh` file then you can run it with `./passwords.sh` if you are in the same directery as the file.

There are 4 commands:

* `list`
* `generate`
* `get`
* `add`

### `list`
This will list every username and password you have.

### `generate`

This takes one aguments which is the length (number) that the password should be. For exampel this will generate a password with a length of 10.
```bash
./passwords.sh generate 10
```

### `get`

This will return one username/password combo. The second agument is the search term for the username. This command uses `grep` to search

### `add`

This adds a password to the file. It takes 2 aguments, the username and password. For example if I had a hackclub login:

```bash
./passwords.sh add hackclub somePassword123
```
