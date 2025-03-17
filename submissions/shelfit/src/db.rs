use crate::error::{Result, ShelfError};
use chrono::{DateTime, Utc};
use rusqlite::{params, Connection};
use serde::Serialize;
use std::path::PathBuf;
use directories::ProjectDirs;

#[derive(Debug, Serialize)]
pub struct Note {
    pub id: i64,
    pub content: String,
    pub url: Option<String>,
    pub tags: Option<String>,
    #[serde(with = "chrono::serde::ts_seconds")]
    pub created_at: DateTime<Utc>,
}

pub fn init_db() -> Result<Connection> {
    let proj_dirs = ProjectDirs::from("", "", "shelfit")
        .ok_or(ShelfError::ConfigError("Could not find project directory".into()))?;
    let db_dir = proj_dirs.config_dir();
    std::fs::create_dir_all(db_dir)?;

    let db_path = db_dir.join("shelfit.db");
    let conn = Connection::open(db_path)?;

    conn.execute(
        "CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL,
            url TEXT,
            tags TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )",
        [],
    )?;

    Ok(conn)
}

pub fn save_note(content: &str, url: Option<&str>, tags: Option<&str>) -> Result<i64> {
    let conn = init_db()?;
    conn.execute(
        "INSERT INTO notes (content, url, tags) VALUES (?1, ?2, ?3)",
        params![content, url, tags],
    )?;
    Ok(conn.last_insert_rowid())
}

pub fn list_notes() -> Result<Vec<Note>> {
    let conn = init_db()?;
    let mut stmt = conn.prepare(
        "SELECT id, content, url, tags, created_at
        FROM notes ORDER BY created_at DESC"
    )?;

    let notes = stmt
        .query_map([], |row| {
            Ok(Note {
                id: row.get(0)?,
                content: row.get(1)?,
                url: row.get(2)?,
                tags: row.get(3)?,
                created_at: row.get(4)?,
            })
        })?
        .collect::<std::result::Result<Vec<_>, _>>()
        .map_err(ShelfError::Database)?;

    Ok(notes)
}

pub fn search_notes(query: &str) -> Result<Vec<Note>> {
    let conn = init_db()?;
    let mut stmt = conn.prepare(
        "SELECT id, content, url, tags, created_at
        FROM notes
        WHERE content LIKE ?1 OR tags LIKE ?1
        ORDER BY created_at DESC"
    )?;

    let search_term = format!("%{}%", query);
    let notes = stmt
        .query_map([search_term], |row| {
            Ok(Note {
                id: row.get(0)?,
                content: row.get(1)?,
                url: row.get(2)?,
                tags: row.get(3)?,
                created_at: row.get(4)?,
            })
        })?
        .collect::<std::result::Result<Vec<_>, _>>()
        .map_err(ShelfError::Database)?;

    Ok(notes)
}

pub fn delete_note(id: i64) -> Result<()> {
    let conn = init_db()?;
    let rows_affected = conn.execute(
        "DELETE FROM notes WHERE id = ?1",
        params![id],
    )?;

    if rows_affected == 0 {
        return Err(ShelfError::NoteNotFound);
    }

    Ok(())
}

pub fn export_notes(path: &PathBuf) -> Result<()> {
    let notes = list_notes()?;
    let json = serde_json::to_string_pretty(&notes)?;
    std::fs::write(path, json)?;
    Ok(())
}

pub fn get_note(id: i64) -> Result<Note> {
    let conn = init_db()?;
    let mut stmt = conn.prepare(
        "SELECT id, content, url, tags, created_at
        FROM notes WHERE id = ?1"
    )?;

    stmt.query_row([id], |row| {
        Ok(Note {
            id: row.get(0)?,
            content: row.get(1)?,
            url: row.get(2)?,
            tags: row.get(3)?,
            created_at: row.get(4)?,
        })
    })
        .map_err(|_| ShelfError::NoteNotFound)
}