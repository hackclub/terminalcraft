use device_query::{DeviceQuery, DeviceState, Keycode};
use std::{thread, time::{Duration, Instant}};
use std::io::{self, Write};
use crossterm::{
    terminal::{self, EnterAlternateScreen, LeaveAlternateScreen, Clear, ClearType},
    cursor::MoveTo,
    execute
};
use std::collections::HashMap;
use std::env;
use std::fs::File;
use std::io::BufReader;
use serde_json::Value;
use rand::seq::SliceRandom;
use rand::thread_rng;


fn morse_mapping() -> HashMap<&'static str, char> {
    let mut map = HashMap::new();

    map.insert(".-", 'A');
    map.insert("-...", 'B');
    map.insert("-.-.", 'C');
    map.insert("-..", 'D');
    map.insert(".", 'E');
    map.insert("..-.", 'F');
    map.insert("--.", 'G');
    map.insert("....", 'H');
    map.insert("..", 'I');
    map.insert(".---", 'J');
    map.insert("-.-", 'K');
    map.insert(".-..", 'L');
    map.insert("--", 'M');
    map.insert("-.", 'N');
    map.insert("---", 'O');
    map.insert(".--.", 'P');
    map.insert("--.-", 'Q');
    map.insert(".-.", 'R');
    map.insert("...", 'S');
    map.insert("-", 'T');
    map.insert("..-", 'U');
    map.insert("...-", 'V');
    map.insert(".--", 'W');
    map.insert("-..-", 'X');
    map.insert("-.--", 'Y');
    map.insert("--..", 'Z');
    map.insert(".----", '1');
    map.insert("..---", '2');
    map.insert("...--", '3');
    map.insert("....-", '4');
    map.insert(".....", '5');
    map.insert("-....", '6');
    map.insert("--...", '7');
    map.insert("---..", '8');
    map.insert("----.", '9');
    map.insert("-----", '0');
    map
}

fn latin_to_morse_mapping() -> HashMap<char, &'static str> {
    morse_mapping()
        .iter()
        .map(|(k, v)| (*v, *k))
        .collect()
}

fn decode_morse(morse: &str) -> String {
    let mapping = morse_mapping();
    let mut result = String::new();
    let words: Vec<&str> = morse.split(' ').filter(|w| !w.is_empty()).collect();
    
    for word in words {
        let letters: Vec<&str> = word.split('/').filter(|l| !l.is_empty()).collect();
        let mut decoded_word = String::new();
        
        for letter in letters {
            if let Some(&char) = mapping.get(letter) {
                decoded_word.push(char);
            } else {
                decoded_word.push('�');
            }
        }
        
        if !decoded_word.is_empty() {
            result.push_str(&decoded_word);
            result.push(' '); 
        }
    }
    
    result.trim().to_string()
}

fn format_morse_table() -> Vec<String> {
    let mapping = latin_to_morse_mapping();
    let mut table = Vec::new();
    
    table.push("LETTERS:".to_string());
    let letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    let mut letter_lines = Vec::new();
    
    for (i, c) in letters.chars().enumerate() {
        if i % 8 == 0 {
            letter_lines.push(String::new());
        }
        if let Some(code) = mapping.get(&c) {
            let last = letter_lines.len() - 1;
            letter_lines[last] += &format!("  {}: {:<8}", c, code);
        }
    }
    
    table.extend(letter_lines);
    table.push("".to_string()); 
    
    table.push("NUMBERS:".to_string());
    let numbers = "1234567890";
    let mut number_lines = Vec::new();
    
    for (i, c) in numbers.chars().enumerate() {
        if i % 8 == 0 {
            number_lines.push(String::new());
        }
        if let Some(code) = mapping.get(&c) {
            let last = number_lines.len() - 1;
            number_lines[last] += &format!("  {}: {:<8}", c, code);
        }
    }
    
    table.extend(number_lines);
    table
}

fn load_words(language_code: &str, count: usize) -> Vec<String> {
    let path = format!("thousand-most-common-words/words/{}.json", language_code);
    let file = File::open(&path).expect("Failed to open word file");
    let reader = BufReader::new(file);
    let json: Value = serde_json::from_reader(reader).expect("Invalid JSON format");
    
    let words_array = json["words"].as_array().expect("Invalid words format");
    let mut words = Vec::new();
    
    for word in words_array {
        let word_str = if language_code == "en" {
            word["englishWord"].as_str()
        } else {
            word["targetWord"].as_str()
        };
        
        if let Some(w) = word_str {
            words.push(w.to_uppercase());
        }
    }
    
    let mut rng = thread_rng();
    words.shuffle(&mut rng);
    words.into_iter().take(count).collect()
}

