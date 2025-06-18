use crate::stats::DetailedRoundStats;
use rand::Rng;
use serde::{Deserialize, Serialize};
use std::time::{Duration, Instant};

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub enum Operation {
    Add,
    Subtract,
    Multiply,
    Divide,
}

impl Operation {
    pub fn to_string(&self) -> &str {
        match self {
            Operation::Add => "+",
            Operation::Subtract => "-",
            Operation::Multiply => "*",
            Operation::Divide => "/",
        }
    }
}

#[derive(Debug, Clone, Copy)]
pub struct Problem {
    pub num1: i32,
    pub num2: i32,
    pub operator: Operation,
    pub answer: i32,
}

impl Problem {
    pub fn new(difficulty: &DifficultySettings) -> Self {
        let mut rng = rand::thread_rng();
        let op_idx = rng.gen_range(0..difficulty.allowed_ops.len());
        let operator = difficulty.allowed_ops[op_idx];

        let (num1, num2, answer) = match operator {
            Operation::Add => {
                let n1 = rng.gen_range(difficulty.min_val..=difficulty.max_val);
                let n2 = rng.gen_range(difficulty.min_val..=difficulty.max_val);
                (n1, n2, n1 + n2)
            }
            Operation::Subtract => {
                let n1 = rng.gen_range(difficulty.min_val..=difficulty.max_val);
                let n2 = rng.gen_range(difficulty.min_val..=n1); // Ensure positive result
                (n1, n2, n1 - n2)
            }
            Operation::Multiply => {
                // Limit range for multiplication to avoid large numbers
                let mul_max = (difficulty.max_val as f32).sqrt() as i32;
                let n1 = rng.gen_range(difficulty.min_val..=difficulty.max_val);
                let n2 = rng.gen_range(difficulty.min_val..=mul_max);
                (n1, n2, n1 * n2)
            }
            Operation::Divide => {
                // Ensure n2 is not zero and n1 is divisible by n2
                let div_max = (difficulty.max_val as f32).sqrt() as i32;
                let n1 = rng.gen_range(difficulty.min_val..=difficulty.max_val);
                let n2 = rng.gen_range(difficulty.min_val..=div_max);
                (n1 * n2, n2, n1)
            }
        };
        Problem {
            num1,
            num2,
            operator,
            answer,
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub enum TimedModeOption {
    ThirtySeconds,
    SixtySeconds,
    OneTwentySeconds,
    Unlimited,
}

impl TimedModeOption {
    pub fn to_duration(&self) -> Option<Duration> {
        match self {
            TimedModeOption::ThirtySeconds => Some(Duration::from_secs(30)),
            TimedModeOption::SixtySeconds => Some(Duration::from_secs(60)),
            TimedModeOption::OneTwentySeconds => Some(Duration::from_secs(120)),
            TimedModeOption::Unlimited => None,
        }
    }

    pub fn next(&self) -> Self {
        match self {
            TimedModeOption::ThirtySeconds => TimedModeOption::SixtySeconds,
            TimedModeOption::SixtySeconds => TimedModeOption::OneTwentySeconds,
            TimedModeOption::OneTwentySeconds => TimedModeOption::Unlimited,
            TimedModeOption::Unlimited => TimedModeOption::ThirtySeconds,
        }
    }

    pub fn to_string(&self) -> String {
        match self {
            TimedModeOption::ThirtySeconds => "30 Seconds".to_string(),
            TimedModeOption::SixtySeconds => "60 Seconds".to_string(),
            TimedModeOption::OneTwentySeconds => "120 Seconds".to_string(),
            TimedModeOption::Unlimited => "Unlimited".to_string(),
        }
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub enum InputMode {
    AutoSubmit,
    EnterToSubmit,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DifficultySettings {
    pub min_val: i32,
    pub max_val: i32,
    pub allowed_ops: Vec<Operation>,
    pub input_mode: InputMode,
    pub timed_mode: TimedModeOption,
}

impl Default for DifficultySettings {
    fn default() -> Self {
        DifficultySettings {
            min_val: 2,
            max_val: 144,
            allowed_ops: vec![
                Operation::Add,
                Operation::Subtract,
                Operation::Multiply,
                Operation::Divide,
            ],
            input_mode: InputMode::EnterToSubmit,
            timed_mode: TimedModeOption::Unlimited,
        }
    }
}

#[derive(Debug)]
pub struct GameState {
    pub active_problem: Option<Problem>,
    pub user_input: String,
    pub current_score: u32,
    pub feedback_message: Option<String>,
    pub question_given_at: Instant,
    pub remaining_time: Option<Duration>,
    pub difficulty_settings: DifficultySettings,
    pub playing: bool,
    pub detailed_round_stats: DetailedRoundStats,
}

impl GameState {
    pub fn new(initial_difficulty: DifficultySettings) -> Self {
        GameState {
            active_problem: None,
            user_input: String::new(),
            current_score: 0,
            feedback_message: None,
            question_given_at: Instant::now(),
            remaining_time: None,
            difficulty_settings: initial_difficulty.clone(),
            playing: false,
            detailed_round_stats: DetailedRoundStats::new(initial_difficulty.input_mode),
        }
    }

    pub fn generate_new_problem(&mut self) {
        self.active_problem = Some(Problem::new(&self.difficulty_settings));
    }
}
