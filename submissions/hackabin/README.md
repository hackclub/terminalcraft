# hackabin  
a simple CLI app that lets you save code snippets for you to copy and paste wherever needed.

## commands  
- `hackabin add [title:string] [code:string|file]` - add a snippet  
- `hackabin remove [id]` - remove a snippet  
- `hackabin list` - view all snippets  
- `hackabin view [id]` - view and copy snippet to clipboard  
- `hackabin help` - [stop it get some help](https://imgur.com/gallery/stop-get-some-help-DJIkoRf)

## running  
1. download the binary for your OS from the [`build/`](https://github.com/ronykax/hackabin/tree/master/build) folder  
2. open a terminal in the same directory as the binary file  
3. run `hackabin` and you should see the help command!  
4. if you want to make the command accessible globally, refer to [building](https://github.com/ronykax/hackabin?tab=readme-ov-file#building)

## building  
follow the steps below if you prefer building the binary for your OS yourself:  
1. download and install a non-ancient version of [golang](https://go.dev/doc/install) on your computer  
2. clone this repo and go into the directory  
3. run `go build -o hackabin` and you will see a `hackabin` or `hackabin.exe` file appear in that directory!  
4. run `go install` to make `hackabin` accessible globally :)  

## project details
1. **What is the name of your project?**
_hackabin_

2. **How many hours did you spend developing this?**
_9_

3. **Briefly describe what your project is. What makes it unique?**
_hackabin lets you save code snippets directly from your terminal to view and use wherever needed. it's unique because it hasn't been done before and it also has hackclub's unique charm to it. you will see orpheus here and there! ;)_

4. **How many people have tested your extension?**
_two. my dad and best friend_

5. **On What operating systems have you tested this project?**
_linux and windows_

6. **Does your project include a Readme file with instructions on how to use it?**
_yes!_