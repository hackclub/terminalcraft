use std::{
    io::Write,
    sync::{
        Arc,
        atomic::{AtomicBool, Ordering},
    },
    time::Duration,
};

use crossterm::{
    ExecutableCommand,
    cursor::{self, MoveTo},
    event::{self, Event, KeyEventKind},
    style::{Color, Print, ResetColor, SetBackgroundColor, SetForegroundColor},
    terminal::{self, Clear, ClearType},
};

struct PaintCursor {
    row: u16,
    col: u16,
    canvas_rows: u16,
    canvas_cols: u16,
    color: Color,
}

impl PaintCursor {
    fn new(row: u16, col: u16, canvas_size: (u16, u16)) -> Self {
        PaintCursor {
            row,
            col,
            canvas_cols: canvas_size.0,
            canvas_rows: canvas_size.1,
            color: Color::White,
        }
    }

    fn left(&mut self, by: u16) {
        if self.col >= by {
            self.col -= by;
        } else {
            let underflow = by - self.col;
            self.col = self.canvas_cols - underflow;
        }
    }

    fn right(&mut self, by: u16) {
        if self.col < self.canvas_cols - by {
            self.col += by;
        } else {
            let overflow = by - (self.canvas_cols - self.col);
            self.col = 0 + overflow;
        }
    }

    fn up(&mut self, by: u16) {
        if self.row >= by {
            self.row -= by;
        } else {
            let underflow = by - self.row;
            self.row = self.canvas_rows - underflow;
        }
    }

    fn down(&mut self, by: u16) {
        if self.row < self.canvas_rows - by {
            self.row += by;
        } else {
            let overflow = by - (self.canvas_rows - self.row);
            self.row = 0 + overflow;
        }
    }

    fn set_canvas_size(&mut self, size: &(u16, u16)) {
        self.canvas_cols = size.0;
        self.canvas_rows = size.1;
    }
}

/// All the state and main methods for the TUI program
struct Paint2D {
    stdout: std::io::Stdout,
    running: Arc<AtomicBool>,
    cursor: PaintCursor,
    /// `(height, width)` i.e. (cols, rows)
    terminal_size: (u16, u16),
    color_canvas: Vec<Vec<Option<Color>>>,
    space_button_held: bool,
}

const BOTTOM_BAR_HEIGHT: u16 = 2;

struct ColorKey {
    key: char,
    name: &'static str,
    color: Color,
}

impl ColorKey {
    const fn new(key: char, color: Color, name: &'static str) -> Self {
        ColorKey { key, color, name }
    }
}

static COLOUR_KEYS: [ColorKey; 9] = [
    ColorKey::new('1', Color::White, "White"),
    ColorKey::new('2', Color::Red, "Red"),
    ColorKey::new('3', Color::Green, "Green"),
    ColorKey::new('4', Color::Yellow, "Yellow"),
    ColorKey::new('5', Color::Blue, "Blue"),
    ColorKey::new('6', Color::Magenta, "Magenta"),
    ColorKey::new('7', Color::Cyan, "Cyan"),
    ColorKey::new('8', Color::Grey, "Grey"),
    ColorKey::new('0', Color::Reset, "Eraser"),
];

impl Paint2D {
    fn new(terminal_size: &(u16, u16)) -> Self {
        let canvas_size = (terminal_size.0, terminal_size.1 - BOTTOM_BAR_HEIGHT);
        Paint2D {
            stdout: std::io::stdout(),
            running: Arc::new(AtomicBool::new(true)),
            cursor: PaintCursor::new(0, 1, canvas_size),
            terminal_size: terminal_size.clone(),
            color_canvas: vec![vec![None; canvas_size.0.into()]; canvas_size.1.into()],
            space_button_held: false,
        }
    }

    fn setup(&mut self) -> std::io::Result<()> {
        terminal::enable_raw_mode()?;
        self.stdout.execute(terminal::EnterAlternateScreen)?;
        self.stdout.execute(event::PushKeyboardEnhancementFlags(
            event::KeyboardEnhancementFlags::REPORT_EVENT_TYPES,
        ))?;
        // Hide the cursor as much as we can
        self.stdout
            .execute(cursor::SetCursorStyle::SteadyUnderScore)?;
        self.stdout.execute(cursor::MoveTo(0, 0))?;
        self.stdout.execute(cursor::Hide)?;
        Ok(())
    }

