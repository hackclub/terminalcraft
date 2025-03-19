# Scientific Calculator in Rust

A command-line scientific calculator implemented in Rust, capable of evaluating mathematical expressions with basic arithmetic, trigonometric functions, and user-defined constants. It uses Reverse Polish Notation (RPN) for efficient expression parsing and evaluation.

## Features

- **Basic Arithmetic**: Supports `+`, `-`, `*`, `/`, and `^` (exponentiation).
- **Trigonometric Functions**: `sin`, `cos`, `tg` (tangent), `ctg` (cotangent) with degree inputs.
- **Constants**: Define and reuse constants (e.g., `export pi = 3.14159`).
- **REPL Interface**: Interactive Read-Eval-Print-Loop for quick calculations.
- **Error Handling**: Detects mismatched parentheses and invalid syntax.
- **Command history**: Use arrows to navigate to previous lines

## Installation

1. Ensure [Rust and Cargo](https://www.rust-lang.org/tools/install) are installed.
2. Clone the repository:
   ```bash
   git clone https://github.com/mzums/calculator
   cd calculator
   ```
3. Run the project:
   ```bash
   cargo run
   ```

## Usage

### Interactive Mode
Start the program, and enter expressions directly:
```
> 3 + 5 * 2
Result = 13
> sin(30)
Result = 0.5
> 2^3 + 4
Result = 12
```

### Define Constants
Use `export NAME = EXPRESSION` to define constants:
```
> export pi = 3.14159
Variable: pi, Value: 3.14159
> 2 * pi
Result = 6.28318
```

### Supported Operations
- **Arithmetic**: `3 + 4 * (2 - 5)`
- **Exponents**: `2^3^2` (evaluated as 2^(3^2) = 512)
- **Functions**: `sin(45)`, `cos(30)`, `tg(45)`, `ctg(45)`

## How It Works

1. **Tokenization**:  
   The input expression is split into tokens (numbers, operators, functions, parentheses) using regex. User-defined constants are replaced with their values during this phase.

2. **RPN Conversion**:  
   Tokens are converted to Reverse Polish Notation using the Shunting Yard algorithm, respecting operator precedence and parentheses.

3. **Evaluation**:  
   The RPN expression is evaluated using a stack. Trigonometric functions convert inputs to radians internally.

## Dependencies

- [`regex`](https://crates.io/crates/regex): For tokenizing the input expression.
- [`rustyline`](https://crates.io/crates/rustyline): For command history
- [`num traits`](https://crates.io/crates/num-traits)

## Notes

- Use parentheses to enforce evaluation order (e.g., `(3 + 5) * 2`).
- Negative numbers are supported (e.g., `-5 + 3`).
- Constants persist until the program exits.
- All trigonometric functions expect degrees (converted to radians internally).

---

Feel free to contribute or report issues!
