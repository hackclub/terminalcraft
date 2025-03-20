use crate::ui::{App, MenuState, WarningState};
use ratatui::{
    layout::{Alignment, Constraint, Direction, Layout, Rect},
    style::{Color, Modifier, Style},
    symbols,
    text::{Line, Span, Text},
    widgets::{Block, BorderType, Borders, Chart, Dataset, Gauge, Paragraph, Wrap},
    Frame,
};

pub fn render(app: &App, frame: &mut Frame) -> anyhow::Result<()> {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(3),
            Constraint::Min(5),
            Constraint::Length(7),
        ])
        .split(frame.size());

    draw_top_menu(app, frame, chunks[0]);

    if app.warning_state != WarningState::None {
        draw_warning(app, frame, chunks[1]);
    } else if app.menu_state == MenuState::TestComplete {
        draw_test_complete(app, frame, chunks[1]);
    } else if app.menu_state != MenuState::Typing {
        draw_menu(app, frame, chunks[1]);
    } else {
        draw_typing_area(app, frame, chunks[1]);
    }

    draw_stats(app, frame, chunks[2]);

    Ok(())
}

fn draw_top_menu(app: &App, frame: &mut Frame, area: Rect) {
    let title = format!(
        "TuiType{}",
        if app.config.repeat_test {
            " [Repeat Mode]"
        } else {
            ""
        }
    );

    // Format current settings to display at the top
    let test_mode_str = match app.config.test_mode {
        crate::config::TestMode::Timed(secs) => format!("Mode: Timed {}s", secs),
        crate::config::TestMode::Words(count) => format!("Mode: Words {}", count),
        crate::config::TestMode::Quote => "Mode: Quote".to_string(),
        crate::config::TestMode::Custom => "Mode: Custom".to_string(),
    };

    let diff_str = match app.config.difficulty {
        crate::config::Difficulty::Easy => "Difficulty: Easy",
        crate::config::Difficulty::Medium => "Difficulty: Medium",
        crate::config::Difficulty::Hard => "Difficulty: Hard",
        crate::config::Difficulty::Custom => "Difficulty: Custom",
    };

    let settings_info = format!(
        "{}  |  {}  |  End on Error: {}  |  Press ESC for menu",
        test_mode_str,
        diff_str,
        if app.config.end_on_first_error {
            "Yes"
        } else {
            "No"
        }
    );

    let paragraph = Paragraph::new(settings_info)
        .block(Block::default().borders(Borders::ALL).title(title))
        .style(Style::default().fg(Color::Rgb(
            app.theme.text.0,
            app.theme.text.1,
            app.theme.text.2,
        )))
        .alignment(Alignment::Center);

    frame.render_widget(paragraph, area);
}

