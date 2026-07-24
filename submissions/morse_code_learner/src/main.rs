use std::{
    collections::{VecDeque, HashMap},
    fs,
    io::{self, Write},
    path::PathBuf,
    time::Instant,
};
use rand::{seq::SliceRandom, rngs::ThreadRng};
use serde_derive::{Serialize, Deserialize};
use serde::{Deserialize, Serialize};
use chrono;
use rodio::{source::SineWave, OutputStream, Sink, Source};
use std::thread;


const DOT_DURATION_MS: u64 = 80;
const DASH_DURATION_MS: u64 = 500;

const MORSE_MAPPING: [(char, &str); 36] = [
    ('A', ".-"), ('B', "-..."), ('C', "-.-."), ('D', "-.."), ('E', "."), ('F', "..-."),
    ('G', "--."), ('H', "...."), ('I', ".."), ('J', ".---"), ('K', "-.-"), ('L', ".-.."),
    ('M', "--"), ('N', "-."), ('O', "---"), ('P', ".--."), ('Q', "--.-"), ('R', ".-."),
    ('S', "..."), ('T', "-"), ('U', "..-"), ('V', "...-"), ('W', ".--"), ('X', "-..-"),
    ('Y', "-.--"), ('Z', "--.."), ('1', ".----"), ('2', "..---"), ('3', "...--"),
    ('4', "....-"), ('5', "....."), ('6', "-...."), ('7', "--..."), ('8', "---.."),
    ('9', "----."), ('0', "-----"),
];

#[derive(Debug, Serialize, Deserialize, Clone)]
struct AppConfig {
    difficulty_level: u8,
    session_duration: u32,
    known_chars: Vec<char>,
}

impl Default for AppConfig {
    fn default() -> Self {
        AppConfig {
            difficulty_level: 1,
            session_duration: 5,
            known_chars: vec![],
        }
    }
}

fn play_morse_code(morse_code: &str) {
    let (_stream, stream_handle) = match OutputStream::try_default() {
        Ok(stream) => stream,
        Err(e) => {
            eprintln!("Error creating audio output: {}", e);
            return;
        }
    };
    
    let sink = match Sink::try_new(&stream_handle) {
        Ok(sink) => sink,
        Err(e) => {
            eprintln!("Error creating audio sink: {}", e);
            return;
        }
    };

    for symbol in morse_code.chars() {
        match symbol {
            '.' => play_beep(&sink, DOT_DURATION_MS),
            '-' => play_beep(&sink, DASH_DURATION_MS),
            ' ' => thread::sleep(std::time::Duration::from_millis(3 * DOT_DURATION_MS)),
            _ => {}
        }
        thread::sleep(std::time::Duration::from_millis(DOT_DURATION_MS));
    }
}

fn play_beep(sink: &Sink, duration_ms: u64) {
    let source = SineWave::new(600.0)
        .take_duration(std::time::Duration::from_millis(duration_ms))
        .amplify(0.2);
    sink.append(source);
    thread::sleep(std::time::Duration::from_millis(duration_ms));
}

#[derive(Debug, Serialize, Deserialize, Default)]
struct UserStats {
    sessions_completed: u32,
    chars_learned: u32,
    words_learned: u32,
    accuracy: f32,
    #[serde(serialize_with = "serialize_response_times")]
    #[serde(deserialize_with = "deserialize_response_times")]
    response_times: HashMap<char, f32>,
    word_response_times: HashMap<String, f32>,
    session_history: Vec<LearningSession>,
}

fn serialize_response_times<S>(
    map: &HashMap<char, f32>,
    serializer: S,
) -> Result<S::Ok, S::Error>
where
    S: serde::Serializer,
{
    let string_map: HashMap<String, f32> = map
        .iter()
        .map(|(k, v)| (k.to_string(), *v))
        .collect();
    string_map.serialize(serializer)
}

