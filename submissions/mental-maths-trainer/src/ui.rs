use ratatui::{
    prelude::*,
    widgets::{Axis, Block, Borders, Chart, Dataset, GraphType, List, ListItem, Paragraph},
};

use crate::app::{get_problem_text, Model, Screen};
use crate::game::{InputMode, Operation};

pub fn view(model: &Model, frame: &mut Frame) {
    match model.current_screen {
        Screen::MainMenu => draw_main_menu(model, frame),
        Screen::ProblemScreen => draw_problem_screen(model, frame),
        Screen::SettingsScreen => draw_settings_screen(model, frame),
        Screen::StatsScreen => draw_stats_screen(model, frame),
        Screen::DetailedRoundScreen => draw_detailed_round_screen(model, frame),
    }
}

fn draw_main_menu(_model: &Model, frame: &mut Frame) {
    let area = frame.area();
    let title = Line::from(" Mental Maths Trainer ".bold()).alignment(Alignment::Center);
    // let instructions = Line::from(vec![
    //     "Press ".into(),
    //     "<P>".blue().bold(),
    //     " to Start, ".into(),
    //     "<S>".green().bold(),
    //     " for Settings, ".into(),
    //     "<T>".yellow().bold(),
    //     " for Stats, ".into(),
    //     "<Q>".red().bold(),
    //     " to Quit".into(),
    // ]);

    let block = Block::default().title(title).borders(Borders::ALL);

    let text_content = "Welcome to the Mental Maths Trainer!\n\n\
                        Press 'P' to start practicing.\n\
                        Press 'S' for Settings.\n\
                        Press 'T' for Stats.\n\n\
                        Press 'Q' to Quit.";

    let paragraph = Paragraph::new(text_content)
        .block(block)
        .alignment(Alignment::Center);

    frame.render_widget(paragraph, area);
}

fn draw_problem_screen(model: &Model, frame: &mut Frame) {
    let area = frame.area();
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Percentage(30), // For problem display
            Constraint::Percentage(20), // For user input area
            Constraint::Percentage(10), // For feedback message
            Constraint::Percentage(10), // For score display
            Constraint::Percentage(10), // For timer display
            Constraint::Percentage(20), // For controls/instructions
        ])
        .split(area);

    // Problem Display
    let problem_text = get_problem_text(model.game_state.active_problem.as_ref());
    let problem_paragraph = Paragraph::new(problem_text)
        .alignment(Alignment::Center)
        .block(Block::default().borders(Borders::ALL).title("Problem"));
    frame.render_widget(problem_paragraph, chunks[0]);

    // User Input Area
    let input_text = format!("Your answer: {}", model.game_state.user_input);
    let input_paragraph = Paragraph::new(input_text)
        .alignment(Alignment::Center)
        .block(Block::default().borders(Borders::ALL).title("Input"));
    frame.render_widget(input_paragraph, chunks[1]);

    // Feedback Message Display
    let feedback_display_text = if let Some(msg) = &model.game_state.feedback_message {
        msg.clone()
    } else {
        String::new()
    };
    let feedback_display_paragraph = Paragraph::new(feedback_display_text)
        .alignment(Alignment::Center)
        .block(Block::default().borders(Borders::NONE));
    frame.render_widget(feedback_display_paragraph, chunks[2]);

    // Score display
    let score_text = format!("Score: {}", model.game_state.current_score);
    let score_paragraph = Paragraph::new(score_text)
        .alignment(Alignment::Center)
        .block(Block::default().borders(Borders::NONE));
    frame.render_widget(score_paragraph, chunks[3]);

    // Timer Display
    let timer_text = if let Some(remaining) = model.game_state.remaining_time {
        format!("Time remaining: {:.0}s", remaining.as_secs_f32())
    } else {
        format!(
            "Time elapsed: {:.1}s",
            model.game_state.question_given_at.elapsed().as_secs_f32()
        )
    };
    let timer_paragraph = Paragraph::new(timer_text)
        .alignment(Alignment::Center)
        .block(Block::default().borders(Borders::NONE));
    frame.render_widget(timer_paragraph, chunks[4]);

    // Controls/Instructions
    let controls_text = if model.game_state.playing {
        if model
            .game_state
            .difficulty_settings
            .game_mode
            .is_estimation_mode()
        {
            "Type your estimate. Press <Enter> to Submit, <Q> to Main Menu."
        } else {
            match model.game_state.difficulty_settings.input_mode {
                InputMode::EnterToSubmit => {
                    "Type your answer. Press <Enter> to Submit, <Q> to Main Menu."
                }
                InputMode::AutoSubmit => {
                    "Type your answer. Correct answer submits automatically. <Q> to Main Menu."
                }
            }
        }
    } else {
        "Press <T> for round stats, <Q> to Main Menu."
    };
    let controls_paragraph = Paragraph::new(controls_text)
        .alignment(Alignment::Center)
        .block(Block::default().borders(Borders::ALL).title("Controls"));
    frame.render_widget(controls_paragraph, chunks[5]);
}