fn draw_typing_area(app: &App, frame: &mut Frame, area: Rect) {
    let title = if let Some(remaining) = app.time_remaining {
        format!(
            "{}   |   Time: {}s   |   WPM: {:.1}   |   Accuracy: {:.1}%",
            crate::config::test_mode_name(app.config.test_mode),
            remaining,
            app.stats.wpm,
            app.stats.accuracy
        )
    } else {
        format!(
            "{}   |   WPM: {:.1}   |   Accuracy: {:.1}%",
            crate::config::test_mode_name(app.config.test_mode),
            app.stats.wpm,
            app.stats.accuracy
        )
    };

    let block = Block::default()
        .title(title)
        .borders(Borders::ALL)
        .border_type(BorderType::Rounded);

    let inner_area = block.inner(area);

    frame.render_widget(block, area);

    let target_text = app.text_source.full_text();
    let mut styled_spans = Vec::new();

    let correct_style = Style::default().fg(Color::Rgb(
        app.theme.correct.0,
        app.theme.correct.1,
        app.theme.correct.2,
    ));

    let incorrect_style = Style::default().fg(Color::Rgb(
        app.theme.incorrect.0,
        app.theme.incorrect.1,
        app.theme.incorrect.2,
    ));

    let pending_style = Style::default().fg(Color::Rgb(
        app.theme.pending.0,
        app.theme.pending.1,
        app.theme.pending.2,
    ));

    for (i, ch) in target_text.chars().enumerate() {
        let span = if i < app.typed_text.len() {
            let typed_char = app.typed_text.chars().nth(i).unwrap();
            if typed_char == ch {
                Span::styled(ch.to_string(), correct_style)
            } else {
                Span::styled(ch.to_string(), incorrect_style)
            }
        } else if i == app.cursor_pos {
            Span::styled(
                ch.to_string(),
                Style::default()
                    .fg(Color::Rgb(
                        app.theme.cursor.0,
                        app.theme.cursor.1,
                        app.theme.cursor.2,
                    ))
                    .add_modifier(Modifier::REVERSED),
            )
        } else {
            Span::styled(ch.to_string(), pending_style)
        };

        styled_spans.push(span);
    }

    if app.typed_text.len() > target_text.len() {
        for (i, ch) in app.typed_text.chars().skip(target_text.len()).enumerate() {
            let pos = target_text.len() + i;
            let span = if pos == app.cursor_pos {
                Span::styled(
                    ch.to_string(),
                    Style::default()
                        .fg(Color::Rgb(
                            app.theme.incorrect.0,
                            app.theme.incorrect.1,
                            app.theme.incorrect.2,
                        ))
                        .add_modifier(Modifier::REVERSED),
                )
            } else {
                Span::styled(ch.to_string(), incorrect_style)
            };
            styled_spans.push(span);
        }
    }

    if app.cursor_pos >= app.typed_text.len() && app.cursor_pos >= target_text.len() {
        styled_spans.push(Span::styled(
            " ",
            Style::default()
                .fg(Color::Rgb(
                    app.theme.cursor.0,
                    app.theme.cursor.1,
                    app.theme.cursor.2,
                ))
                .add_modifier(Modifier::REVERSED),
        ));
    }

    let text = Text::from(Line::from(styled_spans));
    let paragraph = Paragraph::new(text)
        .block(Block::default())
        .wrap(Wrap { trim: false });

    frame.render_widget(paragraph, inner_area);
}