fn deserialize_response_times<'de, D>(
    deserializer: D,
) -> Result<HashMap<char, f32>, D::Error>
where
    D: serde::Deserializer<'de>,
{
    let string_map = HashMap::<String, f32>::deserialize(deserializer)?;
    let char_map = string_map
        .into_iter()
        .map(|(k, v)| (k.chars().next().unwrap(), v))
        .collect();
    Ok(char_map)
}

#[derive(Debug, Serialize, Deserialize)]
struct LearningSession {
    timestamp: String,
    duration: u32,
    chars_practiced: Vec<char>,
    words_practiced: Vec<String>,
    accuracy: f32,
    difficulty: u8,
}

#[derive(Debug)]
struct ProgressionSystem {
    levels: Vec<ProgressionLevel>,
    common_words: Vec<String>,
}

#[derive(Debug)]
struct ProgressionLevel {
    level: u8,
    chars_to_learn: Vec<char>,
    speed_requirement: f32,
    accuracy_requirement: f32,
}

struct MorseTutor {
    config: AppConfig,
    stats: UserStats,
    progression: ProgressionSystem,
    practice_queue: VecDeque<String>,
    session_start: Instant,
    correct_answers: u32,
    total_answers: u32,
    is_word_level: bool,
    rng: ThreadRng,
}

impl MorseTutor {
    fn new() -> Self {
        let config = AppConfig::load().unwrap_or_default();
        let stats = UserStats::load().unwrap_or_default();
        let progression = ProgressionSystem::new();
        
        let is_word_level = config.difficulty_level >= 9;
        
        MorseTutor {
            config: config.clone(),
            stats,
            progression,
            practice_queue: VecDeque::new(),
            session_start: Instant::now(),
            correct_answers: 0,
            total_answers: 0,
            is_word_level,
            rng: rand::rng(),
        }
    }

    fn generate_practice_queue(&mut self) {
        self.practice_queue.clear();
        
        if self.is_word_level {
            let mut selected_words = self.progression.common_words.clone();
            selected_words.shuffle(&mut self.rng);
            
            for word in selected_words.into_iter().take(10) {
                self.practice_queue.push_back(word);
            }
        } else {
            let mut chars = self.config.known_chars.clone();
            chars.shuffle(&mut self.rng);
            
            if let Some(level) = self.progression.levels.iter()
                .find(|l| l.level == self.config.difficulty_level) 
            {
                for c in &level.chars_to_learn {
                    if !chars.contains(c) {
                        chars.push(*c);
                    }
                }
            }
            
            for _ in 0..5 {
                for c in &chars {
                    self.practice_queue.push_back(c.to_string());
                }
            }
        }
    }

    fn end_session(&mut self) {
        let duration = self.session_start.elapsed().as_secs() as u32;
        let accuracy = if self.total_answers > 0 {
            self.correct_answers as f32 / self.total_answers as f32
        } else {
            0.0
        };
        
        if let Some(session) = self.stats.session_history.last_mut() {
            session.duration = duration;
            session.accuracy = accuracy;
            
            if self.is_word_level {
                session.words_practiced = self.practice_queue.iter().cloned().collect();
            } else {
                session.chars_practiced = self.practice_queue.iter()
                    .filter_map(|s| s.chars().next())
                    .collect();
            }
        }
        
        self.stats.sessions_completed += 1;
        self.stats.accuracy = (self.stats.accuracy * (self.stats.sessions_completed - 1) as f32 + accuracy) / 
                            self.stats.sessions_completed as f32;

        if let Err(e) = self.config.save() {
            eprintln!("Error saving configuration: {}", e);
        }

        if let Err(e) = self.stats.save() {
            eprintln!("Error saving stats: {}", e);
        }
        
        self.show_summary();
        self.update_progression();
    }

