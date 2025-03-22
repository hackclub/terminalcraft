use std::{
    io::Write,
    sync::{
        Arc,
        atomic::{AtomicBool, Ordering},
    },
    time::Duration,
};

use chrono::Local;
use crossterm::{
    ExecutableCommand,
    cursor::{self, MoveTo},
    event::{self, Event, KeyEventKind},
    style::{Color, Print, ResetColor, SetBackgroundColor, SetForegroundColor},
    terminal::{self, Clear, ClearType},
};
use image::{Rgb, RgbImage};

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

fn make_dark(color: Color) -> Color {
    match color {
        Color::White => Color::Grey,
        Color::Red => Color::DarkRed,
        Color::Green => Color::DarkGreen,
        Color::Yellow => Color::DarkYellow,
        Color::Blue => Color::DarkBlue,
        Color::Magenta => Color::DarkMagenta,
        Color::Cyan => Color::DarkCyan,
        Color::Grey => Color::Black,
        _ => color,
    }
}

/// All the state and main methods for the TUI program
struct Paint2D {
    stdout: std::io::Stdout,
    running: Arc<AtomicBool>,
    cursor: PaintCursor,
    /// `(height, width)` i.e. (cols, rows)
    terminal_size: (u16, u16),
    /// A vec of rows. Can be accessed like `color_canvas[row][col]`
    color_canvas: Vec<Vec<Option<Color>>>,
    space_button_held: bool,
    /// True if the terminal sends key release events (as well as normal key down events)
    enhanced_key_events: bool,
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
            // True if the terminal sends key release events (as well as normal key down events)
            enhanced_key_events: false,
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
                self.stdout.execute(SetForegroundColor(make_dark(color)))?;
                self.stdout.execute(Print(char))?;
                self.stdout.execute(SetBackgroundColor(Color::Reset))?;
                self.stdout.execute(SetForegroundColor(Color::Reset))?;
            } else {
                self.stdout.execute(SetForegroundColor(self.cursor.color))?;
                self.stdout.execute(Print(char))?;
                self.stdout.execute(SetForegroundColor(Color::Reset))?;
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
            "Arrow keys: move, Space: paint, Number keys: change color, E: export, Q: quit"
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

    fn export_canvas_to_image(&self) {
        // Block widths and heights based on Kitty with default settings
        const BLOCK_WIDTH: u16 = 9;
        const BLOCK_HEIGHT: u16 = 20;
        let image_width = self.cursor.canvas_cols * BLOCK_WIDTH;
        let image_height = self.cursor.canvas_rows * BLOCK_HEIGHT;
        let mut image = RgbImage::new(image_width.into(), image_height.into());
        for row in 0..self.cursor.canvas_rows {
            for col in 0..self.cursor.canvas_cols {
                // Named color colors are based on the default Kitty colors
                let rgb = match self.color_canvas[row as usize][col as usize] {
                    Some(Color::Reset) => Rgb([0, 0, 0]),
                    Some(Color::White) => Rgb([255, 255, 255]),
                    Some(Color::Red) => Rgb([242, 31, 30]),
                    Some(Color::Green) => Rgb([34, 253, 0]),
                    Some(Color::Yellow) => Rgb([254, 253, 0]),
                    Some(Color::Blue) => Rgb([25, 143, 255]),
                    Some(Color::Magenta) => Rgb([253, 39, 255]),
                    Some(Color::Cyan) => Rgb([19, 255, 254]),
                    Some(Color::Grey) => Rgb([221, 221, 221]),
                    Some(Color::Rgb { r, g, b }) => Rgb([r, g, b]),
                    None => Rgb([0, 0, 0]),
                    _ => Rgb([0, 0, 0]), // Any other colours aren't supported by the program, so we draw them black
                };
                // Draw the block to the image buffer!
                // I feel like there should be a more efficient way to do this (without iterating)
                let start_x = col * BLOCK_WIDTH;
                let start_y = row * BLOCK_HEIGHT;
                for y in 0..BLOCK_HEIGHT {
                    for x in 0..BLOCK_WIDTH {
                        image.put_pixel((start_x + x).into(), (start_y + y).into(), rgb);
                    }
                }
            }
        }
        // Save the image to a file
        let time = Local::now().format("%Y-%m-%d %H_%M_%S");
        let filename = format!("Paint 2D at {}.png", time);
        match image.save(&filename) {
            Ok(_) => {
                print!(" Exported canvas to \"{}\"", filename);
            }
            Err(_) => {
                print!(" Error exporting canvas to {}", filename);
            }
        }
    }

    fn run(&mut self) -> std::io::Result<()> {
        self.redraw_screen()?;
        while self.running.load(Ordering::SeqCst) {
            while event::poll(Duration::from_millis(50))? {
                match event::read()? {
                    Event::Key(key) => {
                        // We need to know if we receive key release events or not
                        // This is a hacky way of working that out
                        if key.kind != KeyEventKind::Press {
                            self.enhanced_key_events = true;
                        }

                        // Keep track of if the space button is being held or not
                        if key.code == event::KeyCode::Char(' ') && self.enhanced_key_events {
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

                        // Prevents actions happening twice per key press
                        if key.kind == KeyEventKind::Release {
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
                            event::KeyCode::Char('e') => {
                                self.export_canvas_to_image();
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
