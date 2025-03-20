# DriveExplorer

My first CLI I made using the Google Drive API and Python! Allows you to make a folder and push stuff inside it to your drive straight from the command line!

### Usage

Overall, the usage is super simple with only 2 commands:

- ```dexp setup <directory>```: Log in with google and set up a folder which will be pushed to Drive  
- ```dexp save```: Saves the folder set up with dexp setup and pushes all its contents to Google Drive

(Recommended to not set up many times or at least delete old folders to make it less messy)


### Installation (Windows & Linux)

1. Clone the repo:
```
git clone https://github.com/yourusername/driveExplorer.git
cd driveExplorer
```

2. Install the package:
```
pip install -e .
```

3. Use the app!
```
dexp setup <dir>
```

NOTE: On linux systems, the package might be installed into a folder which is not in the PATH variable, in which case you should add it with ```export PATH="<your path>:$PATH"```


If you want you can also use the files from ./dist to install !