    fn practice_item(&mut self, item: &str) -> bool {
        let morse_code = if self.is_word_level {
            self.encode_word(item)
        } else {
            Self::char_to_morse(item.chars().next().unwrap())
                .map(|s| s.to_string())
                .unwrap_or_default()
        };
        
        println!("\n--- New {} ---", if self.is_word_level { "Word" } else { "Character" });
        println!("Level: {} | Exercises left: {}", 
            self.config.difficulty_level,
            self.practice_queue.len()
        );
        println!("{}: {}", if self.is_word_level { "Word" } else { "Character" }, item);
        
        print!("Your Morse code: ");
        io::stdout().flush().unwrap();
        
        let start_time = Instant::now();
        let mut input = String::new();
        io::stdin().read_line(&mut input).expect("Error reading input");
        let response_time = start_time.elapsed().as_secs_f32();
        
        let input = input.trim().to_uppercase();
        let correct = input == morse_code;
        
        self.total_answers += 1;
        
        if self.is_word_level {
            self.stats.word_response_times.insert(item.to_string(), response_time);
            self.stats.words_learned += 1;
        } else {
            if let Some(c) = item.chars().next() {
                self.stats.response_times.insert(c, response_time);
                self.stats.chars_learned += 1;
            }
        }

        if correct {
            self.correct_answers += 1;
            println!("✓ Correct! (time: {:.1}s)", response_time);
        } else {
            println!("✗ Incorrect! Correct code: {} (your: {})", morse_code, input);
        }

        let morse_audio = morse_code.clone();
        thread::spawn(move || {
            play_morse_code(&morse_audio);
        });
        
        correct
    }