fn draw_test_complete_new(app: &App, frame: &mut Frame, area: Rect) {
    let width = area.width.saturating_sub(4);
    let height = area.height.saturating_sub(2);

    let x = area.x + (area.width.saturating_sub(width)) / 2;
    let y = area.y + (area.height.saturating_sub(height)) / 2;

    let popup_area = Rect::new(x, y, width, height);

    let background = Block::default().style(Style::default().bg(Color::Black));
    frame.render_widget(background, popup_area);

    let block = Block::default()
        .borders(Borders::ALL)
        .border_style(Style::default().fg(Color::White))
        .title(" TEST COMPLETE ");

    frame.render_widget(block.clone(), popup_area);

    let duration = if let (Some(start), Some(end)) = (app.start_time, app.end_time) {
        end.duration_since(start).as_secs_f64()
    } else {
        0.0
    };

    let inner_area = block.inner(popup_area);
    let columns = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Percentage(50), Constraint::Percentage(50)])
        .split(inner_area);

    let mut results_lines = vec![
        Line::from(vec![Span::styled(
            "TEST RESULTS",
            Style::default().add_modifier(Modifier::BOLD),
        )]),
        Line::default(),
        Line::from(vec![
            Span::raw("WPM: "),
            Span::styled(
                format!("{:.1}", app.stats.wpm),
                Style::default().add_modifier(Modifier::BOLD),
            ),
        ]),
        Line::from(vec![
            Span::raw("Accuracy: "),
            Span::styled(
                format!("{:.1}%", app.stats.accuracy),
                Style::default().add_modifier(Modifier::BOLD),
            ),
        ]),
        Line::from(vec![
            Span::raw("Time: "),
            Span::styled(
                format!("{:.1}s", duration),
                Style::default().add_modifier(Modifier::BOLD),
            ),
        ]),
    ];

    if let Some(reason) = &app.test_end_reason {
        results_lines.push(Line::default());
        results_lines.push(Line::from(vec![
            Span::raw("Note: "),
            Span::styled(
                reason,
                Style::default().fg(Color::Red).add_modifier(Modifier::BOLD),
            ),
        ]));
    }

    let test_mode_str = match app.config.test_mode {
        crate::config::TestMode::Timed(secs) => format!("Timed - {}s", secs),
        crate::config::TestMode::Words(count) => format!("Words - {}", count),
        crate::config::TestMode::Quote => "Quote".to_string(),
        crate::config::TestMode::Custom => "Custom".to_string(),
    };

    let diff_str = match app.config.difficulty {
        crate::config::Difficulty::Easy => "Easy",
        crate::config::Difficulty::Medium => "Medium",
        crate::config::Difficulty::Hard => "Hard",
        crate::config::Difficulty::Custom => "Custom",
    };

    let settings_lines = vec![
        Line::from(vec![Span::styled(
            "TEST SETTINGS",
            Style::default().add_modifier(Modifier::BOLD),
        )]),
        Line::default(),
        Line::from(vec![
            Span::raw("Mode: "),
            Span::styled(
                &test_mode_str,
                Style::default().add_modifier(Modifier::BOLD),
            ),
        ]),
        Line::from(vec![
            Span::raw("Difficulty: "),
            Span::styled(diff_str, Style::default().add_modifier(Modifier::BOLD)),
        ]),
        Line::from(vec![
            Span::raw("Repeat Mode: "),
            Span::styled(
                if app.config.repeat_test { "ON" } else { "OFF" },
                Style::default().add_modifier(Modifier::BOLD),
            ),
        ]),
        Line::from(vec![
            Span::raw("End on First Error: "),
            Span::styled(
                if app.config.end_on_first_error {
                    "ON"
                } else {
                    "OFF"
                },
                Style::default().add_modifier(Modifier::BOLD),
            ),
        ]),
        Line::default(),
    ];

    let divider = Block::default()
        .borders(Borders::LEFT)
        .border_style(Style::default().fg(Color::White));
    frame.render_widget(divider, columns[1]);

    let total_height = inner_area.height;
    let content_height = results_lines.len().max(settings_lines.len()) as u16;
    let padding_top = if total_height > content_height {
        (total_height - content_height) / 2
    } else {
        0
    };

    let left_column = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(padding_top),
            Constraint::Min(content_height),
            Constraint::Min(1),
        ])
        .split(columns[0])[1];

    let right_column = Layout::default()
        .direction(Direction::Vertical)
        .constraints([
            Constraint::Length(padding_top),
            Constraint::Min(content_height),
            Constraint::Min(1),
        ])
        .split(columns[1])[1];

    let results_paragraph = Paragraph::new(results_lines)
        .alignment(Alignment::Center)
        .style(Style::default().fg(Color::White));
    frame.render_widget(results_paragraph, left_column);

    let settings_paragraph = Paragraph::new(settings_lines)
        .alignment(Alignment::Center)
        .style(Style::default().fg(Color::White));
    frame.render_widget(settings_paragraph, right_column);

    let footer_area = Rect::new(
        popup_area.x,
        popup_area.y + popup_area.height - 2,
        popup_area.width,
        2,
    );

    let footer_lines = vec![
        Line::default(),
        Line::from("Press ENTER to restart typing test").alignment(Alignment::Center),
    ];

    let footer = Paragraph::new(footer_lines)
        .alignment(Alignment::Center)
        .style(Style::default().fg(Color::White));

    frame.render_widget(footer, footer_area);
}

fn draw_stats(app: &App, frame: &mut Frame, area: Rect) {
    let chunks = Layout::default()
        .direction(Direction::Horizontal)
        .constraints([Constraint::Percentage(30), Constraint::Percentage(70)])
        .split(area);

    draw_gauges(app, frame, chunks[0]);

    draw_chart(app, frame, chunks[1]);
}