fn draw_settings_screen(model: &Model, frame: &mut Frame) {
    let area = frame.area();
    let current_settings = &model.difficulty_settings;

    let settings_items = vec![
        // Min Value Setting
        ListItem::new(
            Line::from(vec![
                "Min Value: ".into(),
                current_settings.min_val.to_string().green().bold().into(),
                " (L/R to change)".into(),
            ])
            .alignment(Alignment::Center),
        ),
        // Max Value Setting
        ListItem::new(
            Line::from(vec![
                "Max Value: ".into(),
                current_settings.max_val.to_string().green().bold().into(),
                " (Up/Down to change)".into(),
            ])
            .alignment(Alignment::Center),
        ),
        // Allowed Operators Setting
        ListItem::new(
            Line::from(vec![
                "Operators: ".into(),
                if current_settings.allowed_ops.contains(&Operation::Add) {
                    "+ ".green()
                } else {
                    "+ ".dim()
                }
                .into(),
                if current_settings.allowed_ops.contains(&Operation::Subtract) {
                    "- ".green()
                } else {
                    "- ".dim()
                }
                .into(),
                if current_settings.allowed_ops.contains(&Operation::Multiply) && current_settings.operator_count == 1 {
                    "* ".green()
                } else {
                    "* ".dim()
                }
                .into(),
                if current_settings.allowed_ops.contains(&Operation::Divide) && current_settings.operator_count == 1 {
                    "/ ".green()
                } else {
                    "/ ".dim()
                }
                .into(),
                "(1-4 to Toggle)".into(),
            ])
            .alignment(Alignment::Center),
        ),
        // Operator Count Setting
        ListItem::new(
            Line::from(vec![
                "Operator Count: ".into(),
                current_settings.operator_count.to_string().green().bold().into(),
                " (Press [ or ] to change)".into(),
            ])
            .alignment(Alignment::Center),
        ),
        // Input Mode Setting
        ListItem::new(
            Line::from(vec![
                "Input Mode: ".into(),
                match current_settings.input_mode {
                    InputMode::EnterToSubmit => "Enter to Submit".green(),
                    InputMode::AutoSubmit => match current_settings.input_mode {
                        InputMode::EnterToSubmit => "Enter to Submit".green(),
                        InputMode::AutoSubmit => {
                            if !current_settings.game_mode.is_estimation_mode() {
                                "Auto Submit".green()
                            } else {
                                "Enter to submit (estimation mode)".gray()
                            }
                        }
                    },
                }
                .into(),
                " (Press 'I' to Toggle)".into(),
            ])
            .alignment(Alignment::Center),
        ),
        // Game Mode Setting
        ListItem::new(
            Line::from(vec![
                "Game Mode: ".into(),
                current_settings.game_mode.to_string().green().bold().into(),
                " (Press 'T' to Toggle)".into(),
            ])
            .alignment(Alignment::Center),
        ),
    ];

    let settings_list = List::new(settings_items)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .title(" Settings ".bold())
                .title_alignment(Alignment::Center),
        )
        .highlight_symbol("> ");
    frame.render_widget(settings_list, area);
}

