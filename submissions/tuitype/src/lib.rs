use anyhow::Result;

pub mod config;
pub mod input;
pub mod stats;
pub mod text;
pub mod ui;
pub mod util;

pub type AppResult<T> = Result<T>;

pub use config::Config;
pub use stats::TypingStats;
pub use text::TextSource;
pub use ui::App;
