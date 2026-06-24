// src/stats_io.rs
use crate::game::{InputMode, GameModeOption};
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::{
    fs, io,
    path::PathBuf,
    time::Duration,
};

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct GameSessionStats {
    pub score: u32,
    pub timestamp: DateTime<Utc>,
    pub timed_mode: GameModeOption,
}

// Struct to store statistics for a single problem
#[derive(Debug, Clone)]
pub struct ProblemStat {
    pub problem_text: String,
    pub correct_answer: i32,
    pub user_answer_if_incorrect: Option<String>,
    pub time_taken: Duration,
    pub is_correct: bool,
}

// Stores detailed statistics for a round of play (not serialized)
#[derive(Debug, Clone)]
pub struct DetailedRoundStats {
    pub input_mode: InputMode,
    pub problems: Vec<ProblemStat>,
}

impl DetailedRoundStats {
    pub fn new(input_mode: InputMode) -> Self {
        DetailedRoundStats {
            input_mode,
            problems: Vec::new(),
        }
    }
}

fn get_stats_filename() -> String {
    "game_stats.json".to_string()
}

fn get_stats_path() -> Result<PathBuf, io::Error> {
    let filename = get_stats_filename();
    let mut path = std::env::current_dir()?;
    path.push(filename);
    Ok(path)
}

pub fn load_all_stats_for_mode(
    timed_mode: &GameModeOption,
) -> Result<Vec<GameSessionStats>, Box<dyn std::error::Error>> {
    if *timed_mode == GameModeOption::Unlimited {
        return Ok(Vec::new());
    }
    let path = get_stats_path()?;
    if !path.exists() {
        return Ok(Vec::new());
    }
    let json_data = fs::read_to_string(path)?;
    if json_data.trim().is_empty() {
        return Ok(Vec::new());
    }
    let all_stats: Vec<GameSessionStats> = serde_json::from_str(&json_data)?;
    let filtered_stats = all_stats
        .into_iter()
        .filter(|stat| stat.timed_mode == *timed_mode)
        .collect();
    Ok(filtered_stats)
}

pub fn append_game_session_stats(
    session_stats: &GameSessionStats,
) -> Result<(), Box<dyn std::error::Error>> {
    if session_stats.timed_mode == GameModeOption::Unlimited {
        return Ok(());
    }
    let path = get_stats_path()?;
    let mut all_stats = if path.exists() {
        let json_data = fs::read_to_string(&path)?;
        if json_data.trim().is_empty() {
            Vec::new()
        } else {
            serde_json::from_str(&json_data).unwrap_or_else(|_| Vec::new())
        }
    } else {
        Vec::new()
    };

    all_stats.push(session_stats.clone());

    let json_data = serde_json::to_string_pretty(&all_stats)?;
    fs::write(path, json_data)?;
    Ok(())
}