fn draw_gauges(app: &App, frame: &mut Frame, area: Rect) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([Constraint::Percentage(50), Constraint::Percentage(50)])
        .split(area);

    let accuracy_label = format!("Accuracy: {:.1}%", app.stats.accuracy);
    let accuracy_gauge = Gauge::default()
        .block(Block::default().borders(Borders::ALL).title("Accuracy"))
        .gauge_style(Style::default().fg(Color::Rgb(
            app.theme.correct.0,
            app.theme.correct.1,
            app.theme.correct.2,
        )))
        .percent((app.stats.accuracy as u16).min(100))
        .label(accuracy_label);
    frame.render_widget(accuracy_gauge, chunks[0]);

    // Calculate progress for the current test
    let progress = if app.text_source.full_text().is_empty() {
        0
    } else if app.text_source.is_scrollable {
        let total_words = app.text_source.total_words() as usize;
        if total_words == 0 {
            0
        } else {
            let typed_words = app.typed_text.split_whitespace().count();
            ((typed_words * 100) / total_words) as u16
        }
    } else {
        ((app.typed_text.len().min(app.text_source.full_text().len()) * 100)
            / app.text_source.full_text().len()) as u16
    };

    // Always display progress as a visible bar
    let progress_label = format!("Progress: {}%", progress);
    let progress_gauge = Gauge::default()
        .block(Block::default().borders(Borders::ALL).title("Progress"))
        .gauge_style(Style::default().fg(Color::Rgb(
            app.theme.pending.0,
            app.theme.pending.1,
            app.theme.pending.2,
        )))
        .percent(progress.clamp(0, 100))
        .label(progress_label);
    frame.render_widget(progress_gauge, chunks[1]);
}

fn draw_chart(app: &App, frame: &mut Frame, area: Rect) {
    let wpm_data: Vec<(f64, f64)> = app
        .stats
        .wpm_samples
        .iter()
        .enumerate()
        .map(|(i, &wpm)| (i as f64, wpm))
        .collect();

    let mut max_wpm = 20.0f64;
    for &wpm in &app.stats.wpm_samples {
        if wpm > max_wpm {
            max_wpm = wpm;
        }
    }
    max_wpm = max_wpm.max(20.0) * 1.2;

    let datasets = vec![Dataset::default()
        .name("WPM")
        .marker(symbols::Marker::Braille)
        .style(Style::default().fg(Color::Rgb(
            app.theme.accent.0,
            app.theme.accent.1,
            app.theme.accent.2,
        )))
        .data(&wpm_data)];

    let chart = Chart::new(datasets)
        .block(
            Block::default()
                .title("WPM Over Time")
                .borders(Borders::ALL),
        )
        .x_axis(
            ratatui::widgets::Axis::default()
                .title("Time")
                .style(Style::default().fg(Color::Rgb(
                    app.theme.text.0,
                    app.theme.text.1,
                    app.theme.text.2,
                )))
                .bounds([0.0, app.stats.wpm_samples.len() as f64])
                .labels(vec![
                    Span::raw("0"),
                    Span::raw(format!("{}", app.stats.wpm_samples.len())),
                ]),
        )
        .y_axis(
            ratatui::widgets::Axis::default()
                .title("WPM")
                .style(Style::default().fg(Color::Rgb(
                    app.theme.text.0,
                    app.theme.text.1,
                    app.theme.text.2,
                )))
                .bounds([0.0, max_wpm])
                .labels(vec![
                    Span::raw("0"),
                    Span::raw(format!("{:.0}", max_wpm / 2.0)),
                    Span::raw(format!("{:.0}", max_wpm)),
                ]),
        );

    frame.render_widget(chart, area);
}

