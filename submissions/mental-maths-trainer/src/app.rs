use std::time::{Duration, Instant};

use crate::config;
use crate::game::{DifficultySettings, GameState, InputMode, Operation, Problem};
use crate::stats::{self, ProblemStat};
use chrono::Utc;

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Screen {
    MainMenu,
    ProblemScreen,
    SettingsScreen,
    StatsScreen,
    DetailedRoundScreen,
}

#[derive(Debug)]
pub enum Msg {
    KeyPress(char),
    Backspace,
    SubmitAnswer,
    SwitchScreen(Screen),
    TimerTick,
    Quit,
    IncrementMinVal,
    DecrementMinVal,
    IncrementMaxVal,
    DecrementMaxVal,
    IncrementOperatorCount,
    DecrementOperatorCount,
    ToggleOperator(Operation),
    ToggleInputMode,
    ToggleTimedMode,
    ToggleChartType,
}

pub struct Model {
    pub current_screen: Screen,
    pub game_state: GameState,
    pub difficulty_settings: DifficultySettings,
    pub exit: bool,
    pub stats_data: Vec<stats::GameSessionStats>,
    pub stats_show_rolling_average: bool,
}

impl Model {
    pub fn new() -> Self {
        let loaded_settings = config::load_settings().unwrap_or_else(|err| {
            eprintln!("Failed to load or initialize settings: {}. Using in-memory default for this session.", err);
            DifficultySettings::default()
        });

        Model {
            current_screen: Screen::MainMenu,
            game_state: GameState::new(loaded_settings.clone()),
            difficulty_settings: loaded_settings,
            exit: false,
            stats_data: Vec::new(),
            stats_show_rolling_average: false,
        }
    }
}

