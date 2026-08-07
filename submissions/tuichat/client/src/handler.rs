use crate::app::{App, AppResult};
use crossterm::event::{KeyCode, KeyEvent, KeyModifiers};

pub fn handle_key_events(
    key_event: KeyEvent,
    app: &mut App,
    tx: &tokio::sync::mpsc::Sender<String>,
) -> AppResult<()> {
    match key_event.code {
        KeyCode::Esc => {
            app.quit();
        }
        
        // So we can exit on ctrl c
        KeyCode::Char('c') | KeyCode::Char('C') => {
            if key_event.modifiers == KeyModifiers::CONTROL {
                app.quit();
            } else {
                app.add_char('c');
            }
        }
        KeyCode::Enter => {
            let message = app.input.clone();
            app.clear_input();
            tx.try_send(message)?;
        }
        KeyCode::Char(c) => {
            app.add_char(c);
        }
        KeyCode::Backspace => {
            app.remove_char();
        }
        KeyCode::Right => {
            app.cursor_right();
        }
        KeyCode::Left => {
            app.cursor_left();
        }
        _ => {}
    }
    Ok(())
}
