use crate::ui::ThemeType;
use anyhow::Result;
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::PathBuf;

#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize)]
pub enum Difficulty {
    Easy,
    Medium,
    Hard,
    Custom,
}

#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize)]
pub enum TestMode {
    Timed(u32),

    Words(u32),

    Quote,

    Custom,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub enum FontStyle {
    Default,
    Simple,
    Monospace,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct ThemeConfig {
    pub background: (u8, u8, u8),

    pub text: (u8, u8, u8),

    pub accent: (u8, u8, u8),

    pub correct: (u8, u8, u8),

    pub incorrect: (u8, u8, u8),

    pub pending: (u8, u8, u8),

    pub cursor: (u8, u8, u8),
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Config {
    pub test_mode: TestMode,

    pub difficulty: Difficulty,

    pub custom_text: Option<String>,

    pub theme_type: ThemeType,

    pub font_style: FontStyle,

    pub repeat_test: bool,

    pub last_test_text: Option<String>,

    pub end_on_first_error: bool,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            test_mode: TestMode::Words(10),
            difficulty: Difficulty::Medium,
            custom_text: None,
            theme_type: ThemeType::Dark,
            font_style: FontStyle::Default,
            repeat_test: false,
            last_test_text: None,
            end_on_first_error: false,
        }
    }
}

impl Config {
    fn get_config_dir() -> Result<PathBuf> {
        let mut dir = dirs::config_dir().unwrap_or_else(|| PathBuf::from("."));
        dir.push("tuitype");
        if !dir.exists() {
            fs::create_dir_all(&dir)?;
        }
        Ok(dir)
    }

    fn get_config_path() -> Result<PathBuf> {
        let mut path = Self::get_config_dir()?;
        path.push("config.json");
        Ok(path)
    }

    pub fn save(&self) -> Result<()> {
        let path = Self::get_config_path()?;
        let serialized = serde_json::to_string_pretty(self)?;
        fs::write(path, serialized)?;
        Ok(())
    }

    pub fn load() -> Result<Self> {
        let path = Self::get_config_path()?;
        if path.exists() {
            let contents = fs::read_to_string(path)?;
            let config = serde_json::from_str(&contents)?;
            Ok(config)
        } else {
            let config = Self::default();
            config.save()?;
            Ok(config)
        }
    }
}

pub fn theme_name(theme_type: ThemeType) -> &'static str {
    match theme_type {
        ThemeType::Light => "Light",
        ThemeType::Dark => "Dark",
        ThemeType::Sepia => "Sepia",
        ThemeType::Matrix => "Matrix",
        ThemeType::Ocean => "Ocean",
    }
}

pub fn test_mode_name(mode: TestMode) -> String {
    match mode {
        TestMode::Timed(seconds) => format!("{} seconds", seconds),
        TestMode::Words(count) => format!("{} words", count),
        TestMode::Quote => "Quote".to_string(),
        TestMode::Custom => "Custom".to_string(),
    }
}

pub trait Theme {
    fn background(&self) -> (u8, u8, u8);
    fn text(&self) -> (u8, u8, u8);
    fn accent(&self) -> (u8, u8, u8);
    fn correct(&self) -> (u8, u8, u8);
    fn incorrect(&self) -> (u8, u8, u8);
    fn pending(&self) -> (u8, u8, u8);
    fn cursor(&self) -> (u8, u8, u8);
}
