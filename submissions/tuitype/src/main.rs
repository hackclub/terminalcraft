use anyhow::Result;
use crossterm::{
    event::{DisableMouseCapture, EnableMouseCapture},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{backend::CrosstermBackend, Terminal};
use std::{
    io::{self},
    time::Duration,
};
use tuitype::{
    config::Config,
    input::{Event, InputHandler},
    ui::{render, App},
    AppResult,
};

fn main() -> Result<()> {
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen, EnableMouseCapture)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    let config = Config::load().unwrap_or_default();

    let app = App::new(config);
    let mut input_handler = InputHandler::new(Duration::from_millis(33));

    let res = run_app(&mut terminal, app, &mut input_handler);

    terminal.show_cursor()?;
    let backend = terminal.backend_mut();
    disable_raw_mode()?;
    execute!(backend, LeaveAlternateScreen, DisableMouseCapture)?;

    if let Err(err) = res {
        println!("Error: {:?}", err)
    }

    Ok(())
}

fn run_app<B: ratatui::backend::Backend>(
    terminal: &mut Terminal<B>,
    mut app: App,
    input_handler: &mut InputHandler,
) -> AppResult<()> {
    while app.running {
        terminal.draw(|f| render(&app, f).expect("Failed to render UI"))?;

        match input_handler.poll_event()? {
            Some(Event::Key(key)) => app.handle_events(Event::Key(key))?,
            Some(Event::Mouse(mouse)) => app.handle_events(Event::Mouse(mouse))?,
            Some(Event::Resize(w, h)) => app.handle_events(Event::Resize(w, h))?,
            Some(Event::Tick) => app.tick()?,
            None => {
                std::thread::sleep(Duration::from_millis(1));
            }
        }
    }

    Ok(())
}
