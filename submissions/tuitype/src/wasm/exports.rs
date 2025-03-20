use crate::{config::TestMode, App, Config};
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct WasmTuiType {
    app: App,
}

#[wasm_bindgen]
impl WasmTuiType {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Self {
        console_error_panic_hook::set_once();

        let config = Config::default();
        let app = App::new(config);

        Self { app }
    }

    #[wasm_bindgen]
    pub fn wpm(&self) -> f64 {
        self.app.stats.wpm
    }

    #[wasm_bindgen]
    pub fn accuracy(&self) -> f64 {
        self.app.stats.accuracy
    }

    #[wasm_bindgen]
    pub fn text(&self) -> String {
        self.app.text_source.full_text().to_string()
    }

    #[wasm_bindgen]
    pub fn typed_text(&self) -> String {
        self.app.typed_text.clone()
    }

    #[wasm_bindgen]
    pub fn is_complete(&self) -> bool {
        self.app.test_complete
    }

    #[wasm_bindgen]
    pub fn keypress(&mut self, key: &str) -> bool {
        let key_event = match key {
            "Escape" => crossterm::event::KeyEvent::new(
                crossterm::event::KeyCode::Esc,
                crossterm::event::KeyModifiers::empty(),
            ),
            "Backspace" => crossterm::event::KeyEvent::new(
                crossterm::event::KeyCode::Backspace,
                crossterm::event::KeyModifiers::empty(),
            ),
            "Tab" => crossterm::event::KeyEvent::new(
                crossterm::event::KeyCode::Tab,
                crossterm::event::KeyModifiers::empty(),
            ),
            "Enter" => crossterm::event::KeyEvent::new(
                crossterm::event::KeyCode::Enter,
                crossterm::event::KeyModifiers::empty(),
            ),
            " " => crossterm::event::KeyEvent::new(
                crossterm::event::KeyCode::Char(' '),
                crossterm::event::KeyModifiers::empty(),
            ),
            k if k.len() == 1 => {
                let c = k.chars().next().unwrap();
                crossterm::event::KeyEvent::new(
                    crossterm::event::KeyCode::Char(c),
                    crossterm::event::KeyModifiers::empty(),
                )
            }
            _ => return false,
        };

        if self.app.handle_key_event(key_event).is_ok() {
            if self.app.start_time.is_some() && !self.app.test_complete {
                let _ = self.app.tick();
            }
            true
        } else {
            false
        }
    }

    #[wasm_bindgen]
    pub fn set_test_mode(&mut self, mode: &str, value: Option<u32>) {
        let test_mode = match mode {
            "timed" => TestMode::Timed(value.unwrap_or(60)),
            "words" => TestMode::Words(value.unwrap_or(50)),
            "quote" => TestMode::Quote,
            "custom" => TestMode::Custom,
            _ => return,
        };

        self.app.config.test_mode = test_mode;
        self.app.restart_test();
    }

    #[wasm_bindgen]
    pub fn set_custom_text(&mut self, text: &str) {
        self.app.config.custom_text = Some(text.to_string());

        if matches!(self.app.config.test_mode, TestMode::Custom) {
            self.app.restart_test();
        }
    }

    #[wasm_bindgen]
    pub fn restart(&mut self) {
        self.app.restart_test();
    }

    #[wasm_bindgen]
    pub fn get_theme_colors(&self) -> Box<[u8]> {
        let theme = &self.app.theme;
        let colors = [
            theme.background.0,
            theme.background.1,
            theme.background.2,
            theme.text.0,
            theme.text.1,
            theme.text.2,
            theme.accent.0,
            theme.accent.1,
            theme.accent.2,
            theme.correct.0,
            theme.correct.1,
            theme.correct.2,
            theme.incorrect.0,
            theme.incorrect.1,
            theme.incorrect.2,
            theme.pending.0,
            theme.pending.1,
            theme.pending.2,
            theme.cursor.0,
            theme.cursor.1,
            theme.cursor.2,
        ];
        colors.into_boxed_slice()
    }

    #[wasm_bindgen]
    pub fn set_theme(&mut self, theme_name: &str) {
        use crate::ui::ThemeType;

        let theme_type = match theme_name {
            "light" => ThemeType::Light,
            "dark" => ThemeType::Dark,
            "sepia" => ThemeType::Sepia,
            "matrix" => ThemeType::Matrix,
            "ocean" => ThemeType::Ocean,
            _ => return,
        };

        self.app.set_theme(theme_type);
    }
}

#[wasm_bindgen(start)]
pub fn start() {
    #[cfg(target_arch = "wasm32")]
    {
        web_sys::console::log_1(&JsValue::from_str("TuiType WASM module initialized"));
    }
}