    fn draw_cursor(&mut self) -> std::io::Result<()> {
        const CHARS: [char; 3] = ['┣', 'ˣ', '┫'];
        let offset: u32 = (CHARS.len() / 2).try_into().unwrap();
        self.stdout.execute(SetForegroundColor(self.cursor.color))?;
        for (i, char) in CHARS.iter().enumerate() {
            // The next few lines are pure Rust pain
            // I just want to subtract two numbers and get a negative number >:(
            let i: i32 = i.try_into().unwrap();
            let relative_pos: i32 = i - TryInto::<i32>::try_into(offset).unwrap();
            let cursor_col: i32 = self.cursor.col.into();
            let current_col: i32 = cursor_col + relative_pos;
            // Back to relative sanity
            let current_col: u16 = match current_col.try_into() {
                Ok(col) => col,
                // If this errors, it's probably a negative value (therefore off the screen)
                // so we won't draw it
                Err(_) => continue,
            };
            let color = self
                .color_canvas
                .get(self.cursor.row as usize)
                .and_then(|row| row.get(current_col as usize))
                .copied()
                .flatten();
            self.stdout.execute(MoveTo(current_col, self.cursor.row))?;
            if let Some(color) = color {
                self.stdout.execute(SetBackgroundColor(color))?;
                self.stdout.execute(Print(char))?;
                self.stdout.execute(SetBackgroundColor(Color::Reset))?;
            } else {
                self.stdout.execute(Print(char))?;
            }
        }
        self.stdout.execute(SetForegroundColor(Color::White))?;
        Ok(())
    }

    fn draw_bottom_bar(&mut self) -> std::io::Result<()> {
        self.stdout.execute(MoveTo(0, self.terminal_size.1 - 1))?;
        self.stdout.execute(SetForegroundColor(Color::Black))?;
        self.stdout.execute(SetBackgroundColor(Color::White))?;
        write!(
            self.stdout,
            "Arrow keys: move, Space: paint, Number keys: change color, q: quit"
        )?;
        self.stdout.execute(ResetColor)?;
        Ok(())
    }

    fn draw_colors_bar(&mut self) -> std::io::Result<()> {
        self.stdout.execute(MoveTo(0, self.terminal_size.1 - 2))?;
        for ColorKey { key, name, color } in COLOUR_KEYS.iter() {
            let display_color = match color {
                Color::Reset => Color::White,
                _ => *color,
            };

            if self.cursor.color == *color {
                self.stdout.execute(SetBackgroundColor(display_color))?;
                self.stdout.execute(SetForegroundColor(Color::Black))?;
                write!(self.stdout, "{} {}", key, name)?;
                self.stdout.execute(ResetColor)?;
            } else {
                self.stdout.execute(SetForegroundColor(display_color))?;
                write!(self.stdout, "{} {}", key, name)?;
                self.stdout.execute(ResetColor)?;
            }
            self.stdout.execute(Print(" "))?;
        }
        Ok(())
    }

    fn redraw_screen(&mut self) -> std::io::Result<()> {
        self.stdout.execute(Clear(ClearType::All))?;
        self.stdout.execute(cursor::MoveTo(0, 0))?;
        for r in 0..self.terminal_size.1 - BOTTOM_BAR_HEIGHT {
            self.stdout.execute(cursor::MoveTo(0, r))?;
            for c in 0..self.terminal_size.0 {
                // None if the access is out of bounds, or if the colour is transparent
                let color = self
                    .color_canvas
                    .get(r as usize)
                    .and_then(|row| row.get(c as usize))
                    .copied()
                    .flatten();

                if let Some(color) = color {
                    self.stdout.execute(SetBackgroundColor(color))?;
                    self.stdout.execute(Print(" "))?;
                    self.stdout.execute(SetBackgroundColor(Color::Reset))?;
                } else {
                    self.stdout.execute(cursor::MoveRight(1))?;
                    // self.stdout.execute(Print(" "))?;
                }
            }
        }
        self.draw_cursor()?;
        self.draw_colors_bar()?;
        self.draw_bottom_bar()?;
        Ok(())
    }

