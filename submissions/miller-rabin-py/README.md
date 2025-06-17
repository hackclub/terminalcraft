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
- pyinstaller (if you want to compile the program)

## Usage

Run the program using either:

```bash
python miller-rabin.py <mode> [options]
```
or:
```bash
py miller-rabin.py <mode> [options]
```
It is also possible to compile the program into executable file using pyinstaller:
```bash
pyinstaller miller-rabin.py
```
Or on Linux you can run the miller-rabin file located in executable folder (requires _internal folder in the same directory)
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
```
python miller-rabin.py 2 -f
what prime?: 99991

99991 is prime
```

Find 3 next primes after 69420:
```
python miller-rabin.py 4 -f
find next prime from: 69420
how many primes(1): 3


[69427, 69431, 69439]  are the next primes
```

Probabilistically test if 3141592653589793238462643383279502884197169 (which is 3 and 42 numbers of decimal expansion of pi) is prime with 8 tries:
```
python miller-rabin.py 1
how many times (its enough to test 1+prime//4 times): 8
what prime?: 31415926535897932384626433832795028841971693

........

31415926535897932384626433832795028841971693 is composite, divisors unknown;
   [1587088428223162779269218254204032911984758, 12700993974063310714093934152073824303341338, 20685932838058947786340928476433154132105303, 22375615338257956630441004902892471688213272, 22456507157576339597082781274285735147959232, 25879674012274480841901161150864945013050884, 27536274559240670603991979379942601800732147, 28735429035142801005187809323698018828715233] are the witnesses for the compositeness.
```

Find next prime number after 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139
```
python miller-rabin.py
find next prime from: 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139
how many primes(1):  


[1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006379]  are the next primes
```
(it took around 30 seconds)

Now check if it is prime with probabilistic test:
```
python miller-rabin.py
how many times (its enough to test 1+prime//4 times): 4
what prime?: 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006379

....

1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006379 is strong probable prime to bases: [186989568843949329913032870707725275641871823988620315347505381059937702582077847540168664022836954, 292404684612628197531052753924074823477781939960434642333975295165766042992106703358570422264812778, 530296371489712074259816043876596791271306905261660055906886698535154640539597818015200688035315045, 614837739069201934359411964041226864249013588376248343720041503561668565356330259015634895996862835]
    chances of it being composite are: 1/256
```
As we see there is 1/256 chance that this number is strong probable liar to those randomly chosen bases. (this test took less than a second)

The dots that showed up show progress (each dot is a base checked).
