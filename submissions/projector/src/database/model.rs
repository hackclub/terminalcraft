use std::path::Path;

use chrono::{NaiveDateTime, Utc};
use rusqlite::{params, Connection, Result};

use crate::state::languages::ProgrammingLanguage;

pub struct Project {
    pub id: i64,
    pub type_lang: ProgrammingLanguage,
    pub name: String,
    pub path: String,
    pub last_opened: Option<NaiveDateTime>,
    pub created_on: NaiveDateTime,
}

impl Project {
    pub fn new(type_lang: ProgrammingLanguage, name: String, path: &Path) -> Self {
        Project {
            id: 0, // Placeholder, SQLite will auto-increment
            type_lang,
            name,
            path: path.to_string_lossy().into_owned(),
            last_opened: None,
            created_on: Utc::now().naive_utc(),
        }
    }

    pub fn insert(&mut self, conn: &Connection) -> Result<()> {
        conn.execute(
            "INSERT INTO projects (type_lang, name, path, last_opened, created_on) VALUES (?1, ?2, ?3, ?4, ?5)",
            params![self.type_lang, self.name, self.path, self.last_opened, self.created_on],
        )?;
        self.id = conn.last_insert_rowid();
        Ok(())
    }
}
