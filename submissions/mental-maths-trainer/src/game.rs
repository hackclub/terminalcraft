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

#[derive(Debug, Clone)]
pub struct Problem {
    pub answer: i32,
    pub text: String,
}

impl Problem {
    pub fn new(difficulty: &DifficultySettings) -> Self {
        let mut rng = rand::thread_rng();

        if difficulty.operator_count > 1 {
            let mut numbers = Vec::new();
            let mut operators = Vec::new();
            let answer: i32;
            let mut text = String::new();

            let allowed_ops = [Operation::Add, Operation::Subtract];

            for _ in 0..difficulty.operator_count {
                numbers.push(rng.gen_range(difficulty.min_val..=difficulty.max_val));
            }

            // Generate operators
            for _ in 0..(difficulty.operator_count - 1) {
                let op_idx = rng.gen_range(0..allowed_ops.len());
                operators.push(allowed_ops[op_idx]);
            }

            // Build text and calculate answer
            text.push_str(&numbers[0].to_string());
            let mut current_answer = numbers[0];

            for i in 0..(difficulty.operator_count - 1) as usize {
                text.push(' ');
                text.push_str(operators[i].to_string());
                text.push(' ');
                text.push_str(&numbers[i + 1].to_string());

                match operators[i] {
                    Operation::Add => current_answer += numbers[i + 1],
                    Operation::Subtract => current_answer -= numbers[i + 1],
                    _ => {} // Should not happen
                }
            }
            answer = current_answer;

            Problem {
                answer,
                text,
            }
        } else {
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
                    let n2 = rng.gen_range(difficulty.min_val..=mul_max.max(difficulty.min_val));
                    (n1, n2, n1 * n2)
                }
                Operation::Divide => {
                    // Ensure n2 is not zero and n1 is divisible by n2
                    let n2_max = (difficulty.max_val as f32).sqrt() as i32;
                    let n2 = rng.gen_range(
                        difficulty.min_val.max(1)..=n2_max.max(difficulty.min_val.max(1)),
                    );
                    let n1_max = difficulty.max_val / n2;
                    let n1 = rng.gen_range(difficulty.min_val..=n1_max.max(difficulty.min_val));
                    (n1 * n2, n2, n1)
                }
            };
            let text = format!("{} {} {}", num1, operator.to_string(), num2);
            Problem {
                answer,
                text,
            }
        }
    }

    pub fn check_answer(&self, user_answer: i32) -> bool {
        user_answer == self.answer
    }
}

#[derive(Debug, Clone, Copy, PartialEq, Serialize, Deserialize)]
pub enum GameModeOption {
    ThirtySeconds,
    SixtySeconds,
    OneTwentySeconds,
    Unlimited,
    EstimationEasy,
    EstimationHard,
}

impl GameModeOption {
    pub fn to_duration(&self) -> Option<Duration> {
        match self {
            GameModeOption::ThirtySeconds => Some(Duration::from_secs(30)),
            GameModeOption::SixtySeconds => Some(Duration::from_secs(60)),
            GameModeOption::OneTwentySeconds => Some(Duration::from_secs(120)),
            GameModeOption::EstimationEasy => Some(Duration::from_secs(60)),
            GameModeOption::EstimationHard => Some(Duration::from_secs(60)),
            GameModeOption::Unlimited => None,
        }
    }

    pub fn next(&self) -> Self {
        match self {
            GameModeOption::ThirtySeconds => GameModeOption::SixtySeconds,
            GameModeOption::SixtySeconds => GameModeOption::OneTwentySeconds,
            GameModeOption::OneTwentySeconds => GameModeOption::EstimationEasy,
            GameModeOption::EstimationEasy => GameModeOption::EstimationHard,
            GameModeOption::EstimationHard => GameModeOption::Unlimited,
            GameModeOption::Unlimited => GameModeOption::ThirtySeconds,
        }
    }

    pub fn to_string(&self) -> String {
        match self {
            GameModeOption::ThirtySeconds => "30 Seconds".to_string(),
            GameModeOption::SixtySeconds => "60 Seconds".to_string(),
            GameModeOption::OneTwentySeconds => "120 Seconds".to_string(),
            GameModeOption::EstimationEasy => "Estimation (within 5%)".to_string(),
            GameModeOption::EstimationHard => "Estimation (within 10%)".to_string(),
            GameModeOption::Unlimited => "Unlimited".to_string(),
        }
    }
    
    pub fn is_estimation_mode(&self) -> bool {
        matches!(self, GameModeOption::EstimationEasy | GameModeOption::EstimationHard)
    }
    
    pub fn get_estimation_threshold(&self) -> Option<f64> {
        match self {
            GameModeOption::EstimationEasy => Some(0.10),
            GameModeOption::EstimationHard => Some(0.05),
            _ => None,
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
    pub game_mode: GameModeOption,
    pub operator_count: u32,
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
            game_mode: GameModeOption::Unlimited,
            operator_count: 1,
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
