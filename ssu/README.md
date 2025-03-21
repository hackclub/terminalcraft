# system security utility
Secure your system with some automated commands!
The Controls:
* Up Arrow: Select the item above
* Down Arrow: Select the item below
* Escape: Exit the program
* Enter: Select a file/executable

This tool only supports Linux. The code inside uses executes console commands for each executable item
## Installation
* Install `Go` on Linux: https://go.dev/doc/install

* Navigate to the correct directory: `cd cmd/ssu`

* Run the program: `go run main.go`

## Modules

### Firewall
* Configure UFW (uncomplicated firewall)
* Configure System CTL IPv4
### Remote Access Points
* Modify SSH Configuration
### Least Privilege
* Disable Root (sudo su)
* Disable Guest User & Greeter Remote Login
* System File Permissions
