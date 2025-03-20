use crate::text::TextSource;
use serde::{Deserialize, Serialize};
use std::time::Instant;

#[derive(Clone, Debug, Default, PartialEq, Serialize, Deserialize)]
pub struct TypingStats {
    pub wpm: f64,

    pub cpm: f64,

    pub accuracy: f64,

    pub correct_chars: usize,

    pub incorrect_chars: usize,

    pub total_chars: usize,

    pub max_wpm: f64,

    pub wpm_samples: Vec<f64>,

    #[serde(skip)]
    pub last_sample_time: Option<Instant>,
}

#[derive(Serialize, Deserialize)]
pub struct SerializableTypingStats {
    pub wpm: f64,
    pub cpm: f64,
    pub accuracy: f64,
    pub correct_chars: usize,
    pub incorrect_chars: usize,
    pub total_chars: usize,
    pub max_wpm: f64,
    pub wpm_samples: Vec<f64>,
}

impl From<&TypingStats> for SerializableTypingStats {
    fn from(stats: &TypingStats) -> Self {
        Self {
            wpm: stats.wpm,
            cpm: stats.cpm,
            accuracy: stats.accuracy,
            correct_chars: stats.correct_chars,
            incorrect_chars: stats.incorrect_chars,
            total_chars: stats.total_chars,
            max_wpm: stats.max_wpm,
            wpm_samples: stats.wpm_samples.clone(),
        }
    }
}

impl From<SerializableTypingStats> for TypingStats {
    fn from(stats: SerializableTypingStats) -> Self {
        Self {
            wpm: stats.wpm,
            cpm: stats.cpm,
            accuracy: stats.accuracy,
            correct_chars: stats.correct_chars,
            incorrect_chars: stats.incorrect_chars,
            total_chars: stats.total_chars,
            max_wpm: stats.max_wpm,
            wpm_samples: stats.wpm_samples,
            last_sample_time: None,
        }
    }
}

impl TypingStats {
    pub fn update(&mut self, text_source: &TextSource, typed_text: &str) {
        let target_text = text_source.full_text();

        self.correct_chars = 0;
        self.incorrect_chars = 0;

        for (i, typed_char) in typed_text.chars().enumerate() {
            if i < target_text.len() {
                let target_char = target_text.chars().nth(i).unwrap();
                if typed_char == target_char {
                    self.correct_chars += 1;
                } else {
                    self.incorrect_chars += 1;
                }
            } else {
                self.incorrect_chars += 1;
            }
        }

        self.total_chars = typed_text.len();

        if self.total_chars > 0 {
            self.accuracy = (self.correct_chars as f64 / self.total_chars as f64) * 100.0;
        } else {
            self.accuracy = 0.0;
        }

        let now = Instant::now();
        if self.last_sample_time.is_none()
            || now
                .duration_since(self.last_sample_time.unwrap())
                .as_secs_f64()
                >= 1.0
        {
            self.wpm_samples.push(self.wpm);
            self.last_sample_time = Some(now);
        }
    }

    pub fn calculate_wpm(&mut self, elapsed_seconds: f64) {
        if elapsed_seconds > 0.0 {
            let minutes = elapsed_seconds / 60.0;
            self.cpm = self.correct_chars as f64 / minutes;
            self.wpm = self.cpm / 5.0;

            if self.wpm > self.max_wpm {
                self.max_wpm = self.wpm;
            }
        }
    }

    pub fn finalize(&mut self) {
        self.wpm_samples.push(self.wpm);
    }

    pub fn net_wpm(&self) -> f64 {
        let gross_wpm = self.wpm;
        let error_penalty = self.incorrect_chars as f64 / 5.0;
        (gross_wpm - error_penalty).max(0.0)
    }

    pub fn to_json(&self) -> String {
        let serializable = SerializableTypingStats::from(self);
        serde_json::to_string(&serializable).unwrap_or_else(|_| String::from("{}"))
    }

    pub fn from_json(json: &str) -> Self {
        serde_json::from_str::<SerializableTypingStats>(json)
            .map(TypingStats::from)
            .unwrap_or_default()
    }
}

#[derive(Clone, Debug, Default, Serialize, Deserialize)]
pub struct TestHistory {
    pub tests: Vec<TestResult>,

    pub best_wpm: f64,

    pub average_wpm: f64,

    pub total_tests: usize,

    pub total_time: f64,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct TestResult {
    pub timestamp: chrono::DateTime<chrono::Utc>,

    pub duration: f64,

    pub wpm: f64,

    pub accuracy: f64,

    pub mode: String,
}

impl TestHistory {
    pub fn add_result(&mut self, result: TestResult) {
        self.tests.push(result.clone());
        self.total_tests += 1;
        self.total_time += result.duration;

        if result.wpm > self.best_wpm {
            self.best_wpm = result.wpm;
        }

        let total_wpm: f64 = self.tests.iter().map(|t| t.wpm).sum();
        self.average_wpm = total_wpm / self.total_tests as f64;
    }
}
