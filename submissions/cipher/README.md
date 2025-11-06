# cipher
A small, customizable CLI app that algorithmically ciphers and deciphers text based on user input.


I have the problem that I want to have coded messages to send to people,
but each message has to go through a ton of steps to manually encode.
Yes, other tools already exist that let me use virtually any encryption
system, but none of them really work all at once, and they're pretty
inconvenient for me to use. My intention for this program is that it should
be a lightweight but powerful tool that's completely customizable to the
end user's needs. It's not meant to be an uncrackable system, a message 
encrypted by Cipher will be eventually decoded by someone trying hard
enough. But, I'm hoping that the ability to layer ciphers on top of one
another will make it much harder for someone trying to read your messages.

Side note, I don't have much experience with cryptography at all; this is
mostly just a fun little side project to distract me from my burnout and
also to learn how to use RegEx because I hate RegEx and I believe that
no end user should need to know how to use it to encrypt things.

**Update 13 March 2025: I did not end up having to use RegEx at all. Maybe in a future release.**

## Build Instructions
#### Prerequisites
- Node.js v23.9.0
- npm

### Linux
1. Run the provided `./build` in your terminal.
2. Run `./cipher` and you should be good to go.

### Windows
1. Run `.\cipher.bat` and ignore any Windows Defender prompts saying that it's malware. Why would this be malware? You can literally look through the source code to confirm that it isn't. 