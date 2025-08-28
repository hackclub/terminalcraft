// KNOWN MAJOR BUGS (FIXME)
// - When "auto"-scrolling, a new, empty line appears at the bottom.
//   eventually, the screen is blank from these new lines appearing.

use ratatui::{
    layout::{Constraint, Direction, Layout},
    style::{Color, Style},
    widgets::{Block, BorderType, Paragraph},
    text::{Span, Line, Text},
    Frame,
};

use crate::app::App;

pub fn render(app: &mut App, frame: &mut Frame) {
    let chunks = Layout::default()
        .direction(Direction::Vertical)
        .constraints([Constraint::Min(1), Constraint::Length(3)].as_ref())
        .split(frame.area());

    let messages_height = chunks[0].height.saturating_sub(2) as usize; // Borders

    let mut message_lines: Vec<Line> = Vec::new();

    // This is needed to split by lines if a message contains \n
    for message in &app.messages {
        for line in message.lines() {
            message_lines.push(Line::from(Span::raw(line.to_string())));
        }
    }

    let total_lines = message_lines.len();
    let mut start_index = 0;

    if total_lines > messages_height {
        start_index = total_lines - messages_height;
    }

    let visible_messages = Text::from(message_lines[start_index..].to_vec());

    let mut scroll_offset = 0;
    if total_lines > messages_height {
        scroll_offset = (total_lines - messages_height) as u16
    }

    let messages_widget = Paragraph::new(visible_messages)
        .block(
            Block::default()
                .title("Messages")
                .border_type(BorderType::Rounded)
                .borders(ratatui::widgets::Borders::ALL),
        )
        .style(Style::default().fg(Color::White).bg(Color::Black))
        .scroll((scroll_offset, 0));

    let input_widget = Paragraph::new(app.input.as_str())
        .block(
            Block::default()
                .title("Input")
                .border_type(BorderType::Rounded)
                .borders(ratatui::widgets::Borders::ALL),
        )
        .style(Style::default().fg(Color::Gray).bg(Color::Black));

    frame.render_widget(messages_widget, chunks[0]);
    frame.render_widget(input_widget, chunks[1]);
}
