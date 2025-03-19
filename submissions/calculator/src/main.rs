use regex::Regex;
use std::collections::{HashMap, HashSet, VecDeque};
use rustyline::error::ReadlineError;
use rustyline::Editor;

const HELP_MSG: &str = r"
Scientific Calculator Help:
---------------------------
Available operations:
  Basic: + - * / ^ 
  Functions: sin(θ) cos(θ) tg(θ) ctg(θ)
  Parentheses: ( )
  Constants: export NAME = VALUE
  
Examples:
  3 + 5 * 2
  sin(45) ^ 2
  export PI = 3.1415
  2 * PI / 180

Special commands:
  help    - Show this message
  exit    - Quit the program
  export  - Define constants

Notes:
- Angles in degrees
- Use parentheses for explicit order
- Negative numbers: -5 + 3
- Ctrl+C to exit
";

#[derive(Debug, Clone)]
struct Token {
    token: String,
    value: String,
}

fn tokenize(expression: &str, consts: &HashMap<String, String>) -> Vec<Token> {
    let const_keys = consts.keys()
    .map(|s| regex::escape(s))
    .collect::<Vec<String>>()
    .join("|");

    let token_pattern = if const_keys.is_empty() {
        r"\b(sin|cos|tg|ctg)\b|\d*\.\d+|\d+|[()+\-*/^]".to_string()
    } else {
        format!(r"\b(sin|cos|tg|ctg|{})\b|\d*\.\d+|\d+|[()+\-*/^]", const_keys)
    };

    let token_regex = Regex::new(&token_pattern).unwrap();
    
    let mut tokens = Vec::new();
    let mut pos = 0;

    while pos < expression.len() {
        let matched;

        if let Some(m) = token_regex.find(&expression[pos..]) {
            let mut val = m.as_str();
            let mut token_type = match val {
                "(" => "LPAREN",
                ")" => "RPAREN",
                "*" => "MUL",
                "/" => "DIV",
                "+" => "ADD",
                "-" => "SUB",
                "^" => "POW",
                "sin" => "SIN",
                "cos" => "COS",
                "tg" => "TAN",
                "ctg" => "COT",
                _ if consts.contains_key(val) => "CONST",
                _ if val.chars().all(|c| c.is_digit(10) || c == '.') => "NUM",
                _ => {
                    println!("Invalid character found: '{}'", val);
                    return vec![];
                }
            };
            if token_type == "CONST" {
                val = consts.get(val).unwrap();
                token_type = "NUM";
            }

            tokens.push(Token {
                token: token_type.to_string(),
                value: val.to_string(),
            });
            pos += m.end();
            matched = true;
        }
        else {
            println!("Invalid character at position {}: {}", pos, &expression[pos..]);
            return vec![];
        }

        if !matched {
            println!("Invalid character at position {}: {}", pos, &expression[pos..]);
            return vec![];
        }
    }
    tokens
}

fn rpn(tokens: Vec<Token>) -> std::result::Result<Vec<String>, String>  {
    let mut stack: Vec<Token> = Vec::new();
    let mut trygo_stack: Vec<Token> = Vec::new();
    let mut out: Vec<String> = vec![];

    let precedence = HashMap::from([
        ("LPAREN", -1), ("RPAREN", -1),
        ("SIN", 0), ("COS", 0), ("TAN", 0), ("CTG", 0),
        ("SUB", 1), ("ADD", 1),
        ("DIV", 2), ("MUL", 2),
        ("POW", 3)
    ]);

    let operators = HashSet::from([
        "-", "+", "/", "*", "^",
    ]);

    let trygo = HashSet::from([
        "sin", "cos", "tg", "ctg",
    ]);

    let mut paren_count = 0;
    let mut i = 0;

    while i < tokens.len() {
        let token = &tokens[i];

        if token.value == "-" && (i == 0 || operators.contains(tokens[i-1].value.as_str())) {
            if i + 1 >= tokens.len() || tokens[i + 1].token != "NUM" {
                return Err("Invalid syntax: Expected number after '-'.".to_string());
            }
            out.push(["-", tokens[i+1].value.as_str()].join(""));
            i += 2;
            continue;
        }
        else if token.token == "NUM" {
            out.push(token.value.clone());
        } else if operators.contains(token.value.as_str()) {
            let current_prec = precedence[token.token.as_str()];
    
            while let Some(top) = stack.last() {
                if let Some(&top_prec) = precedence.get(top.token.as_str()) {
                    if top_prec >= current_prec {
                        out.push(stack.pop().unwrap().value);
                    } else {
                        break;
                    }
                } else {
                    break;
                }
            }
            stack.push(token.clone());
        } else if trygo.contains(token.value.as_str()) {
            trygo_stack.push(token.clone());
        } else if token.value == "(" {
            stack.push(token.clone());
            paren_count += 1;
        } else if token.value == ")" {
            paren_count -= 1;
            while let Some(top) = stack.pop() {
                if top.value == "(" {
                    break;
                }
                out.push(top.value);
            }
            if paren_count == 0 && !trygo_stack.is_empty(){
                out.push(trygo_stack.pop().unwrap().value);
            }
            if paren_count < 0 {
                return Err("Mismatched parentheses.".to_string());
            }
        }
        i += 1;
    }

    if paren_count > 0 {
        return Err("Mismatched parentheses.".to_string());
    }

    while let Some(top) = stack.pop() {
        if top.value != ")" && top.value != "(" {
            out.push(top.value);
        }
    }
    Ok(out)
}

