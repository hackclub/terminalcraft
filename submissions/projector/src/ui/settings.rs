use crate::state::app::App;
use ratatui::style::{Color, Style};
use ratatui::{
    crossterm::event::{self, Event as CrosstermEvent, KeyCode, KeyEventKind},
    layout::{Constraint, Layout},
    text::{Line, Span},
    widgets::{Block, List, ListItem, ListState, Paragraph},
    DefaultTerminal, Frame,
};

pub fn show() -> color_eyre::Result<()> {
    let terminal = ratatui::init();
    let mut app = App::new();
    app.load_settings()?;
    let result = run(terminal, &mut app);
    ratatui::restore();
    result
}

fn run(mut terminal: DefaultTerminal, app: &mut App) -> color_eyre::Result<()> {
    loop {
        terminal.draw(|frame| render(frame, app))?;
        if let CrosstermEvent::Key(key_event) = event::read()? {
            if key_event.kind == KeyEventKind::Press {
                match key_event.code {
                    KeyCode::Esc => break Ok(()),
                    KeyCode::Char('q') => break Ok(()),
                    KeyCode::Up => app.prev_setting(),
                    KeyCode::Down => app.next_setting(),
                    KeyCode::Left => app.prev_option(),
                    KeyCode::Right => app.next_option(),
                    KeyCode::Enter => {
                        app.save_settings()?;
                        break Ok(());
                    }
                    _ => {}
                }
            }
        }
    }
}

fn render(frame: &mut Frame, app: &App) {
    let vertical = Layout::vertical([
        Constraint::Length(1),
        Constraint::Fill(1),
        Constraint::Length(1),
    ])
    .split(frame.area());

    let header = Paragraph::new(Line::from("Projector - Settings"))
        .block(Block::default())
        .style(Style::default().fg(Color::LightBlue))
        .centered();
    frame.render_widget(header, vertical[0]);

    let settings: Vec<ListItem> = app
        .settings
        .iter()
        .map(|setting| {
            let content = Line::from(Span::from(format!(
                "{}: {:?}",
                setting.name,
                setting.value()
            )));
            ListItem::new(content)
        })
        .collect();

    let mut state = ListState::default();
    state.select(Some(app.selected_setting_index));

    let settings_list = List::new(settings)
        .block(
            Block::default()
                .borders(ratatui::widgets::Borders::ALL)
                .title(Span::styled(
                    "Settings",
                    Style::default().fg(Color::Magenta),
                )),
        )
        .highlight_style(Style::default().fg(Color::LightMagenta))
        .highlight_symbol(">> ");

    frame.render_stateful_widget(settings_list, vertical[1], &mut state);

    let footer = Paragraph::new(Line::from(Span::from(
        "Use Up/Down to navigate, Left/Right to change, Enter to save, Esc or Q to exit",
    )));
    frame.render_widget(footer, vertical[2]);
}