fn draw_menu(app: &App, frame: &mut Frame, area: Rect) {
    let width = area.width.saturating_sub(4).min(area.width);
    let height = area.height.saturating_sub(2).min(area.height);
    let x = area.x + (area.width.saturating_sub(width)) / 2;
    let y = area.y + (area.height.saturating_sub(height)) / 2;
    let menu_area = Rect::new(x, y, width, height);

    let title = match app.menu_state {
        MenuState::MainMenu(_) => "MAIN MENU",
        MenuState::TestModeMenu(_) => "TEST MODE",
        MenuState::DifficultyMenu(_) => "DIFFICULTY",
        MenuState::TimeMenu(_) => "TIME LIMIT",
        MenuState::WordCountMenu(_) => "WORD COUNT",
        MenuState::ThemeMenu(_) => "THEME",
        MenuState::CustomTimedInput(_) => "CUSTOM TIMED TEST",
        MenuState::CustomWordsInput(_) => "CUSTOM WORDS TEST",
        MenuState::SettingsMenu(_) => "SETTINGS",
        MenuState::Help => "HELP",
        MenuState::TestComplete => "TEST COMPLETE",
        _ => "",
    };

    let outline = Block::default()
        .borders(Borders::ALL)
        .title(title)
        .border_style(Style::default().fg(Color::White));

    frame.render_widget(outline.clone(), menu_area);

    let inner_area = outline.inner(menu_area);

    let menu_text = match app.menu_state {
        MenuState::MainMenu(idx) => {
            let mut text = Vec::new();
            let items = vec![
                ("1. Test Mode", idx == 0),
                ("2. Difficulty", idx == 1),
                ("3. Theme", idx == 2),
                ("4. Settings", idx == 3),
                ("5. Help", idx == 4),
                ("6. Back", idx == 5),
            ];

            for (item, selected) in items {
                if selected {
                    text.push(Line::from(vec![Span::styled(
                        format!("> {} <", item),
                        Style::default().add_modifier(Modifier::REVERSED),
                    )]));
                } else {
                    text.push(Line::from(item));
                }
            }

            text
        }
        MenuState::TestModeMenu(idx) => {
            let items = [
                ("1. Timed", idx == 0),
                ("2. Words", idx == 1),
                ("3. Quote", idx == 2),
                ("4. Back", idx == 3),
            ];

            items
                .iter()
                .map(|(item, selected)| {
                    if *selected {
                        Line::from(vec![Span::styled(
                            format!("> {} <", item),
                            Style::default().add_modifier(Modifier::REVERSED),
                        )])
                    } else {
                        Line::from(*item)
                    }
                })
                .collect()
        }
        MenuState::DifficultyMenu(idx) => {
            let items = [
                ("1. Easy", idx == 0),
                ("2. Medium", idx == 1),
                ("3. Hard", idx == 2),
                ("4. Back", idx == 3),
            ];

            items
                .iter()
                .map(|(item, selected)| {
                    if *selected {
                        Line::from(vec![Span::styled(
                            format!("> {} <", item),
                            Style::default().add_modifier(Modifier::REVERSED),
                        )])
                    } else {
                        Line::from(*item)
                    }
                })
                .collect()
        }
        MenuState::TimeMenu(idx) => {
            let items = [
                ("1. 15 seconds", idx == 0),
                ("2. 30 seconds", idx == 1),
                ("3. 60 seconds", idx == 2),
                ("4. 120 seconds", idx == 3),
                ("5. Custom...", idx == 4),
                ("6. Back", idx == 5),
            ];

            items
                .iter()
                .map(|(item, selected)| {
                    if *selected {
                        Line::from(vec![Span::styled(
                            format!("> {} <", item),
                            Style::default().add_modifier(Modifier::REVERSED),
                        )])
                    } else {
                        Line::from(*item)
                    }
                })
                .collect()
        }
        MenuState::WordCountMenu(idx) => {
            let items = [
                ("1. 10 words", idx == 0),
                ("2. 25 words", idx == 1),
                ("3. 50 words", idx == 2),
                ("4. Custom...", idx == 3),
                ("5. Back", idx == 4),
            ];

            items
                .iter()
                .map(|(item, selected)| {
                    if *selected {
                        Line::from(vec![Span::styled(
                            format!("> {} <", item),
                            Style::default().add_modifier(Modifier::REVERSED),
                        )])
                    } else {
                        Line::from(*item)
                    }
                })
                .collect()
        }
        MenuState::ThemeMenu(idx) => {
            let items = [
                ("1. Light", idx == 0),
                ("2. Dark", idx == 1),
                ("3. Sepia", idx == 2),
                ("4. Matrix", idx == 3),
                ("5. Ocean", idx == 4),
                ("6. Back", idx == 5),
            ];

            items
                .iter()
                .map(|(item, selected)| {
                    if *selected {
                        Line::from(vec![Span::styled(
                            format!("> {} <", item),
                            Style::default().add_modifier(Modifier::REVERSED),
                        )])
                    } else {
                        Line::from(*item)
                    }
                })
                .collect()
        }
        MenuState::SettingsMenu(idx) => {
            let items = [
                ("1. Toggle Repeat Mode", idx == 0),
                ("2. Toggle End on First Error", idx == 1),
                ("3. Back", idx == 2),
            ];
            vec![
                if items[0].1 {
                    Line::from(vec![Span::styled(
                        format!("> {} <", items[0].0),
                        Style::default().add_modifier(Modifier::REVERSED),
                    )])
                } else {
                    Line::from(items[0].0)
                },
                Line::default(),
                Line::from(format!(
                    "Current: {}",
                    if app.config.repeat_test { "ON" } else { "OFF" }
                )),
                Line::default(),
                if items[1].1 {
                    Line::from(vec![Span::styled(
                        format!("> {} <", items[1].0),
                        Style::default().add_modifier(Modifier::REVERSED),
                    )])
                } else {
                    Line::from(items[1].0)
                },
                Line::default(),
                Line::from(format!(
                    "Current: {}",
                    if app.config.end_on_first_error {
                        "ON"
                    } else {
                        "OFF"
                    }
                )),
                Line::default(),
                if items[2].1 {
                    Line::from(vec![Span::styled(
                        format!("> {} <", items[2].0),
                        Style::default().add_modifier(Modifier::REVERSED),
                    )])
                } else {
                    Line::from(items[2].0)
                },
            ]
        }

        MenuState::CustomTimedInput(ref input) => {
            vec![
                Line::from(Span::styled(
                    "ENTER CUSTOM TIME (SECONDS):",
                    Style::default().add_modifier(Modifier::BOLD),
                )),
                Line::default(),
                Line::from(if input.is_empty() {
                    vec![Span::styled(
                        "▋",
                        Style::default().add_modifier(Modifier::SLOW_BLINK),
                    )]
                } else {
                    vec![Span::styled(
                        format!("{} ▋", input),
                        Style::default().add_modifier(Modifier::BOLD),
                    )]
                }),
                Line::default(),
                Line::from("Press ENTER to confirm"),
            ]
        }

        MenuState::CustomWordsInput(ref input) => {
            vec![
                Line::from(Span::styled(
                    "ENTER CUSTOM WORD COUNT:",
                    Style::default().add_modifier(Modifier::BOLD),
                )),
                Line::default(),
                Line::from(if input.is_empty() {
                    vec![Span::styled(
                        "▋",
                        Style::default().add_modifier(Modifier::SLOW_BLINK),
                    )]
                } else {
                    vec![Span::styled(
                        format!("{} ▋", input),
                        Style::default().add_modifier(Modifier::BOLD),
                    )]
                }),
                Line::default(),
                Line::from("Press ENTER to confirm"),
            ]
        }
        MenuState::Help => {
            vec![
                Line::from("KEYBOARD CONTROLS:"),
                Line::from("Esc: Open/close menu or restart"),
                Line::from("Tab: Restart test"),
                Line::from("Ctrl+C: Exit"),
                Line::default(),
                Line::from("TEST MODES:"),
                Line::from("Timed: Type as many words as possible"),
                Line::from("Words: Type a specific number of words"),
                Line::from("Quote: Type a random quote"),
            ]
        }
        MenuState::TestComplete => {
            let duration = if let (Some(start), Some(end)) = (app.start_time, app.end_time) {
                end.duration_since(start).as_secs_f64()
            } else {
                0.0
            };

            let mut lines = vec![
                Line::from(Span::styled(
                    "TEST RESULTS",
                    Style::default().add_modifier(Modifier::BOLD),
                )),
                Line::default(),
                Line::from(format!("WPM: {:.1}", app.stats.wpm)),
                Line::from(format!("Accuracy: {:.1}%", app.stats.accuracy)),
                Line::from(format!("Time: {:.1} seconds", duration)),
            ];

            if let Some(reason) = &app.test_end_reason {
                lines.push(Line::default());
                lines.push(Line::from(Span::styled(
                    reason,
                    Style::default().fg(Color::Red).add_modifier(Modifier::BOLD),
                )));
            }

            lines.push(Line::default());
            lines.push(Line::from("Press ENTER to restart test"));
            lines.push(Line::from("Press ESC to return to menu"));

            lines
        }

        _ => vec![Line::from("Press ESC to return to typing")],
    };

    let mut full_text = menu_text;

    if app.menu_state != MenuState::Help {
        full_text.push(Line::default());
        full_text.push(Line::from("UP/DOWN: Navigate    ENTER: Select"));
        full_text.push(Line::from("ESC: Return to typing test"));
    } else {
        full_text.push(Line::default());
        full_text.push(Line::from("Press ESC to return"));
    }

    let menu_paragraph = Paragraph::new(full_text)
        .alignment(Alignment::Center)
        .style(Style::default().fg(Color::White));

    frame.render_widget(menu_paragraph, inner_area);
}

