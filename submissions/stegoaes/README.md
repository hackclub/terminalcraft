# stegoAES

A command-line interface (CLI) tool for performing steganography operations, such as hiding and extracting AES encrypted messages within images.

## Features

- Hide encrypted messages within images
- Extract hidden messages from images
- Hide files inside images
- As of now, it only supports PNG file types

## Installation

To install the Steganography CLI tool, run this command:

```bash
npm i -g stegoaes
```

## Usage

### Hiding a Message

To hide a message within an image, use the following command:

```bash
stegoaes -s <your message> -p <optional password> <file> -o <optional output file>
```

Your secret will automatically be encrypted with AES256 if a password is provided

### Hiding a File

To hide a file within an image, use the following command:

```bash
stegoaes -f <file to hide> -p <optional password> <file>
```

The host file must be atleast 8 times bigger than the file you are going to hide

### Extracting a Message

To extract a hidden message from an image, use the following command:

```bash
stegoaes -p <optional password> <file>
```

If there's a file hidden inside, it will automatically extract

# Steganography
Original image:
### ![Example Image](orange-cat-looking-at-camera.png)
Image with a secret message:
### ![Secret message Image](stego.png)
