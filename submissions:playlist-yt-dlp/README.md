# Playlist downloader for yt-dlp
Script to evade youtube rate limiting for yt-dlp

>Mac and Windows dependancies moreutils, python3, and python-pytube, python-pyperclip, YT-DLP
>Linux dependancies: same as Mac/Windows but also xclip
>>Does'nt work if the playlist tittle contains "/"

>How to use
>>Clone this repository with ''' git clone https://github.com/scarlimange/playlist-yt-dlp '''
>>Then cd into the new directory
>>Install python dependancies with ''' pip3 install -r requirements.txt '''
>>You can now run the script with ./playlist.sh, when prompted type/paste in the link to the playlist you want to download and select wether you want the videos or just audio

>>Thats it! youre done. Your playlist will now be in a folder with the same name within the script folder, or if you want it somewhere else just run the script from that location by calling its absolute path.