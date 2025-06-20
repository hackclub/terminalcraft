use crate::database::manage::{get_all_projects, setup_database};
use crate::database::model::Project;
use crate::post_setup;
use ratatui::style::{Color, Style};
use ratatui::{
    crossterm::event::{self, Event as CrosstermEvent, KeyCode, KeyEventKind},
    layout::{Constraint, Layout},
    text::{Line, Span},
    widgets::{Block, List, ListItem, ListState, Paragraph},
    DefaultTerminal, Frame,
};
use std::io::{self};

use super::yn;

#[derive(Debug, Default, serde::Serialize, serde::Deserialize)]
struct Config {
    editor: String,
}

/// Show the interactive setup screen
pub fn show() -> color_eyre::Result<()> {
    blank()?;

    let terminal = ratatui::init();
    let conn = setup_database()?;
    let projects = get_all_projects(&conn)?;
    let result = run(terminal, &conn, &projects);
    ratatui::restore();
    result
}

fn run(
    mut terminal: DefaultTerminal,
    conn: &rusqlite::Connection,
    projects: &[Project],
) -> color_eyre::Result<()> {
    if projects.is_empty() {
        return Err(color_eyre::eyre::eyre!(
            "No projects found in the database."
        ));
    }

    let mut index = 0;
    loop {
        terminal.draw(|frame| render(frame, projects, index))?;
        if let Ok(key) = read_key() {
            match key {
                Key::Up => {
                    if index > 0 {
                        index -= 1;
                    }
                }
                Key::Down => {
                    if index < projects.len() - 1 {
                        index += 1;
                    }
                }
                Key::Enter => {
                    // Reset the terminal
                    ratatui::restore();

                    // Open the selected project
                    open_project(&projects[index])?;
                    break Ok(());
                }
                Key::Delete => {
                    ratatui::restore();
                    if yn::ask("Are you sure you want to delete this project? (y/n)")? {
                        std::fs::remove_dir_all(&projects[index].path)?;
                        crate::database::manage::delete_project(conn, projects[index].id)?;
                    }
                    show()?;
                    break Ok(()); // TODO: ensure this doesn't create deep recursion
                }
                Key::Quit => break Ok(()),
                Key::Other => {}
            }
        }
    }
}

fn render(frame: &mut Frame, projects: &[Project], selected_index: usize) {
    let vertical = Layout::vertical([
        Constraint::Length(1),
        Constraint::Fill(1),
        Constraint::Length(1),
    ])
    .split(frame.area());

    let header = Paragraph::new(Line::from("Projector - Project Gallery"))
        .block(Block::default())
        .style(Style::default().fg(Color::LightBlue))
        .centered();
    frame.render_widget(header, vertical[0]);

    let project_items: Vec<ListItem> = projects
        .iter()
        .map(|project| {
            let path_str = if project.path.starts_with("\\\\?\\") {
                &project.path[4..]
            } else {
                &project.path
            };
            let content = Line::from(Span::from(format!("{} - {}", project.name, path_str)));
            ListItem::new(content)
        })
        .collect();

    let mut state = ListState::default();
    state.select(Some(selected_index));

    let project_list = List::new(project_items)
        .block(
            Block::default()
                .borders(ratatui::widgets::Borders::ALL)
                .title(Span::styled(
                    "Projects",
                    Style::default().fg(Color::Magenta),
                )),
        )
        .highlight_style(Style::default().fg(Color::LightMagenta))
        .highlight_symbol(">> ");

    frame.render_stateful_widget(project_list, vertical[1], &mut state);

    let footer = Paragraph::new(Line::from(Span::from(
        "Use Up/Down to navigate, Enter to open, d to delete, Esc or Q to exit",
    )));
    frame.render_widget(footer, vertical[2]);
}

fn read_key() -> Result<Key, io::Error> {
    if let CrosstermEvent::Key(key_event) = event::read()? {
        if key_event.kind == KeyEventKind::Press {
            match key_event.code {
                KeyCode::Up => return Ok(Key::Up),
                KeyCode::Down => return Ok(Key::Down),
                KeyCode::Enter => return Ok(Key::Enter),
                KeyCode::Char('q') => return Ok(Key::Quit),
                KeyCode::Char('d') => return Ok(Key::Delete),
                _ => return Ok(Key::Other),
            }
        }
    }
    Ok(Key::Other)
}

fn open_project(project: &Project) -> Result<(), io::Error> {
    post_setup::editor::run_editor_setup(std::path::Path::new(&project.path))
        .expect("Failed to open editor");
    Ok(())
}

enum Key {
    Up,
    Down,
    Enter,
    Quit,
    Delete,
    Other,
}

fn blank() -> color_eyre::Result<()> {
    ratatui::init();
    ratatui::restore();
    Ok(())
}