    fn char_to_morse(c: char) -> Option<&'static str> {
        MORSE_MAPPING.iter()
            .find(|(ch, _)| *ch == c.to_ascii_uppercase())
            .map(|(_, code)| *code)
    }
    
    fn encode_word(&self, word: &str) -> String {
        word.chars()
            .filter_map(Self::char_to_morse)
            .collect::<Vec<&str>>()
            .join(" ")
    }

    fn start_session(&mut self) {
        self.generate_practice_queue();
        
        println!("\nNew session started!");
        println!("Difficulty level: {}", self.config.difficulty_level);
        
        if self.is_word_level {
            println!("Mode: Word Practice (10 common words)");
        } else {
            if let Some(level) = self.progression.levels.iter()
                .find(|l| l.level == self.config.difficulty_level) 
            {
                let mut chars: Vec<char> = self.config.known_chars.clone();
                for c in &level.chars_to_learn {
                    if !chars.contains(c) {
                        chars.push(*c);
                    }
                }
                println!("Characters to learn: {}", chars.iter().collect::<String>());
            } else {
                println!("Characters to learn: {}", self.config.known_chars.iter().collect::<String>());
            }
        }
        
        println!("Exercise number: {}", self.practice_queue.len());
        println!("------------------------------------------------");

        self.session_start = Instant::now();
        self.stats.session_history.push(LearningSession {
            timestamp: chrono::Local::now().to_rfc3339(),
            duration: 0,
            chars_practiced: vec![],
            words_practiced: vec![],
            accuracy: 0.0,
            difficulty: self.config.difficulty_level,
        });

        self.correct_answers = 0;
        self.total_answers = 0;
    }

    fn run(&mut self) {
        self.start_session();       
        while let Some(current_item) = self.practice_queue.front().cloned() {
            if self.session_start.elapsed().as_secs() > self.config.session_duration as u64 * 60 
            {
                println!("\n⏰ Time passed!");
                break;
            }
            
            let correct = self.practice_item(&current_item);
            
            if correct {
                self.practice_queue.pop_front();
            } else {
                if let Some(item) = self.practice_queue.pop_front() {
                    self.practice_queue.push_back(item);
                }
            }
            
            print!("Press 'q' to quit or Enter to continue: ");
            io::stdout().flush().unwrap();
            
            let mut input = String::new();
            io::stdin().read_line(&mut input).expect("Error reading input");
            
            if input.trim().eq_ignore_ascii_case("q") {
                println!("\nSession interrupted");
                break;
            }
        }
        
        self.end_session();
    }

    fn show_summary(&self) {
        let duration = self.session_start.elapsed().as_secs() as u32;
        let minutes = duration / 60;
        let seconds = duration % 60;
        let accuracy = if self.total_answers > 0 {
            (self.correct_answers as f32 / self.total_answers as f32) * 100.0
        } else {
            0.0
        };
        
        println!("\n================================================");
        println!("                SESSION SUMMARY");
        println!("================================================");
        println!("Duration:      {:02}:{:02}", minutes, seconds);
        println!("Exercise number:    {}", self.total_answers);
        println!("Correct answers: {}/{} ({:.1}%)", 
            self.correct_answers, self.total_answers, accuracy);
        println!("Difficulty:  {}", self.config.difficulty_level);

        if self.is_word_level {
            if !self.stats.word_response_times.is_empty() {
                println!("\nWord statistics:");
                for (word, time) in &self.stats.word_response_times {
                    println!("  {}: {:.1}s", word, time);
                }
                
                let avg_time: f32 = self.stats.word_response_times.values().sum::<f32>() / 
                                   self.stats.word_response_times.len() as f32;
                println!("Average reaction time: {:.1}s", avg_time);
            }
        } else {
            if !self.stats.response_times.is_empty() {
                println!("\nCharacter statistics:");
                for (c, time) in &self.stats.response_times {
                    println!("  {}: {:.1}s", c, time);
                }
                
                let avg_time: f32 = self.stats.response_times.values().sum::<f32>() / 
                                   self.stats.response_times.len() as f32;
                println!("Average reaction time: {:.1}s", avg_time);
            }
        }
        
        println!("================================================");
    }

    fn update_progression(&mut self) {
        let current_level = self.config.difficulty_level;
        
        if self.is_word_level {
            println!("\nCongrats! You're practicing words!");
            println!("Continue to improve your word encoding speed.");
            return;
        }
        
        if let Some(level) = self.progression.levels.iter().find(|l| l.level == current_level) {
            let accuracy = if self.total_answers > 0 {
                self.correct_answers as f32 / self.total_answers as f32
            } else {
                0.0
            };

            let avg_time = if !self.stats.response_times.is_empty() {
                self.stats.response_times.values().sum::<f32>() / 
                self.stats.response_times.len() as f32
            } else {
                0.0
            };
            
            println!("\nLevel requirements {}:", current_level);
            println!("- Accuracy: {:.1}% (required: {:.1}%)", 
                accuracy * 100.0, level.accuracy_requirement * 100.0);

            println!("- Average time: {:.1}s (required: {:.1}s)", 
                avg_time, level.speed_requirement);

            if avg_time <= level.speed_requirement && accuracy >= level.accuracy_requirement {
                self.config.difficulty_level += 1;
                println!("\n🎉 Advanced to level {}!", self.config.difficulty_level);
                
                if self.config.difficulty_level == 9 {
                    self.is_word_level = true;
                    println!("🌟 CONGRATULATIONS! You've reached word level!");
                    println!("Now you'll practice encoding common words.");
                } else {
                    if let Some(next_level) = self.progression.levels.iter()
                        .find(|l| l.level == self.config.difficulty_level) 
                    {
                        for c in &next_level.chars_to_learn {
                            if !self.config.known_chars.contains(c) {
                                self.config.known_chars.push(*c);
                                println!("+ New char added: {}", c);
                            }
                        }
                    }
                }
                
                self.generate_practice_queue();
            } else {
                println!("\nℹ️ Continue practicing on current level.");
            }

            if let Err(e) = self.config.save() {
                eprintln!("Error saving configuration: {}", e);
            }
        }
    }
}

impl AppConfig {
    fn config_path() -> PathBuf {
        PathBuf::from("morse_config.toml")
    }

    fn load() -> Result<Self, Box<dyn std::error::Error>> {
        let path = Self::config_path();
        if path.exists() {
            let data = fs::read_to_string(&path)?;
            toml::from_str(&data).map_err(|e| e.into())
        } else {
            let config = AppConfig::default();
            config.save()?;
            Ok(config)
        }
    }

