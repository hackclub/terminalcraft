# Terminal Encryption App

## Overview

The Terminal Encryption App is a command-line application that provides encryption, decryption, key generation, and hashing functionality. It supports both public-private key cryptography and symmetric key cryptography, as well as hashing methods like SHA-256 and MD5.

## Features

- **Encryption Methods:**
    - Public-private key (RSA)
    - Symmetric key (AES)

- **Hashing Methods:**
    - SHA-256
    - MD5

- **Key Generation:**
    - RSA 2048-bit key pairs

## Dependencies

- OpenSSL library

## Compilation

To compile the application, use the following command:

```sh
gcc -o app (ls *.c) -g -lssl -lcrypto
```
Make sure to have the OpenSSL library installed on your system, you're in the correct directory, and the `*.c` and `*.h` files are present.

## Usage

### Menu Options

1. **Encrypt**
     - Choose an encryption method (Public-private key or Symmetric key)
     - Choose an input source (File or Text)
     - Choose an output destination (File or Text)
     - Choose a key source (File or Text)

2. **Decrypt**
     - Choose a decryption method (Public-private key or Symmetric key)
     - Choose an input source (File or Text)
     - Choose an output destination (File or Text)
     - Choose a key source (File or Text)
     - Select input format (Base64 or Binary)

3. **Generate Key**
     - Generate RSA 2048-bit key pairs and save them to files

4. **Hash**
     - Choose an input source (File or Text)
     - Choose an output destination (File or Text)
     - Choose a hash algorithm (SHA-256, SHA-512, or MD5)

5. **Info**
     - Display information about the application, including version and author

6. **Exit**
     - Exit the application

### Example Commands

#### Encrypt a File

```sh
./TerminalApp
# Follow the prompts to select encryption method, input source, output destination, and key source
```

#### Decrypt a File

```sh
./TerminalApp
# Follow the prompts to select decryption method, input source, output destination, key source, and input format
```

#### Generate RSA Key Pair

```sh
./TerminalApp
# Follow the prompts to generate and save RSA key pairs
```

#### Hash a File

```sh
./TerminalApp
# Follow the prompts to select input source, output destination, and hash algorithm
```

## System Information

- **Platform:** Windows or Unix/Linux
- **Version:** 1.0
- **Author:** Moriaan Michiels

## License

This project is licensed under the MIT License.
