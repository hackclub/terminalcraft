# CLI Steg

Image & Audio Steganography, in you command line

## Features

- Encode & Decode Messages
- Encrypt & Decrypt Messages with a password [IMG only]
- Cross-platform support

## Installation

You can download the pre-built binaries for your operating system from the [GitHub Releases](https://github.com/whirlxd/cli-steg/releases) page.

## Building from source -

**Clone the repository**
```bash
git clone https://github.com/whirlxd/cli-steg.git
cd cli-steg
```
**Install and Run**
```bash
pip install -r requirements.txt
python main.py
```


## How it works
> To be honest this working reminds me of the interstellar lol

We encode the message into binary and then encode it into the lsb of the images pixel values. 
We only alter it by ±1 though otherwise the changes to the color are noticeable.
For decoding the length is stored in the first 32 bits and its just simple decryption password based is a very simple xor encryption.

RGBA - Traditionally one might use RGB and encode values but it would cause changes to alpha channel which govern transparency and would be noticeable with backgroundless images so we use rgba instead.

Its quite similar for audio steganography but we encode the message into the frequency of the audio file. ( literally like interstellar )


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.