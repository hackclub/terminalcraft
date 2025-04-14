#[derive(Debug, serde::Serialize, serde::Deserialize)]
pub enum Command {
    Set { key: String, val: String },
    Remove { key: String },
}

impl Command {
    pub fn set(key: String, val: String) -> Command {
        Command::Set { key, val }
    }
    pub fn rm(key: String) -> Command {
        Command::Remove { key }
    }
}
