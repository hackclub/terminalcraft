use crate::{App, AppResult, Config};
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmApp {
    app: App,
}

#[wasm_bindgen]
impl WasmApp {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        console_error_panic_hook::set_once();

        let config = Config::default();
        let app = App::new(config);

        Self { app }
    }

    #[wasm_bindgen]
    pub fn key_press(&mut self, key: &str) -> bool {
        let key_event = convert_key_to_event(key);

        if let Some(key_event) = key_event {
            if let Ok(_) = self.app.handle_key_event(key_event) {
                return true;
            }
        }
        false
    }

    #[wasm_bindgen]
    pub fn get_wpm(&self) -> f64 {
        self.app.stats.wpm
    }

    #[wasm_bindgen]
    pub fn get_accuracy(&self) -> f64 {
        self.app.stats.accuracy
    }

    #[wasm_bindgen]
    pub fn get_target_text(&self) -> String {
        self.app.text_source.full_text().to_string()
    }

    #[wasm_bindgen]
    pub fn get_typed_text(&self) -> String {
        self.app.typed_text.clone()
    }

    #[wasm_bindgen]
    pub fn get_cursor_position(&self) -> usize {
        self.app.cursor_pos
    }

    #[wasm_bindgen]
    pub fn is_test_complete(&self) -> bool {
        self.app.test_complete
    }

    #[wasm_bindgen]
    pub fn restart_test(&mut self) {
        self.app.restart_test();
    }

    #[wasm_bindgen]
    pub fn set_test_mode(&mut self, mode_type: u8, value: u32) {
        use crate::config::TestMode;

        self.app.config.test_mode = match mode_type {
            0 => TestMode::Timed(value),
            1 => TestMode::Words(value),
            2 => TestMode::Quote,
            3 => TestMode::Custom,
            _ => TestMode::Timed(60),
        };

        self.app.restart_test();
    }

    #[wasm_bindgen]
    pub fn set_theme(&mut self, theme_type: u8) {
        use crate::ui::ThemeType;

        let theme = match theme_type {
            0 => ThemeType::Light,
            1 => ThemeType::Dark,
            2 => ThemeType::Sepia,
            3 => ThemeType::Matrix,
            4 => ThemeType::Ocean,
            _ => ThemeType::Dark,
        };

        self.app.set_theme(theme);
    }

    #[wasm_bindgen]
    pub fn set_custom_text(&mut self, text: String) {
        self.app.config.custom_text = Some(text);
        self.app.restart_test();
    }
}

fn convert_key_to_event(key: &str) -> Option<crossterm::event::KeyEvent> {
    use crossterm::event::{KeyCode, KeyEvent, KeyModifiers};

    match key {
        "Escape" => Some(KeyEvent::new(KeyCode::Esc, KeyModifiers::empty())),
        "Tab" => Some(KeyEvent::new(KeyCode::Tab, KeyModifiers::empty())),
        "Backspace" => Some(KeyEvent::new(KeyCode::Backspace, KeyModifiers::empty())),
        "Enter" => Some(KeyEvent::new(KeyCode::Enter, KeyModifiers::empty())),
        "Space" => Some(KeyEvent::new(KeyCode::Char(' '), KeyModifiers::empty())),
        s if s.len() == 1 => {
            let ch = s.chars().next().unwrap();
            Some(KeyEvent::new(KeyCode::Char(ch), KeyModifiers::empty()))
        }
        _ => None,
    }
}

#[wasm_bindgen(start)]
pub fn start() {
    web_sys::console::log_1(&JsValue::from_str("TuiType WASM module initialized"));
}
