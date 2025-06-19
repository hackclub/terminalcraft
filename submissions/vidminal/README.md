# 📺 Vidminal: 'Cause Who Needs Graphics Anyway? 🤷‍♀️
Ever wanted to watch videos but, like, without all those fancy pixels? Just good ol' text? And maybe with sound too? No? Well, too bad, 'cause this thing does it! 🙄

It's a super "optimized" tool that turns any video into a glorious, eye-straining ASCII art experience right in your terminal. Plus, it plays the audio. Because even a lazy developer knows you can't just have silent movies. 😴


### A little sneek peek:
https://github.com/user-attachments/assets/2813c448-8570-4419-b27a-13f7eec639c3



## 🚀 How to Get This Masterpiece Running

### From Binaries
Just download the right executable for your OS from the [Releases](https://github.com/sajagin/vidminal/releases) page. No Python or dependencies needed. Run it and follow the prompts. All required files (including BadApple.mp4 and ffmpeg) are bundled.

### From Python Script

- Prerequisites (Stuff You Probably Already Have, Hopefully)
- **Python**: 'Cause that's what this is written in. Duh.
- **Pillow**: For image magic. `pip install Pillow`
- **moviepy**: For video wrangling. `pip install moviepy`
- **pygame**: For sound. `pip install pygame`

### No FFmpeg Setup!
You don't need to install ffmpeg yourself . This repo ships with a compressed `ffmpeg_bin.7z` containing all the ffmpeg binaries for Windows, Mac, and Linux (even ARM stuff). The script will extract and use the right one for your system, automatically. So, yeah, just run it.

## 🍿 Usage: "Watch" a Video
Just run it. The script will ask you for everything (video file, width, fps, temp folder) like a lazy wizard. ✨
```bash
python vidminal.py
```
Or, if you downloaded a binary, just run it:
```bash
./vidminal-windows.exe  # or vidminal-linux, vidminal-macos
```
Just follow the prompts. Or just hit Enter for the defaults. That's it.

### Options (If You're Feeling Fancy)
You don't need to remember any command-line arguments. The script will ask you for:
- Video file (default: BadApple.mp4)
- Temp folder (default: temp)
- Width (default: 80)
- FPS (default: 24)

Just press Enter to accept the defaults, or type your own values. Easy.

### ⚠️ Known Issues / "Features"
- Terminal Size Matters: If your terminal is too small, things will look like a jumbled mess. Make it big! Or don't, I'm not your boss.
- Performance: It's Python. It's ASCII. It might stutter. Don't come crying to me.
- Temporary Files: It creates a bunch of image files and an audio file. It doesn't clean them up automatically. Why? **Because I'm lazy. Delete them yourself!** 🔥🗑️
- ffmpeg will be extracted to the script's root folder if not already there. If you delete it, it'll just get extracted again. Magic.
- **Full video path is required (No relative path)**

## Contributing (LOL)
Sure, if you really wanna make this "better," feel free. But honestly, it works, right? So why bother? Issues and pull requests are technically welcome, I guess. 🙄

# License
This project is probably under some open-source license. Just assume you can do whatever with it, but don't blame me if it breaks your computer. Or your eyes. 😜

#### PS: It's fun sometimes written a README from hand without any tool. 😆
#### added `BadApple.mp4` in repo for testing. It's literally the best thing after "Hello World".
