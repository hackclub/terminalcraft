use std::error;

pub type AppResult<T> = std::result::Result<T, Box<dyn error::Error>>;

#[derive(Debug)]
pub struct App {
    pub running: bool,
    pub cursor_pos: usize,
    pub messages: Vec<String>,
    pub input: String,
}

impl Default for App {
    fn default() -> Self {
        Self {
            running: true,
            cursor_pos: 0,
            messages: Vec::new(),
            input: String::new(),
        }
    }
}

impl App {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn tick(&self) {}

    pub fn quit(&mut self) {
        self.running = false;
    }

    pub fn cursor_left(&mut self) {
        if (self.cursor_pos) > 0 {
            self.cursor_pos -= 1;
        }
    }

    pub fn cursor_right(&mut self) {
        if self.cursor_pos < self.input.len() {
            self.cursor_pos += 1;
        }
    }

    pub fn add_message(&mut self, message: String) {
        // Add a message to be rendered
        self.messages.push(message);
    }

    pub fn update_input(&mut self, input: String) {
        self.input = input;
        self.cursor_pos = self.input.len();
    }

    pub fn clear_input(&mut self) {
        self.input.clear();
        self.cursor_pos = 0;
    }

    pub fn add_char(&mut self, c: char) {
        self.input.insert(self.cursor_pos, c);
        self.cursor_pos += 1;
    }

    pub fn remove_char(&mut self) {
        if self.input.len() > 0 && self.cursor_pos > 0 {
            if self.cursor_pos < self.input.len() {
                self.input.remove(self.cursor_pos);
            } else {
                self.input.pop();
            }
            self.cursor_pos -= 1;
        }
    }
}