fn main() -> io::Result<()> {
    let args: Vec<String> = env::args().collect();
    let language_code = args.get(1).map(|s| s.as_str()).unwrap_or("en");
    let word_count = args.get(2).and_then(|s| s.parse().ok()).unwrap_or(10);
    let threshold_ms = args.get(3).and_then(|s| s.parse().ok()).unwrap_or(150);
    
    let words = load_words(language_code, word_count);
    let mut current_word_index = 0;
    let mut morse_output = String::new();
    let mut decoded_text = String::new();
    
    let mut stdout = io::stdout();
    execute!(
        stdout,
        EnterAlternateScreen,
        Clear(ClearType::All)
    )?;
    terminal::enable_raw_mode()?;

    let mut line = 0;
    execute!(stdout, MoveTo(0, line))?;
    println!("Morse Code Typing Trainer");
    line += 1;
    execute!(stdout, MoveTo(0, line))?;
    println!("-------------------------------------------");
    line += 1;
    execute!(stdout, MoveTo(0, line))?;
    println!("Language: {}", language_code);
    line += 1;
    execute!(stdout, MoveTo(0, line))?;
    println!("Words to type: {}", word_count);
    line += 1;
    execute!(stdout, MoveTo(0, line))?;
    println!("Press Threshold: {} ms", threshold_ms);
    line += 1;
    
    let stats_line = line;
    line += 1;
    let wpm_line = line;
    line += 1;
    execute!(stdout, MoveTo(0, line))?;
    println!("Exit: Press 'Q' or 'Esc'");
    line += 1;
    execute!(stdout, MoveTo(0, line))?;
    println!("Space: Short press (.) / Long press (-)");
    line += 1;
    execute!(stdout, MoveTo(0, line))?;
    println!("F: Insert '/' (letter separator)");
    line += 1;
    execute!(stdout, MoveTo(0, line))?;
    println!("J: Insert space (word separator)");
    line += 1;
    execute!(stdout, MoveTo(0, line))?;
    println!("Semicolon (;): Backspace");
    line += 1;
    execute!(stdout, MoveTo(0, line))?;
    println!("-------------------------------------------");
    line += 1;

    let word_line = line;
    line += 1;
    execute!(stdout, MoveTo(0, word_line))?;
    println!("Type this word: {}", words[current_word_index]);
    line += 1;

    let morse_table = format_morse_table();
    for row in &morse_table {
        execute!(stdout, MoveTo(0, line))?;
        println!("{}", row);
        line += 1;
    }
    
    execute!(stdout, MoveTo(0, line))?;
    println!("-------------------------------------------");
    line += 1;

    let current_morse_line = line;
    line += 1;
    let decoded_line = line;
    
    execute!(stdout, MoveTo(0, current_morse_line))?;
    print!("Your Morse: ");
    execute!(stdout, MoveTo(0, decoded_line))?;
    print!("Decoded: ");
    stdout.flush()?;

    let device_state = DeviceState::new();
    let mut prev_space_pressed = false;
    let mut prev_f_pressed = false;
    let mut prev_j_pressed = false;
    let mut prev_semicolon_pressed = false;
    
    let mut space_press_time: Option<Instant> = None;
    let mut completed = false;
    
    let start_time = Instant::now();
    let mut last_update = Instant::now();
    const UPDATE_INTERVAL: Duration = Duration::from_millis(100);

    loop {
        let keys = device_state.get_keys();
        
        if keys.contains(&Keycode::Q) || keys.contains(&Keycode::Escape) {
            break;
        }
        
        let now = Instant::now();
        if now.duration_since(last_update) > UPDATE_INTERVAL {
            last_update = now;
            
            let elapsed = start_time.elapsed();
            let elapsed_secs = elapsed.as_secs_f64();
            let wpm = if elapsed_secs > 0.0 {
                (current_word_index as f64 / elapsed_secs) * 60.0
            } else {
                0.0
            };
            
            execute!(stdout, MoveTo(0, stats_line))?;
            execute!(stdout, Clear(ClearType::UntilNewLine))?;
            print!("Elapsed: {:.1}s", elapsed_secs);
            
            execute!(stdout, MoveTo(0, wpm_line))?;
            execute!(stdout, Clear(ClearType::UntilNewLine))?;
            print!("Current WPM: {:.1}", wpm);
            
            stdout.flush()?;
        }
        
        let space_pressed = keys.contains(&Keycode::Space);
        match (space_pressed, prev_space_pressed) {
            (true, false) => {
                space_press_time = Some(Instant::now());
            },
            (false, true) => {
                if let Some(start) = space_press_time {
                    let duration = start.elapsed();
                    
                    if duration.as_millis() <= threshold_ms {
                        morse_output.push('.');
                    } else {
                        morse_output.push('-');
                    }
                    
                    execute!(stdout, MoveTo(10, current_morse_line))?;
                    execute!(stdout, Clear(ClearType::UntilNewLine))?;
                    print!("{}", morse_output);
                    
                    decoded_text = decode_morse(&morse_output);
                    execute!(stdout, MoveTo(10, decoded_line))?;
                    execute!(stdout, Clear(ClearType::UntilNewLine))?;
                    print!("{}", decoded_text);
                    
                    stdout.flush()?;
                }
            },
            _ => {}
        }
        prev_space_pressed = space_pressed;
        
        let f_pressed = keys.contains(&Keycode::F);
        if !f_pressed && prev_f_pressed {
            morse_output.push('/');
            
            execute!(stdout, MoveTo(10, current_morse_line))?;
            execute!(stdout, Clear(ClearType::UntilNewLine))?;
            print!("{}", morse_output);
            
            decoded_text = decode_morse(&morse_output);
            execute!(stdout, MoveTo(10, decoded_line))?;
            execute!(stdout, Clear(ClearType::UntilNewLine))?;
            print!("{}", decoded_text);
            
            stdout.flush()?;
        }
        prev_f_pressed = f_pressed;
        
        let j_pressed = keys.contains(&Keycode::J);
        if !j_pressed && prev_j_pressed {
            morse_output.push(' ');
            
            execute!(stdout, MoveTo(10, current_morse_line))?;
            execute!(stdout, Clear(ClearType::UntilNewLine))?;
            print!("{}", morse_output);
            
            decoded_text = decode_morse(&morse_output);
            execute!(stdout, MoveTo(10, decoded_line))?;
            execute!(stdout, Clear(ClearType::UntilNewLine))?;
            print!("{}", decoded_text);
            
            stdout.flush()?;
        }
        prev_j_pressed = j_pressed;
        
        let semicolon_pressed = keys.contains(&Keycode::Semicolon);
        if !semicolon_pressed && prev_semicolon_pressed && !morse_output.is_empty() {
            morse_output.pop();
            
            execute!(stdout, MoveTo(10, current_morse_line))?;
            execute!(stdout, Clear(ClearType::UntilNewLine))?;
            print!("{}", morse_output);
            
            decoded_text = decode_morse(&morse_output);
            execute!(stdout, MoveTo(10, decoded_line))?;
            execute!(stdout, Clear(ClearType::UntilNewLine))?;
            print!("{}", decoded_text);
            
            stdout.flush()?;
        }
        prev_semicolon_pressed = semicolon_pressed;
        
        if !completed && decoded_text.trim() == words[current_word_index] {
            completed = true;
            
            current_word_index += 1;
            if current_word_index < words.len() {
                morse_output.clear();
                decoded_text.clear();
                completed = false;
                
                execute!(stdout, MoveTo(0, word_line))?;
                execute!(stdout, Clear(ClearType::UntilNewLine))?;
                println!("Type this word: {}", words[current_word_index]);
                
                execute!(stdout, MoveTo(10, current_morse_line))?;
                execute!(stdout, Clear(ClearType::UntilNewLine))?;
                execute!(stdout, MoveTo(10, decoded_line))?;
                execute!(stdout, Clear(ClearType::UntilNewLine))?;
            } else {
                break;
            }
        }
        
        thread::sleep(Duration::from_millis(5));
    }

    let elapsed_time = start_time.elapsed();
    let total_seconds = elapsed_time.as_secs() as f64 + elapsed_time.subsec_millis() as f64 / 1000.0;
    let wpm = if total_seconds > 0.0 {
        (words.len() as f64 / total_seconds) * 60.0
    } else {
        0.0
    };

    terminal::disable_raw_mode()?;
    execute!(stdout, LeaveAlternateScreen)?;
    
    println!("\nTraining completed!");
    println!("Words practiced: {}", words.len());
    println!("Total time: {:.2} seconds", total_seconds);
    println!("Average speed: {:.1} words per minute", wpm);
    println!("Final Morse Code: {}", morse_output);
    println!("Decoded Message: {}", decoded_text);
    Ok(())
}