fn calc_trygo(x: f64, func: fn(f64) -> f64) -> f64 {
    if x % 180.0 == 90.0 && func == f64::tan {
        println!("Undefined tangent value");
        0.
    } else {
        func(x.to_radians())
    }
}

fn calc_value(rpn: Vec<String>) -> Option<f64> {
    let mut stack: VecDeque<f64> = VecDeque::new();

    for token in rpn {
        match token.to_lowercase().as_str() {
            "*" | "/" | "+" | "-" | "^" => {
                let y = stack.pop_back();
                let x = stack.pop_back();

                if let (Some(x), Some(y)) = (x, y) {
                    let z = match token.as_str() {
                        "*" => x * y,
                        "/" => {
                            if y == 0.0 {
                                println!("Division by zero");
                                return None;
                            }
                            x / y
                        }
                        "+" => x + y,
                        "-" => x - y,
                        "^" => x.powf(y),
                        _ => unreachable!(),
                    };
                    stack.push_back(z);
                }
                 else {
                    return None;
                }
            }
            "sin" | "cos" | "tg" | "ctg" => {
                let x = stack.pop_back();

                if let Some(x) = x {
                    let z = match token.as_str() {
                        "sin" => calc_trygo(x, f64::sin),
                        "cos" => calc_trygo(x, f64::cos),
                        "tg" => calc_trygo(x, f64::tan),
                        "ctg" => {
                            if calc_trygo(x, f64::tan) != 0. {
                                calc_trygo(x, f64::tan).powf(-1.)
                            } else {
                                0.
                            }
                        },
                        _ => unreachable!(),
                    };
                    stack.push_back(z);
                }
                 else {
                    return None;
                }
            }
            _ => {
                if let Ok(num) = token.parse::<f64>() {
                    stack.push_back(num);
                } else {
                    return None;
                }
            }
        }
    }
    if stack.len() == 1 {
        stack.pop_back()
    } else {
        None
    }
}

fn calculator(expr: &str, consts: &HashMap<String, String>) -> Option<f64> {
    let tokens: Vec<Token> = tokenize(&expr, consts);

    match rpn(tokens) {
        Ok(out) => {
            match calc_value(out) {
                Some(result) => {
                    println!("Result = {}", result);
                    Some(result)
                },
                None => {
                    println!("Error: Invalid operation in RPN.");
                    return None
                },
            }
        },
        Err(e) => {
            println!("Error: {}", e);
            return None
        },
    }
}

fn main() {
    let mut rl = Editor::<(), _>::new().unwrap();

    let mut consts: HashMap<String, String> = HashMap::new();
    let assign_regex = Regex::new(r"^export\s+\w+\s*=\s*.*$").unwrap();
    let keywords: [&str; 6] = ["export", "sin", "cos", "tg", "ctg", "help"];
    println!("Welcome to this Scientific Calculator written in Rust!");
    println!("Type help for instructions\n");

    let _ = rl.load_history("history.txt");

    loop {
        match rl.readline(">> ") {
            Ok(line) => {
                if line.trim() == "exit" {
                    println!("Exiting...");
                    break;
                }
                else if line == "help" {
                    println!("{}", HELP_MSG);
                }
                else if assign_regex.is_match(line.as_str()) {
                    let parts: Vec<&str> = line.splitn(2, '=').collect();
                    let var_name = parts[0].trim_start_matches("export").trim();
                    if !var_name.chars().all(|c| c.is_alphabetic()) || keywords.contains(&var_name) {
                        println!("Please choose different variable name");
                        continue;
                    }
        
                    let value = calculator(parts[1].trim(), &consts);
                    match value {
                        Some(result) => {
                            println!("Variable: {}, Value: {}", var_name, result);
                            consts.insert(var_name.to_string(), result.to_string());
                        },
                        None => println!("Error: Invalid operation in RPN."),
                    }
                } else {
                    calculator(&line, &consts);
                }
                let _ = rl.add_history_entry(line.as_str());
            }
            Err(ReadlineError::Eof) | Err(ReadlineError::Interrupted) => {
                println!("Exiting...");
                break;
            }
            Err(_) => {
                println!("Error");
                break;
            }
        }
    }
    let _ = rl.save_history("history.txt");
}