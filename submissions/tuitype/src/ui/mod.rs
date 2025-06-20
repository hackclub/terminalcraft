mod draw;
mod themes;

use crate::config::{Config, Difficulty, TestMode, ThemeConfig};
use crate::input::Event;
use crate::stats::TypingStats;
use crate::text::TextSource;
use crate::AppResult;
use std::collections::HashMap;
use std::time::Instant;

pub use draw::render;
pub use themes::{get_theme, ThemeType};

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum MenuState {
    Typing,

    MainMenu(usize),

    TestModeMenu(usize),

    DifficultyMenu(usize),

    TimeMenu(usize),

    WordCountMenu(usize),

    Help,

    ThemeMenu(usize),

    SettingsMenu(usize),

    TestComplete,

    CustomTimedInput(String),

    CustomWordsInput(String),
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum WarningState {
    None,

    RepeatModeSettings {
        action: String,

        prev_state: Box<MenuState>,
    },
}

impl Default for WarningState {
    fn default() -> Self {
        Self::None
    }
}

impl Default for MenuState {
    fn default() -> Self {
        Self::Typing
    }
}

pub struct App {
    pub config: Config,

    pub running: bool,

    pub text_source: TextSource,

    pub typed_text: String,

    pub cursor_pos: usize,

    pub stats: TypingStats,

    pub start_time: Option<Instant>,

    pub end_time: Option<Instant>,

    pub test_complete: bool,

    pub theme: ThemeConfig,

    pub menu_state: MenuState,

    pub time_remaining: Option<u32>,

    pub warning_state: WarningState,

    key_timestamps: HashMap<crossterm::event::KeyCode, Instant>,
    last_restart: Instant,

    pub test_end_reason: Option<String>,
}

impl App {
    pub fn new(config: Config) -> Self {
        let text_source = TextSource::new(&config);
        let theme = get_theme(config.theme_type);

        let time_remaining = match config.test_mode {
            TestMode::Timed(seconds) => Some(seconds),
            _ => None,
        };

        Self {
            config,
            running: true,
            text_source,
            typed_text: String::new(),
            cursor_pos: 0,
            stats: TypingStats::default(),
            start_time: None,
            end_time: None,
            test_complete: false,
            theme,
            menu_state: MenuState::default(),
            time_remaining,
            warning_state: WarningState::default(),
            key_timestamps: HashMap::new(),
            last_restart: Instant::now(),
            test_end_reason: None,
        }
    }

    fn handle_menu_keys(&mut self, key_event: crossterm::event::KeyEvent) -> AppResult<()> {
        use crossterm::event::KeyCode;

        match (self.menu_state.clone(), key_event.code) {
            (MenuState::MainMenu(idx), KeyCode::Left) | (MenuState::MainMenu(idx), KeyCode::Up) => {
                self.menu_state = MenuState::MainMenu(idx.saturating_sub(1));
            }
            (MenuState::MainMenu(idx), KeyCode::Right)
            | (MenuState::MainMenu(idx), KeyCode::Down) => {
                let menu_items_count = 6;
                self.menu_state = MenuState::MainMenu((idx + 1).min(menu_items_count - 1));
            }
            (MenuState::MainMenu(idx), KeyCode::Enter) => match idx {
                0 => self.menu_state = MenuState::TestModeMenu(0),
                1 => self.menu_state = MenuState::DifficultyMenu(0),
                2 => self.menu_state = MenuState::ThemeMenu(0),
                3 => self.menu_state = MenuState::SettingsMenu(0),
                4 => self.menu_state = MenuState::Help,
                _ => self.menu_state = MenuState::Typing,
            },

            (MenuState::TestModeMenu(idx), KeyCode::Left)
            | (MenuState::TestModeMenu(idx), KeyCode::Up) => {
                self.menu_state = MenuState::TestModeMenu(idx.saturating_sub(1));
            }
            (MenuState::TestModeMenu(idx), KeyCode::Right)
            | (MenuState::TestModeMenu(idx), KeyCode::Down) => {
                self.menu_state = MenuState::TestModeMenu((idx + 1).min(3));
            }
            (MenuState::TestModeMenu(idx), KeyCode::Enter) => {
                if !self.can_change_settings("test_mode") {
                    self.set_repeat_mode_warning(
                        "Test mode cannot be changed while Repeat Mode is active.".to_string(),
                    );
                    return Ok(());
                }

                match idx {
                    0 => self.menu_state = MenuState::TimeMenu(0),
                    1 => self.menu_state = MenuState::WordCountMenu(0),
                    2 => {
                        self.config.test_mode = TestMode::Quote;
                        self.menu_state = MenuState::Typing;
                        self.restart_test();
                    }
                    _ => {
                        self.menu_state = MenuState::MainMenu(0);
                    }
                }
            }

            (MenuState::TimeMenu(idx), KeyCode::Left) | (MenuState::TimeMenu(idx), KeyCode::Up) => {
                self.menu_state = MenuState::TimeMenu(idx.saturating_sub(1));
            }
            (MenuState::TimeMenu(idx), KeyCode::Right)
            | (MenuState::TimeMenu(idx), KeyCode::Down) => {
                self.menu_state = MenuState::TimeMenu((idx + 1).min(5));
            }
            (MenuState::TimeMenu(idx), KeyCode::Enter) => {
                if idx == 5 {
                    self.menu_state = MenuState::MainMenu(0);
                } else if idx == 4 {
                    if !self.can_change_settings("time") {
                        self.set_repeat_mode_warning(
                            "Time cannot be changed to a custom value while Repeat Mode is active unless already using a timed test.".to_string(),
                        );
                        return Ok(());
                    }

                    self.menu_state = MenuState::CustomTimedInput(String::new());
                } else {
                    let seconds = match idx {
                        0 => 15,
                        1 => 30,
                        2 => 60,
                        3 => 120,
                        _ => 60,
                    };

                    if !matches!(self.config.test_mode, TestMode::Timed(_)) {
                        if !self.can_change_settings("test_mode") {
                            self.set_repeat_mode_warning(
                                "Test mode cannot be changed while Repeat Mode is active."
                                    .to_string(),
                            );
                            return Ok(());
                        }
                    }

                    self.config.test_mode = TestMode::Timed(seconds);
                    self.time_remaining = Some(seconds);
                    self.menu_state = MenuState::Typing;
                    self.restart_test();
                }
            }

            (MenuState::WordCountMenu(idx), KeyCode::Left)
            | (MenuState::WordCountMenu(idx), KeyCode::Up) => {
                self.menu_state = MenuState::WordCountMenu(idx.saturating_sub(1));
            }
            (MenuState::WordCountMenu(idx), KeyCode::Right)
            | (MenuState::WordCountMenu(idx), KeyCode::Down) => {
                self.menu_state = MenuState::WordCountMenu((idx + 1).min(4));
            }
            (MenuState::WordCountMenu(idx), KeyCode::Enter) => {
                if idx == 4 {
                    self.menu_state = MenuState::MainMenu(0);
                } else if idx == 3 {
                    if !self.can_change_settings("test_mode") {
                        self.set_repeat_mode_warning(
                            "Custom word count cannot be set while Repeat Mode is active."
                                .to_string(),
                        );
                        return Ok(());
                    }
                    self.menu_state = MenuState::CustomWordsInput(String::new());
                } else {
                    if !matches!(self.config.test_mode, TestMode::Words(_)) {
                        if !self.can_change_settings("test_mode") {
                            self.set_repeat_mode_warning(
                                "Test mode cannot be changed while Repeat Mode is active."
                                    .to_string(),
                            );
                            return Ok(());
                        }
                    } else {
                        if !self.can_change_settings("test_mode") {
                            self.set_repeat_mode_warning(
                                "Word count cannot be changed while Repeat Mode is active."
                                    .to_string(),
                            );
                            return Ok(());
                        }
                    }

                    let words = match idx {
                        0 => 10,
                        1 => 25,
                        2 => 50,
                        _ => 10,
                    };
                    self.config.test_mode = TestMode::Words(words);
                    self.menu_state = MenuState::Typing;
                    self.restart_test();
                }
            }

            (MenuState::DifficultyMenu(idx), KeyCode::Left)
            | (MenuState::DifficultyMenu(idx), KeyCode::Up) => {
                self.menu_state = MenuState::DifficultyMenu(idx.saturating_sub(1));
            }
            (MenuState::DifficultyMenu(idx), KeyCode::Right)
            | (MenuState::DifficultyMenu(idx), KeyCode::Down) => {
                self.menu_state = MenuState::DifficultyMenu((idx + 1).min(3));
            }
            (MenuState::DifficultyMenu(idx), KeyCode::Enter) => {
                if idx == 3 {
                    self.menu_state = MenuState::MainMenu(0);
                    return Ok(());
                }

                if !self.can_change_settings("difficulty") {
                    self.set_repeat_mode_warning(
                        "Difficulty cannot be changed while Repeat Mode is active.".to_string(),
                    );
                    return Ok(());
                }

                self.config.difficulty = match idx {
                    0 => Difficulty::Easy,
                    1 => Difficulty::Medium,
                    2 => Difficulty::Hard,
                    _ => Difficulty::Medium,
                };

                self.menu_state = MenuState::Typing;
                self.restart_test();
            }

            (MenuState::ThemeMenu(idx), KeyCode::Left)
            | (MenuState::ThemeMenu(idx), KeyCode::Up) => {
                self.menu_state = MenuState::ThemeMenu(idx.saturating_sub(1));
            }
            (MenuState::ThemeMenu(idx), KeyCode::Right)
            | (MenuState::ThemeMenu(idx), KeyCode::Down) => {
                self.menu_state = MenuState::ThemeMenu((idx + 1).min(5));
            }
            (MenuState::ThemeMenu(idx), KeyCode::Enter) => {
                if idx == 5 {
                    self.menu_state = MenuState::MainMenu(0);
                    return Ok(());
                }

                if !self.can_change_settings("theme") {
                    self.set_repeat_mode_warning(
                        "Theme cannot be changed while Repeat Mode is active.".to_string(),
                    );
                    return Ok(());
                }

                let theme = match idx {
                    0 => ThemeType::Light,
                    1 => ThemeType::Dark,
                    2 => ThemeType::Sepia,
                    3 => ThemeType::Matrix,
                    4 => ThemeType::Ocean,
                    _ => ThemeType::Dark,
                };
                self.set_theme(theme);
                self.config.theme_type = theme;
                self.config.save().ok();
                self.menu_state = MenuState::Typing;
            }

            (MenuState::SettingsMenu(idx), KeyCode::Left)
            | (MenuState::SettingsMenu(idx), KeyCode::Up) => {
                self.menu_state = MenuState::SettingsMenu(idx.saturating_sub(1));
            }
            (MenuState::SettingsMenu(idx), KeyCode::Right)
            | (MenuState::SettingsMenu(idx), KeyCode::Down) => {
                self.menu_state = MenuState::SettingsMenu((idx + 1).min(2));
            }
            (MenuState::SettingsMenu(idx), KeyCode::Enter) => match idx {
                0 => {
                    self.config.repeat_test = !self.config.repeat_test;
                    if !self.config.repeat_test {
                        self.config.last_test_text = None;
                    }
                    self.config.save().ok();
                    self.menu_state = MenuState::Typing;
                }
                1 => {
                    self.config.end_on_first_error = !self.config.end_on_first_error;
                    self.config.save().ok();
                    self.menu_state = MenuState::Typing;
                }
                2 => {
                    self.menu_state = MenuState::MainMenu(0);
                }
                _ => {}
            },

            (MenuState::Help, KeyCode::Enter) | (MenuState::Help, KeyCode::Esc) => {
                self.menu_state = MenuState::Typing;
            }

            (MenuState::TestComplete, KeyCode::Enter) | (MenuState::TestComplete, KeyCode::Esc) => {
                self.restart_test();
                self.menu_state = MenuState::Typing;
            }

            (MenuState::CustomTimedInput(ref input), KeyCode::Char(c)) if c.is_numeric() => {
                if input.len() < 3 {
                    let mut new_input = input.clone();
                    new_input.push(c);
                    self.menu_state = MenuState::CustomTimedInput(new_input);
                }
            }
            (MenuState::CustomTimedInput(ref input), KeyCode::Backspace) => {
                let mut new_input = input.clone();
                new_input.pop();
                self.menu_state = MenuState::CustomTimedInput(new_input);
            }
            (MenuState::CustomTimedInput(ref input), KeyCode::Enter) => {
                if let Ok(seconds) = input.parse::<u32>() {
                    if seconds > 0 {
                        self.config.test_mode = TestMode::Timed(seconds);
                        self.time_remaining = Some(seconds);
                        self.menu_state = MenuState::Typing;
                        self.restart_test();
                    } else {
                        self.menu_state = MenuState::CustomTimedInput(input.clone());
                    }
                } else {
                    self.menu_state = MenuState::TimeMenu(0);
                }
            }

            (MenuState::CustomWordsInput(ref input), KeyCode::Char(c)) if c.is_numeric() => {
                if input.len() < 3 {
                    let mut new_input = input.clone();
                    new_input.push(c);
                    self.menu_state = MenuState::CustomWordsInput(new_input);
                }
            }
            (MenuState::CustomWordsInput(ref input), KeyCode::Backspace) => {
                let mut new_input = input.clone();
                new_input.pop();
                self.menu_state = MenuState::CustomWordsInput(new_input);
            }
            (MenuState::CustomWordsInput(ref input), KeyCode::Enter) => {
                if let Ok(words) = input.parse::<u32>() {
                    if words > 0 {
                        self.config.test_mode = TestMode::Words(words);
                        self.menu_state = MenuState::Typing;
                        self.restart_test();
                    } else {
                        self.menu_state = MenuState::CustomWordsInput(input.clone());
                    }
                } else {
                    self.menu_state = MenuState::WordCountMenu(0);
                }
            }

            (_, KeyCode::Esc) => {
                self.menu_state = MenuState::Typing;
            }

            _ => {}
        }

        Ok(())
    }

    pub fn tick(&mut self) -> AppResult<()> {
        if self.start_time.is_some() && !self.test_complete {
            self.update_test_progress();
        }
        Ok(())
    }

    pub fn handle_events(&mut self, event: Event) -> AppResult<()> {
        match event {
            Event::Key(key_event) => self.handle_key_event(key_event),
            _ => Ok(()),
        }
    }

    fn handle_numeric_menu_selection(&mut self, digit: u8) -> AppResult<bool> {
        let idx = (digit - 1) as usize;

        match self.menu_state.clone() {
            MenuState::MainMenu(_) => {
                if idx < 6 {
                    self.menu_state = MenuState::MainMenu(idx);

                    self.handle_menu_keys(Self::create_enter_key_event())?;
                    return Ok(true);
                }
            }
            MenuState::TestModeMenu(_) => {
                if idx < 4 {
                    self.menu_state = MenuState::TestModeMenu(idx);
                    self.handle_menu_keys(Self::create_enter_key_event())?;
                    return Ok(true);
                }
            }
            MenuState::DifficultyMenu(_) => {
                if idx < 4 {
                    self.menu_state = MenuState::DifficultyMenu(idx);
                    self.handle_menu_keys(Self::create_enter_key_event())?;
                    return Ok(true);
                }
            }
            MenuState::TimeMenu(_) => {
                if idx < 6 {
                    self.menu_state = MenuState::TimeMenu(idx);
                    self.handle_menu_keys(Self::create_enter_key_event())?;
                    return Ok(true);
                }
            }
            MenuState::WordCountMenu(_) => {
                if idx < 5 {
                    self.menu_state = MenuState::WordCountMenu(idx);
                    self.handle_menu_keys(Self::create_enter_key_event())?;
                    return Ok(true);
                }
            }
            MenuState::ThemeMenu(_) => {
                if idx < 6 {
                    self.menu_state = MenuState::ThemeMenu(idx);
                    self.handle_menu_keys(Self::create_enter_key_event())?;
                    return Ok(true);
                }
            }
            MenuState::SettingsMenu(_) => {
                if idx < 3 {
                    self.menu_state = MenuState::SettingsMenu(idx);
                    self.handle_menu_keys(Self::create_enter_key_event())?;
                    return Ok(true);
                }
            }
            _ => {}
        }

        Ok(false)
    }

    fn create_enter_key_event() -> crossterm::event::KeyEvent {
        crossterm::event::KeyEvent {
            code: crossterm::event::KeyCode::Enter,
            modifiers: crossterm::event::KeyModifiers::empty(),
            kind: crossterm::event::KeyEventKind::Press,
            state: crossterm::event::KeyEventState::NONE,
        }
    }

    pub fn handle_key_event(&mut self, key_event: crossterm::event::KeyEvent) -> AppResult<()> {
        use crossterm::event::{KeyCode, KeyModifiers};

        if self.warning_state != WarningState::None {
            if self.handle_warning(key_event) {
                return Ok(());
            }
        }

        let now = Instant::now();
        let key_code = key_event.code;

        if let Some(last_press_time) = self.key_timestamps.get(&key_code) {
            let elapsed = now.duration_since(*last_press_time).as_millis();

            if elapsed < 60 {
                return Ok(());
            }
        }

        self.key_timestamps.insert(key_code, now);

        if key_event.code == KeyCode::Char('c')
            && key_event.modifiers.contains(KeyModifiers::CONTROL)
        {
            self.running = false;
            return Ok(());
        }

        if (key_event.code == KeyCode::Tab)
            || (key_event.code == KeyCode::Enter && self.test_complete)
        {
            let elapsed_since_restart = now.duration_since(self.last_restart).as_millis() as u64;
            if elapsed_since_restart < 60 {
                return Ok(());
            }
            self.last_restart = now;
            self.restart_test();
            self.menu_state = MenuState::Typing;
            return Ok(());
        }

        if self.menu_state != MenuState::Typing
            && self.menu_state != MenuState::Help
            && self.menu_state != MenuState::CustomTimedInput("".into())
            && self.menu_state != MenuState::CustomWordsInput("".into())
        {
            if let KeyCode::Char(c) = key_event.code {
                if c.is_ascii_digit() && c != '0' {
                    let digit = c as u8 - b'0';
                    if self.handle_numeric_menu_selection(digit)? {
                        return Ok(());
                    }
                }
            }
        }

        if self.menu_state != MenuState::Typing {
            return self.handle_menu_keys(key_event);
        }

        match key_event.code {
            KeyCode::Esc => {
                if self.test_complete {
                    self.restart_test();
                    self.menu_state = MenuState::Typing;
                } else {
                    if self.menu_state == MenuState::Typing {
                        self.menu_state = MenuState::MainMenu(0);
                    } else {
                        self.menu_state = MenuState::Typing;
                    }
                }
            }

            KeyCode::Char(c) if !self.test_complete => {
                if self.start_time.is_none() {
                    self.start_time = Some(Instant::now());

                    if let TestMode::Timed(seconds) = self.config.test_mode {
                        self.time_remaining = Some(seconds);
                    }
                }

                if self.text_source.should_add_more_words(self.cursor_pos) {
                    let trimmed = self.text_source.add_more_words();

                    if trimmed > 0 && self.cursor_pos > 0 {
                        if trimmed < self.cursor_pos {
                            self.cursor_pos -= trimmed;

                            if trimmed < self.typed_text.len() {
                                self.typed_text = self.typed_text[trimmed..].to_string();
                            } else {
                                self.typed_text.clear();
                                self.cursor_pos = 0;
                            }
                        } else {
                            self.typed_text.clear();
                            self.cursor_pos = 0;
                        }
                    }
                }

                let target_text = self.text_source.full_text().to_string();

                if c == ' ' {
                    let is_timed_test = matches!(self.config.test_mode, TestMode::Timed(_));
                    if !is_timed_test
                        && self.cursor_pos >= target_text.len()
                        && !self.text_source.is_scrollable
                    {
                        return Ok(());
                    }

                    if self.config.end_on_first_error
                        && self.cursor_pos < target_text.len()
                        && target_text.chars().nth(self.cursor_pos) != Some(' ')
                    {
                        self.typed_text.push(' ');
                        self.cursor_pos += 1;

                        self.stats.update(&self.text_source, &self.typed_text);

                        self.complete_test();
                        return Ok(());
                    }

                    if let TestMode::Quote = self.config.test_mode {
                        self.typed_text.push(' ');
                        self.cursor_pos += 1;
                    } else {
                        if self.cursor_pos < target_text.len() {
                            let current_word_end = target_text[self.cursor_pos..]
                                .find(' ')
                                .map(|i| i + self.cursor_pos)
                                .unwrap_or(target_text.len());

                            while self.cursor_pos < current_word_end {
                                let target_char = target_text.chars().nth(self.cursor_pos).unwrap();

                                let error_char = if target_char == 'x' { 'y' } else { 'x' };
                                self.typed_text.push(error_char);
                                self.cursor_pos += 1;
                            }
                        }

                        self.typed_text.push(' ');
                        self.cursor_pos += 1;
                    }
                } else {
                    let is_timed_test = matches!(self.config.test_mode, TestMode::Timed(_));
                    if !is_timed_test && self.cursor_pos >= target_text.len() {
                        if !self.text_source.is_scrollable || self.text_source.is_complete() {
                            return Ok(());
                        }

                        if self.text_source.should_add_more_words(self.cursor_pos) {
                            self.text_source.add_more_words();

                            let _new_text = self.text_source.full_text().to_string();
                            return self.handle_key_event(key_event);
                        }
                    }

                    if self.config.end_on_first_error && self.cursor_pos < target_text.len() {
                        let target_char = target_text.chars().nth(self.cursor_pos).unwrap();
                        if c != target_char {
                            self.typed_text.push(c);
                            self.cursor_pos += 1;

                            self.stats.update(&self.text_source, &self.typed_text);

                            self.complete_test();
                            return Ok(());
                        }
                    }

                    self.typed_text.push(c);
                    self.cursor_pos += 1;
                }

                if c == ' ' || self.cursor_pos % 5 == 0 {
                    self.stats.update(&self.text_source, &self.typed_text);
                }

                self.tick()?;
            }

            KeyCode::Backspace if !self.test_complete && !self.typed_text.is_empty() => {
                self.typed_text.pop();
                self.cursor_pos = self.cursor_pos.saturating_sub(1);
                self.stats.update(&self.text_source, &self.typed_text);
            }

            _ => {}
        }

        Ok(())
    }

    fn update_test_progress(&mut self) {
        if let (Some(start), TestMode::Timed(seconds)) = (self.start_time, self.config.test_mode) {
            if !self.test_complete {
                let elapsed = start.elapsed().as_secs() as u32;
                if elapsed >= seconds {
                    self.time_remaining = Some(0);
                    self.complete_test();
                } else {
                    self.time_remaining = Some(seconds - elapsed);

                    if self.text_source.should_add_more_words(self.cursor_pos) {
                        let trimmed = self.text_source.add_more_words();

                        if trimmed > 0 && self.cursor_pos > 0 {
                            if trimmed < self.cursor_pos {
                                self.cursor_pos -= trimmed;

                                if trimmed < self.typed_text.len() {
                                    self.typed_text = self.typed_text[trimmed..].to_string();
                                } else {
                                    self.typed_text.clear();
                                    self.cursor_pos = 0;
                                }
                            } else {
                                self.typed_text.clear();
                                self.cursor_pos = 0;
                            }
                        }
                    }
                }
            }
        } else {
            if !matches!(self.config.test_mode, TestMode::Timed(_)) {
                let is_word_limit_reached = if self.text_source.is_scrollable {
                    self.text_source.is_complete()
                        && self.typed_text.len() >= self.text_source.full_text().len()
                } else {
                    self.typed_text.len() >= self.text_source.full_text().len()
                };

                if is_word_limit_reached {
                    self.complete_test();
                }
            }
        }

        if let Some(start) = self.start_time {
            if !self.test_complete {
                let elapsed = start.elapsed().as_secs_f64();
                if elapsed > 0.0 {
                    self.stats.calculate_wpm(elapsed);
                }
            }
        }
    }

    fn complete_test(&mut self) {
        if !self.test_complete {
            self.test_complete = true;
            self.end_time = Some(Instant::now());

            if self.config.end_on_first_error && self.stats.incorrect_chars > 0 {
                self.test_end_reason = Some("Test ended due to typing error".to_string());
            }

            self.menu_state = MenuState::TestComplete;
            self.stats.finalize();
        }
    }

    pub fn restart_test(&mut self) {
        if self.config.repeat_test
            && self.config.last_test_text.is_none()
            && !self.text_source.full_text().is_empty()
        {
            self.config.last_test_text = Some(self.text_source.full_text().to_string());
            self.config.save().ok();
        }

        self.text_source = TextSource::new(&self.config);
        self.typed_text.clear();
        self.cursor_pos = 0;
        self.stats = TypingStats::default();
        self.start_time = None;
        self.end_time = None;
        self.key_timestamps.clear();
        self.test_complete = false;
        self.test_end_reason = None;
    }

    pub fn set_theme(&mut self, theme_type: ThemeType) {
        self.theme = get_theme(theme_type);
        self.config.theme_type = theme_type;
    }

    fn can_change_settings(&self, setting_type: &str) -> bool {
        if !self.config.repeat_test {
            return true;
        }

        if setting_type == "time" && matches!(self.config.test_mode, TestMode::Timed(_)) {
            return true;
        }

        false
    }

    fn set_repeat_mode_warning(&mut self, action: String) {
        let prev_state = Box::new(self.menu_state.clone());

        self.warning_state = WarningState::RepeatModeSettings { action, prev_state };
    }

    fn handle_warning(&mut self, key_event: crossterm::event::KeyEvent) -> bool {
        use crossterm::event::KeyCode;

        match &self.warning_state {
            WarningState::None => false,

            WarningState::RepeatModeSettings {
                action: _,
                prev_state,
            } => match key_event.code {
                KeyCode::Enter => {
                    self.config.repeat_test = false;
                    self.config.last_test_text = None;
                    self.config.save().ok();

                    self.menu_state = (**prev_state).clone();

                    self.warning_state = WarningState::None;
                    true
                }

                KeyCode::Esc => {
                    self.menu_state = (**prev_state).clone();

                    self.warning_state = WarningState::None;
                    true
                }

                _ => true,
            },
        }
    }
}