    fn on_cursor_move(&mut self) -> std::io::Result<()> {
        // If Space is being held, then immediately splat some paint down
        if self.space_button_held {
            let row = self.cursor.col as usize;
            let col = self.cursor.row as usize;
            self.color_canvas[col][row] = Some(self.cursor.color);
        }
        self.redraw_screen()?;
        Ok(())
    }

    fn run(&mut self) -> std::io::Result<()> {
        self.redraw_screen()?;
        while self.running.load(Ordering::SeqCst) {
            while event::poll(Duration::from_millis(50))? {
                match event::read()? {
                    Event::Key(key) => {
                        // Keep track of if the space button is being held or not
                        if key.code == event::KeyCode::Char(' ') {
                            match key.kind {
                                KeyEventKind::Press => {
                                    self.space_button_held = true;
                                }
                                KeyEventKind::Release => {
                                    self.space_button_held = false;
                                }
                                KeyEventKind::Repeat => {}
                            }
                        }

                        // Only perform actions on key down (not key up)
                        if key.kind != KeyEventKind::Press {
                            continue;
                        }

                        let is_speedy = key.modifiers.contains(event::KeyModifiers::CONTROL);
                        let is_super_speedy =
                            is_speedy && key.modifiers.contains(event::KeyModifiers::ALT);
                        let horizontal_movement = if is_super_speedy {
                            20
                        } else if is_speedy {
                            8
                        } else {
                            1
                        };
                        let vertical_movement = if is_super_speedy {
                            8
                        } else if is_speedy {
                            2
                        } else {
                            1
                        };
                        match key.code {
                            event::KeyCode::Char('q') => {
                                self.running.store(false, Ordering::SeqCst);
                            }
                            event::KeyCode::Char('c') => {
                                if key.modifiers.contains(event::KeyModifiers::CONTROL) {
                                    // Ctrl+C has been pressed
                                    self.running.store(false, Ordering::SeqCst);
                                }
                            }
                            event::KeyCode::Left => {
                                self.cursor.left(horizontal_movement);
                                self.on_cursor_move()?;
                            }
                            event::KeyCode::Right => {
                                self.cursor.right(horizontal_movement);
                                self.on_cursor_move()?;
                            }
                            event::KeyCode::Up => {
                                self.cursor.up(vertical_movement);
                                self.on_cursor_move()?;
                            }
                            event::KeyCode::Down => {
                                self.cursor.down(vertical_movement);
                                self.on_cursor_move()?;
                            }
                            event::KeyCode::Char(' ') => {
                                let row = self.cursor.col as usize;
                                let col = self.cursor.row as usize;
                                self.color_canvas[col][row] = Some(self.cursor.color);
                                self.redraw_screen()?;
                            }
                            event::KeyCode::Char(char) => {
                                for ColorKey { key, color, .. } in COLOUR_KEYS.iter() {
                                    if char == *key {
                                        self.cursor.color = *color;
                                        self.redraw_screen()?;
                                        break;
                                    }
                                }
                            }
                            _ => {}
                        }
                    }
                    Event::Resize(cols, rows) => {
                        let new_canvas_size = (cols, rows - BOTTOM_BAR_HEIGHT);
                        // Ensure the cursor stays within the new canvas
                        if self.cursor.row >= new_canvas_size.1 {
                            self.cursor.row = new_canvas_size.1 - 1;
                        }
                        if self.cursor.col >= new_canvas_size.0 {
                            self.cursor.col = new_canvas_size.0 - 1;
                        }

                        // Update the attributes & redraw screen
                        self.terminal_size = (cols, rows);
                        self.cursor.set_canvas_size(&(cols, rows - 1));
                        self.redraw_screen()?;
                    }
                    _ => {}
                }
            }
            self.stdout.flush()?;
        }
        Ok(())
    }
}

impl Drop for Paint2D {
    fn drop(&mut self) {
        let _ = terminal::disable_raw_mode();
        let _ = self.stdout.execute(cursor::Show);
        let _ = self.stdout.execute(event::PopKeyboardEnhancementFlags);
        let _ = self.stdout.execute(terminal::LeaveAlternateScreen);
        let _ = self
            .stdout
            .execute(cursor::SetCursorStyle::DefaultUserShape);
    }
}

fn main() -> std::io::Result<()> {
    let terminal_size: (u16, u16) = terminal::size().unwrap_or((1, 1));
    let mut app = Paint2D::new(&terminal_size);
    app.setup()?;
    app.run()?;
    Ok(())
}
