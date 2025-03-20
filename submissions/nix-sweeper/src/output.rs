use std::io::{self, Write};

use crossterm::{
    Command, cursor,
    style::Print,
    terminal::{self, disable_raw_mode, enable_raw_mode},
};

pub fn switch_terminal_mode(stdout: &mut impl Write, raw: bool) -> io::Result<()> {
    if let Err(error) = {
        if raw {
            enable_raw_mode()
        } else {
            disable_raw_mode()
        }
    } {
        return Err(io::Error::new(
            error.kind(),
            format!("Could not set terminal mode: {}", error),
        ));
    }
    if let Err(error) = {
        if raw {
            crossterm::execute!(stdout, terminal::EnterAlternateScreen)
        } else {
            crossterm::execute!(stdout, terminal::LeaveAlternateScreen)
        }
    } {
        return Err(io::Error::new(
            error.kind(),
            format!("Could not switch to alternate screen: {}", error),
        ));
    }

    if let Err(error) = {
        if raw {
            crossterm::execute!(stdout, cursor::Hide)
        } else {
            crossterm::execute!(stdout, cursor::Show)
        }
    } {
        return Err(io::Error::new(
            error.kind(),
            format!("Could not set sursor visibility: {}", error),
        ));
    }

    Ok(())
}

pub fn print_formatted(text: &str) -> impl Command {
    return Print(text.replace("\n", "\r\n"));
}

pub fn redraw_screen(stdout: &mut impl Write, screen: &str) -> io::Result<()> {
    crossterm::execute!(
        stdout,
        cursor::MoveTo(0, 0),
        terminal::Clear(terminal::ClearType::All),
        terminal::Clear(terminal::ClearType::Purge),
        print_formatted(screen)
    )
}
