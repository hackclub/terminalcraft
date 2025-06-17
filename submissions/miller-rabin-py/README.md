# miller-rabin-py

This is a terminal based implementation of miller rabin primality test in python. It doesnt use any python libraries that need to be additionally installed.

## Features

- **Manual base selection** - you are able to manually select a base to check if a given number is strong pseudo-prime against it.
- **Probabilistic test** - you are able to test if given number is composite with randomly selected base, each test gives 3/4 probability of showing that number is composite (if it really is)
- **Deterministic test** - it is possible to deterministicly test primeness (up to 3317044064679887385961980) or any number if we assume that extended riemann hypothesis is true
- **Calculating pi(x) function** - you can count how many primes lie beetween two numbers
- **Finding next prime** - you are able to find next prime to a given integer

## Compatibility
| Operating System | Supported  | Notes               |
|------------------|------------|---------------------|
| Linux            | ✔️         | Fully supported , tested on Fedora 42|
|Windows 11        |✔️          |Works.|
| macOS            | ✔️         | It works on Linux so it is most probable that it will work on macOS|

## Requirements
- Python 3.x

## Usage

You can run the program with:
```bash
python miller-rabin.py
```
or:
```bash
py miller-rabin.py
```
