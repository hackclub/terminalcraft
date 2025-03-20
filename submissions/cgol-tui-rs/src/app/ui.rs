use crate::{app::App, app::Area};
use ratatui::{
    layout::{Constraint, Layout},
    style::Stylize,
    text::Line,
    widgets::{canvas::Canvas, Block, BorderType},
    Frame,
};

/// area of a braille character
const BRAILLE: Area = Area {
    width: 2,
    height: 4,
};

/// ```text
///  _cgol_______________
/// |                    |
/// |                    |
/// |                    |
/// |____________________|
/// |____________________|
/// ```
pub fn ui(f: &mut Frame, app: &mut App) {
    let chunks = Layout::vertical([Constraint::Fill(1), Constraint::Length(1)]).split(f.area());

    let cgol = Block::bordered()
        .border_type(BorderType::Rounded)
        .title(format!(" Conway's Game of Life - {} ", app.universe.name));
    // 2 blocks less: border
    let new_area = Area::new(
        (chunks[0].width - 2) * BRAILLE.width,
        (chunks[0].height - 2) * BRAILLE.height,
    );
    // apply the area change
    if app.area != new_area {
        app.area = new_area;
        app.restart();
    }
    let universe = Canvas::default()
        // .x_bounds([0., chunks[0].height as f64 * 2. - 4.])
        // .y_bounds([0., chunks[0].height as f64 * 2. - 4.])
        .paint(|ctx| ctx.draw(&app.universe))
        .block(cgol);

    f.render_widget(universe, chunks[0]);

    let footer = Layout::horizontal([Constraint::Fill(1)]).split(chunks[1]);

    let current_keys_hint = "[q]uit, [r]estart, pause: [ ], nav: vim/arrows".yellow();

    let poll_t = {
        if let super::PAUSE = app.poll_t {
            "paused".into()
        } else {
            format!("Poll time: {:.0?}", app.poll_t)
        }
    }
    .light_blue();

    let div = " | ".white();
    let current_stats = vec![current_keys_hint, div, poll_t];
    let footer_data = Line::from(current_stats);

    f.render_widget(footer_data, footer[0]);
}