fn draw_stats_screen(model: &Model, frame: &mut Frame) {
    let area = frame.area();
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Min(0),    // For the chart
            Constraint::Length(3), // For controls/info
        ])
        .split(area);

    let stats_data = &model.stats_data;

    if stats_data.is_empty() {
        let no_data_paragraph = Paragraph::new(vec![
            "No stats available for the selected mode. Play some games first!\n".into(),
            "Tip: Switch modes in settings - Unlimited mode has no stats available.\n".into(),
            "\n".into(),
            "<T> to toggle timed mode. <Q> for Main Menu.".into(),
        ])
        .alignment(Alignment::Center)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .title(Line::from(vec![
                    "Stats for ".into(),
                    model
                        .difficulty_settings
                        .game_mode
                        .to_string()
                        .green()
                        .bold(),
                    " Mode".into(),
                ]))
                .title_alignment(Alignment::Center),
        );
        frame.render_widget(no_data_paragraph, area);
        return;
    }

    let mut datasets = vec![];

    // Scatter plot of scores
    let scatter_data: Vec<(f64, f64)> = stats_data
        .iter()
        .enumerate()
        .map(|(i, stat)| (i as f64 + 1.0, stat.score as f64))
        .collect();

    datasets.push(
        Dataset::default()
            .name("Score")
            .marker(symbols::Marker::Dot)
            .graph_type(GraphType::Scatter)
            .style(Style::default().fg(Color::Cyan))
            .data(&scatter_data),
    );

    let rolling_avg_data: Vec<(f64, f64)>;

    // Rolling average (5 games)
    if model.stats_show_rolling_average && stats_data.len() >= 5 {
        rolling_avg_data = stats_data
            .windows(5)
            .enumerate()
            .map(|(i, window)| {
                let sum: u32 = window.iter().map(|s| s.score).sum();
                ((i + 4) as f64 + 1.0, sum as f64 / 5.0) // +4 because window index is start, we plot at end of window
            })
            .collect();
        datasets.push(
            Dataset::default()
                .name("Rolling Avg (5 games)")
                .marker(symbols::Marker::Braille) // Using Braille for line charts often looks better
                .graph_type(GraphType::Line)
                .style(Style::default().fg(Color::Yellow))
                .data(&rolling_avg_data),
        );
    }

    let max_score = stats_data.iter().map(|s| s.score).max().unwrap_or(10) as f64;
    let x_axis_upper_bound = if stats_data.len() == 1 {
        2.0
    } else {
        stats_data.len() as f64
    };
    let x_axis_bounds = [1.0, x_axis_upper_bound.max(1.0)]; // Ensure upper bound is at least 1.0
    let y_axis_bounds = [0.0, (max_score.max(12.0) * 4.0 / 4.0).floor()]; // Ensure y-axis isn't too small and multiple of 4 for even labal spacing

    let chart_title = Line::from(vec![
        "Stats for ".into(),
        model
            .difficulty_settings
            .game_mode
            .to_string()
            .green()
            .bold(),
        " Mode".into(),
    ])
    .alignment(Alignment::Center);

    let x_labels: Vec<Span> = (1..=stats_data.len().max(1))
        .step_by((stats_data.len().max(1) / 10).max(1))
        .map(|i| Span::from(format!("{}", i)))
        .collect::<Vec<Span>>(); // Explicitly collect as Vec<Span>

    let chart = Chart::new(datasets)
        .block(Block::default().title(chart_title).borders(Borders::ALL))
        .x_axis(
            Axis::default()
                .title(Line::from("Game Number")) // Use Line::from for Axis titles
                .style(Style::default().fg(Color::Gray))
                .bounds(x_axis_bounds)
                .labels(x_labels), // Use the explicitly typed Vec<Span>
        )
        .y_axis(
            Axis::default()
                .title(Line::from("Score")) // Use Line::from for Axis titles
                .style(Style::default().fg(Color::Gray))
                .bounds(y_axis_bounds)
                .labels(
                    // labels expects Vec<Span>
                    (0..4)
                        .map(|i| {
                            let val = y_axis_bounds[0]
                                + (y_axis_bounds[1] - y_axis_bounds[0]) * (i as f64) / 3.0;
                            Span::from(format!("{:.0}", val))
                        })
                        .collect::<Vec<_>>(),
                ),
        );
    frame.render_widget(chart, chunks[0]);

    // Controls/Info
    let mut controls_spans = vec![
        "Press ".into(),
        "<Q>".blue().bold(),
        " to go back to Main Menu. ".into(),
    ];
    if stats_data.len() >= 5 {
        controls_spans.push("Press ".into());
        controls_spans.push("<R>".green().bold());
        controls_spans.push(
            format!(
                " to {} Rolling Average.",
                if model.stats_show_rolling_average {
                    "Hide"
                } else {
                    "Show"
                }
            )
            .into(),
        );
    }

    let controls_paragraph = Paragraph::new(Line::from(controls_spans))
        .alignment(Alignment::Center)
        .block(Block::default().borders(Borders::ALL).title("Controls"));
    frame.render_widget(controls_paragraph, chunks[1]);
}

