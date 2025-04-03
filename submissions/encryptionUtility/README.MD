# Terminal Encryption App

## Overview

The Terminal Encryption App is a command-line application that provides encryption, decryption, key generation, and hashing functionality. It supports both public-private key cryptography and symmetric key cryptography, as well as multiple hashing methods.

## Features

- **Encryption Methods:**
    - Public-private key (RSA 2048-bit with OAEP padding)
    - Symmetric key (AES-256-CBC)

- **Hashing Methods:**
    - SHA-256
    - SHA-512
    - MD5

- **Key Generation:**
    - RSA 2048-bit key pairs

- **File Operations:**
    - View and change working directory
    - Read from and write to files
    - Process both relative and absolute paths

## Dependencies

- OpenSSL library

## Compilation

To compile the application, use the following command for Linux:

```sh
gcc -o app *.c -g -lssl -lcrypto
```

For Windows, you may need to specify include and library paths (but I used MinGW for Windows cross-compilation):

```sh
gcc -o app *.c -g -I<openssl_include_path> -L<openssl_lib_path> -lssl -lcrypto
```
I didn't use this command, so I'm not sure if this will work

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
     - Default filenames: pubkey.pem and privkey.pem

4. **Hash**
     - Choose an input source (File or Text)
     - Choose an output destination (File or Text)
     - Choose a hash algorithm (SHA-256, SHA-512, or MD5)

5. **Info**
     - Display general information about the application
     - Access detailed info about cryptographic methods, key generation, and hashing

6. **Change Directory**
     - Change the current working directory for file operations

7. **Exit**
     - Exit the application

### Example Commands

#### Encrypt a File

```sh
./TerminalApp
# Select "Encrypt"
# Select "Public-private key"
# Select "From file"
# Enter the input file path
# Select output destination
# Choose key source and provide key
```

#### Decrypt a File

```sh
./TerminalApp
# Select "Decrypt"
# Select decryption method
# Select "From file"
# Enter the encrypted file path
# Select output destination
# Choose key source and provide key
# Select whether input is Base64 or Binary
```

#### Generate RSA Key Pair

```sh
./TerminalApp
# Select "Generate key"
# Enter filenames for public and private keys (or use defaults)
```

#### Hash a File

```sh
./TerminalApp
# Select "Hash"
# Select "From file"
# Enter the file path
# Select output destination
# Choose hash algorithm (SHA-256, SHA-512, or MD5)
```

### Encryption Details

#### Public-Private Key (RSA)
- Uses RSA 2048-bit with OAEP padding for security
- Encrypt with public key, decrypt with private key
- Suitable for small data and key exchange
- Implementation uses OpenSSL's EVP_PKEY interface

#### Symmetric Key (AES)
- Uses AES-256-CBC with a derived key and initialization vector (IV)
- Same key used for both encryption and decryption
- Key is derived from your passphrase using SHA-256
- IV is randomly generated and stored with encrypted data
- Efficient for encrypting larger amounts of data

### Hashing Details

- **SHA-256**: Produces a 256-bit (32-byte) hash value
- **SHA-512**: Produces a 512-bit (64-byte) hash value
- **MD5**: Produces a 128-bit (16-byte) hash value (Note: not recommended for security purposes)

## System Information

- **Platform:** Windows or Unix/Linux
- **Version:** 1.0
- **Author:** Moriaan Michiels

## License

This project is licensed under the MIT License.