pub fn update(model: &mut Model, msg: Msg) {
    match model.current_screen {
        Screen::MainMenu => {
            match msg {
                Msg::SwitchScreen(screen) => {
                    model.current_screen = screen;
                    if screen == Screen::ProblemScreen {
                        // Start a new game session
                        model.game_state = GameState::new(model.difficulty_settings.clone());
                        model.game_state.generate_new_problem();
                        model.game_state.playing = true;
                        if let Some(duration) = model.difficulty_settings.game_mode.to_duration() {
                            model.game_state.remaining_time = Some(duration);
                        } else {
                            model.game_state.remaining_time = None;
                        }
                        model.game_state.question_given_at = Instant::now();
                    } else if screen == Screen::StatsScreen {
                        // Load stats for the selected timed_mode
                        match stats::load_all_stats_for_mode(&model.difficulty_settings.game_mode)
                        {
                            Ok(data) => model.stats_data = data,
                            Err(e) => {
                                eprintln!("Failed to load stats: {}", e);
                                model.stats_data = Vec::new();
                            }
                        }
                        model.stats_show_rolling_average = false;
                    }
                }
                Msg::Quit => model.exit = true,
                _ => {}
            }
        }
        Screen::ProblemScreen => {
            match msg {
                Msg::KeyPress(c) => {
                    if !model.game_state.playing {
                        return;
                    }
                    model.game_state.user_input.push(c);
                    if model.game_state.difficulty_settings.input_mode != InputMode::AutoSubmit
                       || model.game_state.difficulty_settings.game_mode.is_estimation_mode() {
                        return;
                    }
                    if let Some(problem) = &model.game_state.active_problem {
                        if let Ok(user_answer) = model.game_state.user_input.parse::<i32>() {
                            if problem.check_answer(user_answer) { return; }
                            model.game_state.current_score += 1;
                            let problem_stat = ProblemStat {
                                problem_text: get_problem_text(Some(&problem)),
                                correct_answer: problem.answer,
                                user_answer_if_incorrect: None,
                                time_taken: model.game_state.question_given_at.elapsed(),
                                is_correct: true,
                            };
                            model
                                .game_state
                                .detailed_round_stats
                                .problems
                                .push(problem_stat);
                            model.game_state.question_given_at = Instant::now();
                            model.game_state.generate_new_problem();
                            model.game_state.user_input.clear();
                        }
                    }
                }
                Msg::Backspace => {
                    if !model.game_state.playing {
                        return;
                    }
                    model.game_state.user_input.pop();
                }
                Msg::SubmitAnswer => {
                    if !model.game_state.playing {
                        return;
                    }
                    if let Some(problem) = &model.game_state.active_problem {
                        if let Ok(answer) = model.game_state.user_input.parse::<i32>() {
                            let is_correct = problem.check_answer(answer);
                            let mut estimation_correct = false;
                            if is_correct {
                                model.game_state.current_score += 1;
                                model.game_state.feedback_message = Some("Correct!".to_string());
                            } else if let Some(threshold) = model.game_state.difficulty_settings.game_mode.get_estimation_threshold() {
                                let answer_f64 = problem.answer as f64;
                                let user_answer_f64 = answer as f64;
                                let difference = (answer_f64 - user_answer_f64).abs();
                                let percentage_diff = difference / answer_f64;
        
                                if percentage_diff <= threshold {
                                    estimation_correct = true;
                                    model.game_state.current_score += 1;
                                    model.game_state.feedback_message = Some(format!("Good. The answer was {}", problem.answer));
                                } else {
                                    model.game_state.feedback_message = Some(format!("Too far off. The answer was {}.", problem.answer));
                                }
                            }
                            else {
                                model.game_state.feedback_message = Some(format!("Incorrect. The answer was {}.", problem.answer));
                            }
                            
                            // Record detailed stats
                            let elapsed = model.game_state.question_given_at.elapsed();
                            model.game_state.detailed_round_stats.problems.push(stats::ProblemStat {
                                problem_text: get_problem_text(Some(&problem)),
                                correct_answer: problem.answer,
                                user_answer_if_incorrect: if !is_correct && !estimation_correct {
                                    Some(answer.to_string())
                                } else {
                                    None
                                },
                                time_taken: elapsed,
                                is_correct,
                            });

                            // Generate new problem and reset input
                            model.game_state.user_input.clear();
                            model.game_state.generate_new_problem();
                            model.game_state.question_given_at = Instant::now();
                        }
                    }
                }
                Msg::SwitchScreen(Screen::DetailedRoundScreen) => {
                    if model.game_state.playing {
                        return;
                    }
                    model.current_screen = Screen::DetailedRoundScreen;
                }
                Msg::SwitchScreen(screen) => {
                    model.game_state.playing = false;
                    model.current_screen = screen;
                }
                Msg::TimerTick => {
                    if !model.game_state.playing {
                        return;
                    }
                    if let Some(ref mut remaining) = model.game_state.remaining_time {
                        let tick_duration = Duration::from_millis(100);
                        if *remaining > Duration::ZERO {
                            if *remaining > tick_duration {
                                *remaining -= tick_duration;
                            } else {
                                *remaining = Duration::ZERO;
                                model.game_state.playing = false;
                                let session_stat = stats::GameSessionStats {
                                    score: model.game_state.current_score,
                                    timestamp: Utc::now(),
                                    timed_mode: model.difficulty_settings.game_mode,
                                };
                                if model.game_state.current_score == 0 {
                                    model.game_state.feedback_message =
                                        Some(format!("AFK Detected, score not saved"));
                                    return;
                                }
                                if let Err(e) = stats::append_game_session_stats(&session_stat) {
                                    model.game_state.feedback_message =
                                        Some(format!("Error saving stats: {}", e));
                                } else {
                                    model.game_state.feedback_message = Some(format!(
                                        "Time's up! Final Score: {}.",
                                        model.game_state.current_score
                                    ));
                                }
                            }
                        }
                    }
                }
                _ => {}
            }
        }
        Screen::SettingsScreen => {
            match msg {
                Msg::SwitchScreen(screen) => {
                    model.current_screen = screen;
                    config::save_settings(&model.difficulty_settings)
                        .unwrap_or_else(|e| eprintln!("Error saving settings: {}", e));
                },
                Msg::IncrementMinVal => {
                    model.difficulty_settings.min_val = (model.difficulty_settings.min_val + 1)
                        .min(model.difficulty_settings.max_val - 1);
                    config::save_settings(&model.difficulty_settings).unwrap_or_default();
                    model.game_state.difficulty_settings = model.difficulty_settings.clone();
                }
                Msg::DecrementMinVal => {
                    model.difficulty_settings.min_val =
                        (model.difficulty_settings.min_val - 1).max(1);
                    config::save_settings(&model.difficulty_settings).unwrap_or_default();
                    model.game_state.difficulty_settings = model.difficulty_settings.clone();
                }
                Msg::IncrementMaxVal => {
                    model.difficulty_settings.max_val += 1;
                    config::save_settings(&model.difficulty_settings).unwrap_or_default();
                    model.game_state.difficulty_settings = model.difficulty_settings.clone();
                }
                Msg::DecrementMaxVal => {
                    model.difficulty_settings.max_val = (model.difficulty_settings.max_val - 1)
                        .max(model.difficulty_settings.min_val + 1);
                    config::save_settings(&model.difficulty_settings).unwrap_or_default();
                    model.game_state.difficulty_settings = model.difficulty_settings.clone();
                }
                Msg::IncrementOperatorCount => {
                    model.difficulty_settings.operator_count += 1;
                    config::save_settings(&model.difficulty_settings).unwrap_or_default();
                    model.game_state.difficulty_settings = model.difficulty_settings.clone();
                }
                Msg::DecrementOperatorCount => {
                    model.difficulty_settings.operator_count = (model.difficulty_settings.operator_count - 1).max(1);
                    config::save_settings(&model.difficulty_settings).unwrap_or_default();
                    model.game_state.difficulty_settings = model.difficulty_settings.clone();
                }
                Msg::ToggleOperator(op_to_toggle) => {
                    if let Some(pos) = model
                        .difficulty_settings
                        .allowed_ops
                        .iter()
                        .position(|&x| x == op_to_toggle)
                    {
                        if model.difficulty_settings.allowed_ops.len() > 1 {
                            model.difficulty_settings.allowed_ops.remove(pos);
                        }
                    } else {
                        model.difficulty_settings.allowed_ops.push(op_to_toggle);
                    }
                    config::save_settings(&model.difficulty_settings).unwrap_or_default();
                    model.game_state.difficulty_settings = model.difficulty_settings.clone();
                }
                Msg::ToggleInputMode => {
                    model.difficulty_settings.input_mode =
                        match model.difficulty_settings.input_mode {
                            InputMode::AutoSubmit => InputMode::EnterToSubmit,
                            InputMode::EnterToSubmit => InputMode::AutoSubmit,
                        };
                    config::save_settings(&model.difficulty_settings).unwrap_or_default();
                    model.game_state.difficulty_settings = model.difficulty_settings.clone();
                }
                Msg::ToggleTimedMode => {
                    model.difficulty_settings.game_mode =
                        model.difficulty_settings.game_mode.next();
                    config::save_settings(&model.difficulty_settings).unwrap_or_default();
                    model.game_state.difficulty_settings = model.difficulty_settings.clone();
                }
                _ => {}
            }
        }
        Screen::StatsScreen => {
            match msg {
                Msg::SwitchScreen(screen) => model.current_screen = screen,
                Msg::ToggleChartType => {
                    model.stats_show_rolling_average = !model.stats_show_rolling_average
                }
                Msg::ToggleTimedMode => {
                    model.difficulty_settings.game_mode =
                        model.difficulty_settings.game_mode.next();
                    config::save_settings(&model.difficulty_settings).unwrap_or_default();
                    model.game_state.difficulty_settings = model.difficulty_settings.clone();
                    match stats::load_all_stats_for_mode(&model.difficulty_settings.game_mode) {
                        Ok(data) => model.stats_data = data,
                        Err(e) => {
                            eprintln!("Failed to load stats: {}", e);
                            model.stats_data = Vec::new();
                        }
                    }
                }
                _ => {}
            }
        }
        Screen::DetailedRoundScreen => match msg {
            Msg::SwitchScreen(screen) => model.current_screen = screen,
            _ => {}
        },
    }
}

// Returns a formatted string for a math problem, or "None" if not present.
pub fn get_problem_text(problem: Option<&Problem>) -> String {
    if let Some(p) = problem {
        p.text.clone()
    } else {
        "None".to_string()
    }
}
