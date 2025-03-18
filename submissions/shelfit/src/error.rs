use thiserror::Error;

#[derive(Error, Debug)]
pub enum ShelfError {
    #[error("Database error: {0}")]
    Database(#[from] rusqlite::Error),
    #[error("Clipboard error: {0}")]
    Clipboard(#[from] arboard::Error),
    #[error("I/O error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Note not found")]
    NoteNotFound,
    #[error("Serialization error: {0}")]
    Serialization(#[from] serde_json::Error),
    #[error("Configuration error: {0}")]
    ConfigError(String),
}

pub type Result<T> = std::result::Result<T, ShelfError>;