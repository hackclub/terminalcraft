# Encrypx

Encrypx is a simple Python program to encrypt, decrypt, and brute force decrypt plain/cipher text. It currently supports the following ciphers:

* Caeser
* Railfence
* Vigenere.

## Features
* Encrypt and decrypt messages using classic ciphers.
* Brute-force decryption support for Caesar cipher
* Brute-force decryption support for Railfence based on the maximum number of keys due to the algorithm's reliance on the number of characters in the (plain/cipher)text.
* Brute-force decryption support for Vigenere using a corpus of common English words (unfortunately there isn't a better way as Vigenere is not limited by the number of letters in the alphabet like Caeser, or number of letters in the word like Railfence).

## Usage
To run Encrypx, run the following command (in the `src` folder):

```bash
python main.py
```

You'll be prompted to select a cipher and an action (encrypt, decrypt, or brute force). Then enter the text and the necessary key.

## Requirements
* Python 3.x.
* No external libraries required.