fn draw_detailed_round_screen(model: &Model, frame: &mut Frame) {
    let area = frame.area();
    // Correctly access detailed_stats from model.game_state
    let detailed_stats = &model.game_state.detailed_round_stats;

    if detailed_stats.problems.is_empty() {
        let message = Paragraph::new(
            "No problems were attempted in this round, or detailed stats are not available.",
        )
        .alignment(Alignment::Center)
        .block(
            Block::default()
                .borders(Borders::ALL)
                .title("Detailed Round Stats"),
        );
        frame.render_widget(message, area);
        return;
    }

    // Main layout: 75% for chart, 25% for text stats
    let main_chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Percentage(65), Constraint::Percentage(35)].as_ref())
        .split(area);

    // Left chunk for the chart
    let chart_area = main_chunks[0];
    let mut problem_times_data: Vec<(f64, f64)> = Vec::new();
    let mut total_time_secs = 0.0;

    for (i, problem_stat) in detailed_stats.problems.iter().enumerate() {
        let time_secs = problem_stat.time_taken.as_secs_f64();
        problem_times_data.push(((i + 1) as f64, time_secs));
        total_time_secs += time_secs;
    }

    let average_time_secs = if !detailed_stats.problems.is_empty() {
        total_time_secs / detailed_stats.problems.len() as f64
    } else {
        0.0
    };

    let average_time_line_data: Vec<(f64, f64)> = if !problem_times_data.is_empty() {
        vec![
            (problem_times_data[0].0, average_time_secs),
            (problem_times_data.last().unwrap().0, average_time_secs),
        ]
    } else {
        vec![]
    };

    let max_time = problem_times_data
        .iter()
        .map(|&(_, y)| y)
        .fold(0.0 / 0.0, f64::max)
        .max(1.0); // Max y, at least 1.0
    let x_axis_bounds = [0.0, (detailed_stats.problems.len() + 1) as f64];
    let y_axis_bounds = [0.0, max_time];

    let datasets = vec![
        Dataset::default()
            .name("Problem Times")
            .marker(symbols::Marker::Dot)
            .graph_type(GraphType::Scatter)
            .style(Style::default().fg(Color::Cyan))
            .data(&problem_times_data),
        Dataset::default()
            .name("Average Time")
            .marker(symbols::Marker::Braille)
            .graph_type(GraphType::Line)
            .style(Style::default().fg(Color::Yellow))
            .data(&average_time_line_data),
    ];

    let chart = Chart::new(datasets)
        .block(
            Block::default()
                .title("Problem Completion Times".bold())
                .title_alignment(Alignment::Center)
                .borders(Borders::ALL),
        )
        .x_axis(
            Axis::default()
                .title("Problem Number")
                .style(Style::default().fg(Color::Gray))
                .bounds(x_axis_bounds)
                .labels(
                    problem_times_data
                        .iter()
                        .map(|(x, _)| Span::from(format!("{:.0}", x)))
                        .collect::<Vec<_>>(),
                ),
        )
        .y_axis(
            Axis::default()
                .title("Time (seconds)")
                .style(Style::default().fg(Color::Gray))
                .bounds(y_axis_bounds)
                .labels(
                    (0..=(max_time.ceil() as u32))
                        .step_by((max_time.ceil() / 10.0).max(1.0) as usize) // Adjust step for readability
                        .map(|t| Span::from(format!("{}", t)))
                        .collect::<Vec<_>>(),
                ),
        );
    frame.render_widget(chart, chart_area);

    // Right chunk for text stats, split vertically
    let right_chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([Constraint::Percentage(50), Constraint::Percentage(50)].as_ref())
        .split(main_chunks[1]);

    // Top-right for incorrect problems
    let incorrect_problems_area = right_chunks[0];
    let mut incorrect_items: Vec<ListItem> = Vec::new();
    if detailed_stats.input_mode == InputMode::EnterToSubmit {
        for stat in detailed_stats
            .problems
            .iter()
            .filter(|p| !p.is_correct && p.user_answer_if_incorrect.is_some())
        {
            incorrect_items.push(ListItem::new(Text::from(vec![
                Line::from(Span::styled(
                    format!("Problem: {}", stat.problem_text),
                    Style::default().fg(Color::White),
                )),
                Line::from(Span::styled(
                    format!(
                        "  Your Ans: {}",
                        stat.user_answer_if_incorrect
                            .as_ref()
                            .unwrap_or(&"".to_string())
                    ),
                    Style::default().fg(Color::Red),
                )),
                Line::from(Span::styled(
                    format!("  Correct Ans: {}", stat.correct_answer),
                    Style::default().fg(Color::Green),
                )),
            ])));
        }
    }
    if incorrect_items.is_empty() && detailed_stats.input_mode == InputMode::EnterToSubmit {
        incorrect_items.push(ListItem::new("No incorrect answers recorded!"));
    } else if detailed_stats.input_mode == InputMode::AutoSubmit {
        incorrect_items.push(ListItem::new("N/A"));
    }

    let incorrect_list = List::new(incorrect_items).block(
        Block::default()
            .borders(Borders::ALL)
            .title("Incorrect Answers".bold())
            .title_alignment(Alignment::Center),
    );
    frame.render_widget(incorrect_list, incorrect_problems_area);

    // Bottom-right for slow problems
    let slow_problems_area = right_chunks[1];
    let mut slow_items: Vec<ListItem> = Vec::new();
    if detailed_stats.problems.len() > 1 {
        // Need at least 2 data points for std dev
        let mean_time = average_time_secs;
        let variance = detailed_stats
            .problems
            .iter()
            .map(|p| {
                let diff = p.time_taken.as_secs_f64() - mean_time;
                diff * diff
            })
            .sum::<f64>()
            / detailed_stats.problems.len() as f64;
        let std_dev = variance.sqrt();
        let slow_threshold = mean_time + (1.0 * std_dev);

        slow_items.push(
            Line::from(format!(
                "Mean: {:.2}s, Slow threshold: {:.2}s",
                mean_time, slow_threshold
            ))
            .into(),
        );
        slow_items.push("".into());

        for stat in detailed_stats
            .problems
            .iter()
            .filter(|p| p.time_taken.as_secs_f64() > slow_threshold)
        {
            slow_items.push(ListItem::new(Text::from(vec![
                Line::from(Span::styled(
                    format!("Problem: {}", stat.problem_text),
                    Style::default().fg(Color::White),
                )),
                Line::from(Span::styled(
                    format!("  Time: {:.2}s", stat.time_taken.as_secs_f64()),
                    Style::default().fg(Color::Yellow),
                )),
            ])));
        }
    }
    if slow_items.len() <= 2 {
        slow_items.push(ListItem::new(
            "No problems significantly slower than average\n(or not enough data).",
        ));
    }

    let slow_list = List::new(slow_items).block(
        Block::default()
            .borders(Borders::ALL)
            .title("Slow Problems (> µ + σ)".bold())
            .title_alignment(Alignment::Center),
    );
    frame.render_widget(slow_list, slow_problems_area);

    // Footer for instructions
    let footer_area = Layout::default()
        .direction(Direction::Vertical)
        .constraints([Constraint::Min(0), Constraint::Length(1)].as_ref()) // Push to bottom
        .split(area)[1]; // Get the last chunk

    let footer_text =
        Paragraph::new("Press 'Q' or 'Esc' to return to Main Menu.").alignment(Alignment::Center);
    frame.render_widget(footer_text, footer_area);
}