fn draw_test_complete(app: &App, frame: &mut Frame, area: Rect) {
    draw_test_complete_new(app, frame, area);
}

fn draw_warning(app: &App, frame: &mut Frame, area: Rect) {
    let (action, _prev_state) = match &app.warning_state {
        WarningState::RepeatModeSettings { action, prev_state } => (action, prev_state),
        _ => return,
    };

    let width = area.width.saturating_sub(10).min(80).max(50);
    let height = 10.min(area.height.saturating_sub(4));

    let x = area.x + (area.width.saturating_sub(width)) / 2;
    let y = area.y + (area.height.saturating_sub(height)) / 2;

    let popup_area = Rect::new(x, y, width, height);

    let background = Block::default().style(Style::default().bg(Color::Black));
    frame.render_widget(background, popup_area);

    let block = Block::default()
        .borders(Borders::ALL)
        .border_style(Style::default().fg(Color::Red))
        .title(" REPEAT MODE WARNING ");

    frame.render_widget(block.clone(), popup_area);

    let inner_area = block.inner(popup_area);

    let message_lines = vec![
        Line::from(vec![Span::styled(
            "SETTINGS CHANGE RESTRICTED",
            Style::default().fg(Color::Red).add_modifier(Modifier::BOLD),
        )]),
        Line::default(),
        Line::from(action.as_str()),
        Line::default(),
        Line::from("Changing settings during Repeat Mode would affect test consistency."),
        Line::default(),
        Line::from(vec![
            Span::styled(
                "ENTER",
                Style::default()
                    .fg(Color::Green)
                    .add_modifier(Modifier::BOLD),
            ),
            Span::raw(": Disable Repeat Mode and continue"),
        ]),
        Line::from(vec![
            Span::styled(
                "ESC",
                Style::default()
                    .fg(Color::Yellow)
                    .add_modifier(Modifier::BOLD),
            ),
            Span::raw(": Cancel and return to previous menu"),
        ]),
    ];

    let warning_paragraph = Paragraph::new(message_lines)
        .alignment(Alignment::Center)
        .style(Style::default().fg(Color::White));

    frame.render_widget(warning_paragraph, inner_area);
}
