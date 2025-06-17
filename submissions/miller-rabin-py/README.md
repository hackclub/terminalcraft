# miller-rabin-py

A terminal-based implementation of the Miller-Rabin primality test in Python. This tool allows you to determine whether a given number is prime, calculate value of pi(x) function, and find next prime to a natural number, without requiring any additional Python packages.

## What is Miller-Rabin Primality Test?

The Miller-Rabin primality test is a probabilistic algorithm used to determine if a number is prime. It's much faster than trial division methods, especially for large numbers. This program also uses Miller test, which is a deterministic version of Miller-Rabin test.

## Features

- **Manual Base Testing** - Test if a number is a strong pseudo-prime against a specific base of your choice.

- **Probabilistic Testing** - Test primality with randomly selected bases. Each test gives a 3/4 probability of detecting a composite number, with the probability of error decreasing exponentially with multiple tests.

- **Deterministic Testing \- Miller test** - Get absolute certainty about primality for numbers up to 3,317,044,064,679,887,385,961,980. For larger numbers, the test is deterministic if the Extended Riemann Hypothesis is true.

- **Prime Counting Function (π(x))** - Calculate how many prime numbers exist between any two values. This implements the famous mathematical function π(x) which counts primes up to x.

- **Prime Number Generation** - Find the next prime number(s) following any given integer. Perfect for generating prime numbers for cryptographic applications.

## Compatibility

| Operating System | Supported  | Notes                                          |
|------------------|------------|------------------------------------------------|
| Linux            | ✓         | Fully supported, tested on Fedora 42           |
| Windows 11       | ✓         | It works                              |
| macOS            | ✓         | Expected to work properly (Unix-compatible), but i dont own a macOS machine to test this     |

## Requirements

- Python 3.x (no additional libraries needed)

## Usage

Run the program using either:

```bash
python miller-rabin.py <mode> [options]
```
or:
```bash
py miller-rabin.py <mode> [options]
```

### Available Modes:

- `0`: Manual base testing - Test a specific number with a manually chosen base
- `1`: Probabilistic testing - Test primality with multiple random bases
- `2`: Deterministic testing - Get a definitive primality test
- `3`: Prime counting - Count primes between two values
- `4`: Next prime finder - Find the next prime(s) after a given number

### Options:

- `-f, --fast`: Use fast mode to skip intermediate results and terminate early when possible

### Examples:

Test if 997 is a prime using deterministic testing:
```bash
python miller-rabin.py 2 -f
what prime?: 99991

99991 is prime
```


