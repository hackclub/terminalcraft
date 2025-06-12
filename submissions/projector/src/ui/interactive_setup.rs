use crate::scaffold;
use crate::state::app::App;
use crate::state::languages::ProgrammingLanguage;
use crate::ui::not_implemented_warning;
use ratatui::style::{Color, Style};
use ratatui::{
    crossterm::event::{self, Event as CrosstermEvent, KeyCode, KeyEventKind},
    layout::{Constraint, Layout},
    text::{Line, Span},
    widgets::{Block, BorderType, List, ListItem, ListState, Paragraph},
    DefaultTerminal, Frame,
};

/// Show the interactive setup screen
pub fn show() -> color_eyre::Result<()> {
    blank()?;

    let terminal = ratatui::init();
    let mut app = App::new();
    let result = run(terminal, &mut app);
    ratatui::restore();
    if let Some(lang) = app.selected_lang {
        match lang {
            ProgrammingLanguage::Rust => {
                println!("Rust selected. Setting up Rust environment...");
                scaffold::rust::setup(None);
            }
            ProgrammingLanguage::C => {
                println!("C selected. Setting up C environment...");
                scaffold::c::setup(None);
            }
            ProgrammingLanguage::Python => {
                println!("Python selected. Setting up Python environment...");
                scaffold::python::setup(None);
            }
            _ => {
                not_implemented_warning::show(format!(
                    "Scaffolding for language '{:?}' is not implemented yet.",
                    lang
                ))?;
            }
        }
    }
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
                    KeyCode::Up => app.prev_item(),
                    KeyCode::Down => app.next_item(),
                    KeyCode::Enter => {
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

    let header = Paragraph::new(Line::from("Projector - Interactive Setup"))
        .block(Block::default())
        .style(Style::default().fg(Color::LightBlue))
        .centered();
    frame.render_widget(header, vertical[0]);

    let message_paragraph = Paragraph::new(Line::from("Setup"))
        .block(Block::bordered().border_type(BorderType::Rounded));
    frame.render_widget(message_paragraph, vertical[1]);

    let languages: Vec<ListItem> = ProgrammingLanguage::all_langs()
        .iter()
        .map(|lang| {
            let content = Line::from(Span::from(format!("{:?}", lang)));
            ListItem::new(content)
        })
        .collect();

    let mut state = ListState::default();
    state.select(Some(app.selected_lang_index));

    let languages_list = List::new(languages)
        .block(
            Block::default()
                .borders(ratatui::widgets::Borders::ALL)
                .title(Span::styled(
                    "Languages",
                    Style::default().fg(Color::Magenta),
                )),
        )
        .highlight_style(Style::default().fg(Color::LightMagenta))
        .highlight_symbol(">> ");

    frame.render_stateful_widget(languages_list, vertical[1], &mut state);

    let footer = Paragraph::new(Line::from(Span::from(
        "Use Up/Down to navigate, Esc or Q to exit",
    )));
    frame.render_widget(footer, vertical[2]);
}

/// Blank the screen
fn blank() -> color_eyre::Result<()> {
    ratatui::init();
    ratatui::restore();
    Ok(())
}
