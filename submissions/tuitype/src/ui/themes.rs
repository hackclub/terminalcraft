use crate::config::{Theme, ThemeConfig};
use serde::{Deserialize, Serialize};

/// Available theme types
#[derive(Clone, Copy, Debug, PartialEq, Serialize, Deserialize)]
pub enum ThemeType {
    Light,
    Dark,
    Sepia,
    Matrix,
    Ocean,
}

/// Light theme implementation
struct LightTheme;
impl Theme for LightTheme {
    fn background(&self) -> (u8, u8, u8) {
        (248, 248, 242)
    }
    fn text(&self) -> (u8, u8, u8) {
        (40, 42, 54)
    }
    fn accent(&self) -> (u8, u8, u8) {
        (80, 120, 200)
    }
    fn correct(&self) -> (u8, u8, u8) {
        (20, 150, 20)
    }
    fn incorrect(&self) -> (u8, u8, u8) {
        (220, 50, 50)
    }
    fn pending(&self) -> (u8, u8, u8) {
        (150, 150, 150)
    }
    fn cursor(&self) -> (u8, u8, u8) {
        (80, 120, 200)
    }
}

/// Dark theme implementation
struct DarkTheme;
impl Theme for DarkTheme {
    fn background(&self) -> (u8, u8, u8) {
        (30, 30, 40)
    }
    fn text(&self) -> (u8, u8, u8) {
        (248, 248, 242)
    }
    fn accent(&self) -> (u8, u8, u8) {
        (189, 147, 249)
    }
    fn correct(&self) -> (u8, u8, u8) {
        (80, 250, 123)
    }
    fn incorrect(&self) -> (u8, u8, u8) {
        (255, 85, 85)
    }
    fn pending(&self) -> (u8, u8, u8) {
        (150, 150, 160)
    }
    fn cursor(&self) -> (u8, u8, u8) {
        (255, 184, 108)
    }
}

/// Sepia theme implementation
struct SepiaTheme;
impl Theme for SepiaTheme {
    fn background(&self) -> (u8, u8, u8) {
        (251, 240, 217)
    }
    fn text(&self) -> (u8, u8, u8) {
        (93, 71, 50)
    }
    fn accent(&self) -> (u8, u8, u8) {
        (183, 110, 36)
    }
    fn correct(&self) -> (u8, u8, u8) {
        (76, 122, 40)
    }
    fn incorrect(&self) -> (u8, u8, u8) {
        (192, 52, 29)
    }
    fn pending(&self) -> (u8, u8, u8) {
        (180, 155, 130)
    }
    fn cursor(&self) -> (u8, u8, u8) {
        (183, 110, 36)
    }
}

/// Matrix theme implementation
struct MatrixTheme;
impl Theme for MatrixTheme {
    fn background(&self) -> (u8, u8, u8) {
        (10, 20, 10)
    }
    fn text(&self) -> (u8, u8, u8) {
        (30, 255, 30)
    }
    fn accent(&self) -> (u8, u8, u8) {
        (0, 220, 0)
    }
    fn correct(&self) -> (u8, u8, u8) {
        (0, 220, 0)
    }
    fn incorrect(&self) -> (u8, u8, u8) {
        (255, 70, 70)
    }
    fn pending(&self) -> (u8, u8, u8) {
        (30, 150, 30)
    }
    fn cursor(&self) -> (u8, u8, u8) {
        (200, 255, 200)
    }
}

/// Ocean theme implementation
struct OceanTheme;
impl Theme for OceanTheme {
    fn background(&self) -> (u8, u8, u8) {
        (10, 30, 52)
    }
    fn text(&self) -> (u8, u8, u8) {
        (220, 240, 255)
    }
    fn accent(&self) -> (u8, u8, u8) {
        (100, 200, 255)
    }
    fn correct(&self) -> (u8, u8, u8) {
        (120, 220, 232)
    }
    fn incorrect(&self) -> (u8, u8, u8) {
        (255, 107, 129)
    }
    fn pending(&self) -> (u8, u8, u8) {
        (120, 140, 180)
    }
    fn cursor(&self) -> (u8, u8, u8) {
        (180, 225, 255)
    }
}

pub fn get_theme(theme_type: ThemeType) -> ThemeConfig {
    match theme_type {
        ThemeType::Light => theme_to_config(&LightTheme),
        ThemeType::Dark => theme_to_config(&DarkTheme),
        ThemeType::Sepia => theme_to_config(&SepiaTheme),
        ThemeType::Matrix => theme_to_config(&MatrixTheme),
        ThemeType::Ocean => theme_to_config(&OceanTheme),
    }
}

fn theme_to_config<T: Theme>(theme: &T) -> ThemeConfig {
    ThemeConfig {
        background: theme.background(),
        text: theme.text(),
        accent: theme.accent(),
        correct: theme.correct(),
        incorrect: theme.incorrect(),
        pending: theme.pending(),
        cursor: theme.cursor(),
    }
}
