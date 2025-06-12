use crate::config::{Config, Difficulty, TestMode};
use rand::{seq::SliceRandom, thread_rng};

const EASY_WORDS: &str = include_str!("word_lists/easy.txt");
const MEDIUM_WORDS: &str = include_str!("word_lists/medium.txt");
const HARD_WORDS: &str = include_str!("word_lists/hard.txt");

const QUOTES: &str = include_str!("word_lists/quotes.txt");

const WORDS_BATCH_SIZE: u32 = 50;

const MAX_TEXT_LENGTH: usize = 800;

const TARGET_TEXT_LENGTH: usize = 600;

pub struct TextSource {
    text: String,

    difficulty: Difficulty,

    is_infinite: bool,

    pub is_scrollable: bool,

    total_words: u32,

    loaded_words: u32,
}

impl TextSource {
    pub fn new(config: &Config) -> Self {
        if config.repeat_test && config.last_test_text.is_some() {
            let is_infinite = matches!(config.test_mode, TestMode::Timed(_));

            let (is_scrollable, total_words) = match config.test_mode {
                TestMode::Words(count) if count > WORDS_BATCH_SIZE => (true, count),
                TestMode::Words(count) => (false, count),
                _ => (false, 0),
            };

            return Self {
                text: config.last_test_text.clone().unwrap(),
                difficulty: config.difficulty,
                is_infinite,
                is_scrollable,
                total_words,
                loaded_words: if is_scrollable {
                    WORDS_BATCH_SIZE
                } else {
                    total_words
                },
            };
        }

        let is_infinite = matches!(config.test_mode, TestMode::Timed(_));

        let (is_scrollable, total_words, initial_words) = match config.test_mode {
            TestMode::Words(count) if count > WORDS_BATCH_SIZE => (true, count, WORDS_BATCH_SIZE),
            TestMode::Words(count) => (false, count, count),
            _ => (false, 0, 0),
        };

        let text = match config.test_mode {
            TestMode::Words(_count) if is_scrollable => {
                Self::generate_words(config.difficulty, initial_words)
            }
            TestMode::Words(count) => Self::generate_words(config.difficulty, count),
            TestMode::Timed(_) => Self::generate_words(config.difficulty, WORDS_BATCH_SIZE),
            TestMode::Quote => Self::get_random_quote(),
            TestMode::Custom => config
                .custom_text
                .clone()
                .unwrap_or_else(|| "Type here".to_string()),
        };

        Self {
            text,
            difficulty: config.difficulty,
            is_infinite,
            is_scrollable,
            total_words,
            loaded_words: initial_words,
        }
    }

    pub fn should_add_more_words(&self, cursor_pos: usize) -> bool {
        if !self.is_infinite && !self.is_scrollable {
            return false;
        }

        if self.is_scrollable && self.loaded_words >= self.total_words {
            return false;
        }

        let cursor_threshold = self.text.len() * 3 / 4;

        cursor_pos > cursor_threshold
    }

    pub fn add_more_words(&mut self) -> usize {
        if !self.is_infinite && !self.is_scrollable {
            return 0;
        }

        if self.is_scrollable && self.loaded_words >= self.total_words {
            return 0;
        }

        let words_to_add = if self.is_scrollable {
            let remaining = self.total_words - self.loaded_words;

            remaining.min(WORDS_BATCH_SIZE)
        } else {
            WORDS_BATCH_SIZE
        };

        let additional_words = Self::generate_words(self.difficulty, words_to_add);

        if !self.text.is_empty() {
            self.text.push(' ');
        }

        self.text.push_str(&additional_words);

        if self.is_scrollable {
            self.loaded_words += words_to_add;
        }

        let mut trimmed_count = 0;

        if self.text.len() > MAX_TEXT_LENGTH {
            let text_to_keep = TARGET_TEXT_LENGTH;

            let trim_start_pos = self.text.len() - text_to_keep;

            if trim_start_pos > 0 && self.text.len() > text_to_keep {
                if let Some(space_pos) = self.text[trim_start_pos..].find(' ') {
                    let trim_pos = trim_start_pos + space_pos + 1;

                    if trim_pos < self.text.len() {
                        trimmed_count = trim_pos;
                        self.text = self.text[trim_pos..].to_string();
                    }
                } else {
                    trimmed_count = self.text.len() - text_to_keep;
                    self.text = self.text[trimmed_count..].to_string();
                }
            }
        }

        trimmed_count
    }

    pub fn save_to_config(&self, config: &mut Config) {
        if config.repeat_test {
            config.last_test_text = Some(self.text.clone());
            config.save().ok();
        }
    }

    pub fn full_text(&self) -> &str {
        &self.text
    }

    pub fn total_words(&self) -> u32 {
        if self.is_scrollable {
            self.total_words
        } else {
            self.text.split_whitespace().count() as u32
        }
    }

    pub fn is_complete(&self) -> bool {
        if self.is_scrollable {
            self.loaded_words >= self.total_words
        } else {
            true
        }
    }

    fn generate_words(difficulty: Difficulty, count: u32) -> String {
        let word_list = match difficulty {
            Difficulty::Easy => EASY_WORDS,
            Difficulty::Medium => MEDIUM_WORDS,
            Difficulty::Hard => HARD_WORDS,
            Difficulty::Custom => MEDIUM_WORDS,
        };

        let words: Vec<&str> = word_list.lines().collect();
        let mut rng = thread_rng();

        let mut result = String::new();
        for i in 0..count {
            if i > 0 {
                result.push(' ');
            }
            if let Some(word) = words.choose(&mut rng) {
                result.push_str(word);
            }
        }

        result
    }

    fn get_random_quote() -> String {
        let quotes: Vec<&str> = QUOTES.split("\n\n").collect();
        let mut rng = thread_rng();

        if let Some(quote) = quotes.choose(&mut rng) {
            quote.to_string()
        } else {
            "The quick brown fox jumps over the lazy dog.".to_string()
        }
    }
}
