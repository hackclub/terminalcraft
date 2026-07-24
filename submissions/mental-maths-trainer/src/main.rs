use color_eyre::{eyre::Ok, Result};
use crossterm::event::{self, Event, KeyCode, KeyEvent, KeyEventKind};
use ratatui::DefaultTerminal;
use std::time::{Duration, Instant};

mod app;
mod config;
mod game;
mod stats;
mod ui;

use app::{Model, Msg, Screen};
use game::Operation;

fn main() -> Result<()> {
    color_eyre::install()?;
    let mut terminal = ratatui::init();
    let mut model = Model::new();
    let result = run_app(&mut terminal, &mut model);
    ratatui::restore();
    result
}

/// Runs the application's main loop until the user quits.
fn run_app(terminal: &mut DefaultTerminal, model: &mut Model) -> Result<()> {
    let mut next_tick_target = Instant::now() + Duration::from_millis(100);

    while !model.exit {
        terminal.draw(|frame| ui::view(model, frame))?;

        let now = Instant::now();
        let time_until_next_tick = if now >= next_tick_target {
            Duration::ZERO
        } else {
            next_tick_target - now
        };

        if event::poll(time_until_next_tick)? {
            match event::read()? {
                Event::Key(key_event) if key_event.kind == KeyEventKind::Press => {
                    handle_key_event_input(model, key_event);
                }
                _ => {}
            }
        }

        if Instant::now() >= next_tick_target {
            app::update(model, Msg::TimerTick);
            next_tick_target += Duration::from_millis(100);
        }
    }
    Ok(())
}

// Translates crossterm key events to app Msgs and calls app::update.
fn handle_key_event_input(model: &mut Model, key_event: KeyEvent) {
    let msg = match model.current_screen {
        Screen::MainMenu => match key_event.code {
            KeyCode::Char('q') | KeyCode::Char('Q') | KeyCode::Esc => Msg::Quit,
            KeyCode::Char('p') | KeyCode::Char('P') => Msg::SwitchScreen(Screen::ProblemScreen),
            KeyCode::Char('s') | KeyCode::Char('S') => Msg::SwitchScreen(Screen::SettingsScreen),
            KeyCode::Char('t') | KeyCode::Char('T') => Msg::SwitchScreen(Screen::StatsScreen),
            _ => return,
        },
        Screen::ProblemScreen => match key_event.code {
            KeyCode::Char('q') | KeyCode::Char('Q') | KeyCode::Esc => {
                Msg::SwitchScreen(Screen::MainMenu)
            }
            KeyCode::Char('t') | KeyCode::Char('T') => {
                Msg::SwitchScreen(Screen::DetailedRoundScreen)
            }
            KeyCode::Backspace => Msg::Backspace,
            KeyCode::Enter => Msg::SubmitAnswer,
            KeyCode::Char(c)
                if c.is_ascii_digit() || (c == '-' && model.game_state.user_input.is_empty()) =>
            {
                Msg::KeyPress(c)
            }
            _ => return,
        },
        Screen::SettingsScreen => match key_event.code {
            KeyCode::Char('q') | KeyCode::Char('Q') | KeyCode::Esc => {
                Msg::SwitchScreen(Screen::MainMenu)
            }
            KeyCode::Up => Msg::IncrementMaxVal,
            KeyCode::Down => Msg::DecrementMaxVal,
            KeyCode::Left => Msg::DecrementMinVal,
            KeyCode::Right => Msg::IncrementMinVal,
            KeyCode::Char('1') => Msg::ToggleOperator(Operation::Add),
            KeyCode::Char('2') => Msg::ToggleOperator(Operation::Subtract),
            KeyCode::Char('3') => Msg::ToggleOperator(Operation::Multiply),
            KeyCode::Char('4') => Msg::ToggleOperator(Operation::Divide),
            KeyCode::Char('i') | KeyCode::Char('I') => Msg::ToggleInputMode,
            KeyCode::Char('t') | KeyCode::Char('T') => Msg::ToggleTimedMode,
            KeyCode::Char('[') => Msg::DecrementOperatorCount,
            KeyCode::Char(']') => Msg::IncrementOperatorCount,
            _ => return,
        },
        Screen::StatsScreen => match key_event.code {
            KeyCode::Esc | KeyCode::Char('q') | KeyCode::Char('Q') => {
                Msg::SwitchScreen(Screen::MainMenu)
            }
            KeyCode::Char('t') | KeyCode::Char('T') => Msg::ToggleTimedMode,
            KeyCode::Char('r') | KeyCode::Char('R') => Msg::ToggleChartType,
            _ => return,
        },
        Screen::DetailedRoundScreen => match key_event.code {
            KeyCode::Esc | KeyCode::Char('q') | KeyCode::Char('Q') => {
                Msg::SwitchScreen(Screen::MainMenu)
            }
            _ => return,
        },
    };
    app::update(model, msg);
}
