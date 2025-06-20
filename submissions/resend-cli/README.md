# resend-cli
Simple, pretty command-line based tool for sending emails, managing audiences, etc via [Resend](https://resend.com).

## install
Install resend-cli by running `npm i -g resend-cli`.  
Do not install resend-cli locally, without the `-g` flag, since it does not make sense for it to be a project dependency.

## usage
resend-cli does not require any arguments. If you are running resend-cli for the first time, the command-line will prompt you for an API key.
API keys must have full access for all features of the CLI to work properly. You may create an API key from the [dashboard](https://resend.com/api-keys).

After this, the API key will be saved in plain text (!) at ~/.resend_config.json. For this reason, avoid installing resend-cli on public or shared computers.  

To exit resend-cli, use the Ctrl+C keyboard shortcut.

## misc
visit the [project page](https://pablogracia.net/projects/resend-cli) to learn more about this project.  

Contributions welcome. Stars encouraged.