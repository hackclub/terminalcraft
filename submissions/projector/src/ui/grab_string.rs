use ratatui::style::{Color, Style};
use ratatui::text::{Line, Span};
use ratatui::widgets::{Block, BorderType, Paragraph};
use ratatui::{
    crossterm::event::{self, Event as CrosstermEvent, KeyCode, KeyEventKind},
    layout::{Constraint, Layout},
    DefaultTerminal, Frame,
};

pub fn ask(question: &str) -> color_eyre::Result<String> {
    let terminal = ratatui::init();
    let mut input = String::new();
    let result = run(terminal, question, &mut input);
    ratatui::restore();
    result?;
    Ok(input.trim().to_string())
}

fn run(
    mut terminal: DefaultTerminal,
    question: &str,
    input: &mut String,
) -> color_eyre::Result<()> {
    loop {
        terminal.draw(|frame| render(frame, question, input))?;
        if let CrosstermEvent::Key(key_event) = event::read()? {
            if key_event.kind == KeyEventKind::Press {
                match key_event.code {
                    KeyCode::Esc => break Ok(()),
                    KeyCode::Char('q') => break Ok(()),
                    KeyCode::Enter => break Ok(()),
                    KeyCode::Char(c) => input.push(c),
                    KeyCode::Backspace => {
                        input.pop();
                    }
                    _ => {}
                }
            }
        }
    }
}

fn render(frame: &mut Frame, question: &str, input: &str) {
    let vertical = Layout::vertical([
        Constraint::Length(3), // Adjusted to make the first box smaller
        Constraint::Min(1),    // Ensures the second box fits
        Constraint::Length(3), // Adjusted to make the third box smaller
    ])
    .split(frame.area());

    let header = Paragraph::new(Line::from("Projector - Input Prompt"))
        .block(Block::default())
        .style(Style::default().fg(Color::LightBlue))
        .centered();
    frame.render_widget(header, vertical[0]);

    let question_paragraph = Paragraph::new(Line::from(question))
        .block(Block::bordered().border_type(BorderType::Rounded));
    frame.render_widget(question_paragraph, vertical[1]);

    let input_paragraph = Paragraph::new(Line::from(Span::from(input)))
        .block(Block::bordered().border_type(BorderType::Rounded));
    frame.render_widget(input_paragraph, vertical[2]);
}
