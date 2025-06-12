use ratatui::style::{Color, Style};
use ratatui::{
    crossterm::event::{self, Event, KeyCode},
    layout::{Constraint, Layout},
    text::{Line, Span},
    widgets::{Block, BorderType, Paragraph},
    DefaultTerminal, Frame,
};

/// Show a not implemented warning message in a terminal UI.
pub fn show(message: String) -> color_eyre::Result<()> {
    color_eyre::install()?;
    let terminal = ratatui::init();
    let result = run(terminal, message);
    ratatui::restore();
    result
}

fn run(mut terminal: DefaultTerminal, message: String) -> color_eyre::Result<()> {
    loop {
        terminal.draw(|frame| render(frame, &message))?;
        if let Event::Key(key_event) = event::read()? {
            if key_event.code == KeyCode::Esc {
                break Ok(());
            }
        }
    }
}

fn render(frame: &mut Frame, message: &str) {
    let vertical = Layout::vertical([
        Constraint::Length(1),
        Constraint::Fill(1),
        Constraint::Length(1),
    ])
    .split(frame.area());

    let message_paragraph = Paragraph::new(Line::from(message)).block(
        Block::bordered()
            .title(Span::styled(
                "Not Implemented",
                Style::default().fg(Color::Red),
            ))
            .border_type(BorderType::Rounded),
    );
    frame.render_widget(message_paragraph, vertical[1]);

    let footer = Paragraph::new(Line::from(Span::from("Press escape to exit")));
    frame.render_widget(footer, vertical[2]);
}
