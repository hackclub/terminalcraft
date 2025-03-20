use std::{
    io::{self, Write, stdout},
    process::ExitCode,
    time::Duration,
};

use crossterm::event::{self, Event, KeyCode, KeyModifiers};
use ffi::Action;
use output::{redraw_screen, switch_terminal_mode};

mod ffi;
mod output;
mod random;

fn event_loop(stdout: &mut impl Write) -> io::Result<()> {
    let mut state = ffi::initial(10, 10, 12)?;

    redraw_screen(stdout, &ffi::output(&state)?)?;

    loop {
        let mut last_event: Option<Event> = None;

        // Clear out old events to not overwhelm the nix evaluator
        while event::poll(Duration::ZERO)? {
            last_event = Some(event::read()?);
        }

        // Wait for a new event if none happened while nix was evaluating
        let last_event = if let Some(last_event) = last_event {
            last_event
        } else {
            event::read()?
        };

        let action = match last_event {
            event::Event::Key(key_event) => match key_event.code {
                KeyCode::Char('c') if matches!(key_event.modifiers, KeyModifiers::CONTROL) => break,
                KeyCode::Char('q') => break,
                KeyCode::Char('r') => {
                    state = ffi::initial(10, 10, 12)?;
                    redraw_screen(stdout, &ffi::output(&state)?)?;
                    continue;
                }

                KeyCode::Up | KeyCode::Char('w') => Some(Action::Up),
                KeyCode::Down | KeyCode::Char('s') => Some(Action::Down),
                KeyCode::Left | KeyCode::Char('a') => Some(Action::Left),
                KeyCode::Right | KeyCode::Char('d') => Some(Action::Right),

                KeyCode::Char('f') => Some(Action::Flag),
                KeyCode::Enter | KeyCode::Char(' ') => Some(Action::Expose),

                _ => None,
            },
            _ => None,
        };

        if let Some(action) = action {
            state = ffi::update(action, &state)?;
            redraw_screen(stdout, &ffi::output(&state)?)?;
        }
    }

    Ok(())
}

fn main() -> ExitCode {
    let mut stdout = stdout();
    let mut program_error = None;

    'pre_cleanup: {
        if let Err(error) = switch_terminal_mode(&mut stdout, true) {
            program_error.get_or_insert(error);
            break 'pre_cleanup;
        }

        if let Err(error) = event_loop(&mut stdout) {
            program_error.get_or_insert(error);
            break 'pre_cleanup;
        }
    }

    // Always make sure to clean up the terminal if possible
    if let Err(error) = switch_terminal_mode(&mut stdout, false) {
        program_error.get_or_insert(error);
    }

    if let Some(error) = program_error {
        eprintln!("{}", error.to_string().trim_end());

        ExitCode::FAILURE
    } else {
        ExitCode::SUCCESS
    }
}