    fn save(&self) -> Result<(), Box<dyn std::error::Error>> {
        let path = Self::config_path();
        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent)?;
        }
        
        let data = toml::to_string(self)?;
        fs::write(&path, data)?;
        Ok(())
    }
}

impl UserStats {
    fn stats_path() -> PathBuf {
        PathBuf::from("morse_stats.toml")
    }

    fn load() -> Result<Self, Box<dyn std::error::Error>> {
        let path = Self::stats_path();
        if path.exists() {
            let data = fs::read_to_string(&path)?;
            toml::from_str(&data).map_err(|e| e.into())
        } else {
            Ok(UserStats::default())
        }
    }

    fn save(&self) -> Result<(), Box<dyn std::error::Error>> {
        let path = Self::stats_path();
        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent)?;
        }
        let data = toml::to_string(self)?;
        fs::write(path, data)?;
        Ok(())
    }
}

impl ProgressionSystem {
    fn new() -> Self {
        let levels = vec![
            ProgressionLevel {
                level: 1,
                chars_to_learn: vec!['E', 'T'],
                speed_requirement: 5.0,
                accuracy_requirement: 0.8,
            },
            ProgressionLevel {
                level: 2,
                chars_to_learn: vec!['A', 'I', 'M', 'N'],
                speed_requirement: 4.0,
                accuracy_requirement: 0.85,
            },
            ProgressionLevel {
                level: 3,
                chars_to_learn: vec!['D', 'G', 'K', 'O'],
                speed_requirement: 3.5,
                accuracy_requirement: 0.9,
            },
            ProgressionLevel {
                level: 4,
                chars_to_learn: vec!['R', 'S', 'U', 'W'],
                speed_requirement: 3.5,
                accuracy_requirement: 0.9,
            },
            ProgressionLevel {
                level: 5,
                chars_to_learn: vec!['B', 'C', 'F', 'H', 'J', 'L'],
                speed_requirement: 3.0,
                accuracy_requirement: 0.95,
            },
            ProgressionLevel {
                level: 6,
                chars_to_learn: vec!['P', 'Q', 'V', 'X', 'Y', 'Z'],
                speed_requirement: 3.0,
                accuracy_requirement: 0.95,
            },
            ProgressionLevel {
                level: 7,
                chars_to_learn: vec!['0', '1', '2', '3', '4'],
                speed_requirement: 2.5,
                accuracy_requirement: 0.95,
            },
            ProgressionLevel {
                level: 8,
                chars_to_learn: vec!['5', '6', '7', '8', '9'],
                speed_requirement: 2.5,
                accuracy_requirement: 0.95,
            },
        ];
        
        let common_words = match fs::read_to_string("common_words.txt") {
            Ok(contents) => {
                contents.lines()
                    .map(|s| s.trim().to_uppercase())
                    .filter(|s| !s.is_empty())
                    .collect()
            }
            Err(_) => {
                println!("Warning: common_words.txt not found. Using default words.");
                vec![
                    "THE".to_string(),
                    "BE".to_string(),
                    "TO".to_string(),
                    "OF".to_string(),
                    "AND".to_string(),
                    "A".to_string(),
                    "IN".to_string(),
                    "THAT".to_string(),
                    "HAVE".to_string(),
                    "I".to_string(),
                    "IT".to_string(),
                    "FOR".to_string(),
                    "NOT".to_string(),
                    "ON".to_string(),
                    "WITH".to_string(),
                    "HE".to_string(),
                    "AS".to_string(),
                    "YOU".to_string(),
                    "DO".to_string(),
                    "AT".to_string(),
                ]
            }
        };
        
        ProgressionSystem {
            levels,
            common_words,
        }
    }
}

fn main() {
    println!("================================================");
    println!("               MORSE CODE LEARNER");
    println!("================================================");
    println!("Progression system:");
    println!("- Levels 1-8: Character encoding");
    println!("- Level 9: Word encoding");
    println!("================================================");
    
    let mut app = MorseTutor::new();
    app.run();
}
