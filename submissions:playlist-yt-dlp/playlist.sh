#call python script to enumerate playlist url's and create a new folder named after the playlist tittle

python -c "from pytube import Playlist
import pyperclip
import os

URL_PLAYLIST = input('Enter the URL to download: ')

# make new directory with playlist title
playlist = Playlist(URL_PLAYLIST)
title = playlist.title
os.mkdir(title)

# Retrieve URLs of videos from playlist
print('Number Of Videos In playlist: %s' % len(playlist.video_urls))

urls = []
for url in playlist:
	urls.append(url)

#copies urls to clipboard
pyperclip.copy(urls)"


#detect which os is running
device="$(uname -s)"
case "${unameOut}" in
	Linux*)     device=Linux;;
	Darwin*)    device=Mac;;
	CYGWIN*)    device=Cygwin;;
esac
echo ${device}

#if statement to determin which commands to run
if [ $device == Darwin ]
then
	#sets variable equal to the name of the new folder
	parth="$(ls -tU | head -1)"
	
	#uses built in paste command and some delimiters to sanitize the output of the python and put it into a file
	pbpaste | tail -n 1 | tr -d "][''," | tr ' ' '\n' | sponge playlist.txt
	
	#for loop to evaluate each individual video in the playlist and downlooad them as mp4 files
	for url in $( cat playlist.txt)
	do
		yt-dlp --format "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]" -P "$parth" $url
	done
	rm playlist.txt
	echo "$parth"
	read -p "Convert to mp3?" -n 1 -r
	if [[ $REPLY =~ ^[Yy]$ ]]
	then
		echo
		for ln in "$parth"/*
		do ffmpeg -i "$ln" -vn -ab 192k -acodec libmp3lame -ac 2 "$parth"/"$ln".mp3
		done
	fi
	read -p "Remove mp4's?" -n 1 -r
	if [[ $REPLY =~ ^[Yy]$ ]]
	then
		echo
		rm -v *.mp4
	fi
		
elif [ $device == Linux ]
then
	#same as mac
	parth="$(\ls -1dt ./*/ | head -n 1)"
	xclip -out -selection clipboard | tail -n 1 | tr -d "][''," | tr ' ' '\n' | sponge playlist.txt
	for url in $( cat playlist.txt)
	do
		yt-dlp --format "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]" -P "$parth" $url
	done
	read -p "Convert to mp3?" -n 1 -r
	if [[ $REPLY =~ ^[Yy]$ ]]
	then
		echo
		for ln in "$parth"/*
		converttomp3.sh "$ln"
		done
	fi
	read -p "Remove mp4's?" -n 1 -r
	if [[ $REPLY =~ ^[Yy]$ ]]
	then
		echo
		rm -v *.mp4
	fi
elif [ $device == Cygwin ]
then

	parth="$(\ls -1dt ./*/ | head -n 1)"
	pclip | tail -n 1 | tr -d "][''," | tr ' ' '\n' | sponge playlist.txt
	read -p "Convert to mp3?" -n 1 -r
	if [[ $REPLY =~ ^[Yy]$ ]]
	then
		for url in $( cat playlist.txt)
		do
			yt-dlp -x --audio-format mp3 -P "$parth" $url
		done
	else 
	for url in $( cat playlist.txt)
		do
			yt-dlp --format "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]" -P "$parth" $url
		done
	fi
fi
#thanks for using :D
