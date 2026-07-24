use crate::game::DifficultySettings;
use std::{fs, io, path::PathBuf};

const CONFIG_FILE_NAME: &str = "mental_maths_settings.json";

// Returns the path to the config file in the current working directory.
fn get_config_path() -> Result<PathBuf, io::Error> {
    let mut path = std::env::current_dir()?;
    path.push(CONFIG_FILE_NAME);
    Ok(path)
}

pub fn save_settings(settings: &DifficultySettings) -> Result<(), Box<dyn std::error::Error>> {
    let path = get_config_path()?;
    let json = serde_json::to_string_pretty(settings)?;
    fs::write(path, json)?;
    Ok(())
}

pub fn load_settings() -> Result<DifficultySettings, Box<dyn std::error::Error>> {
    let path = get_config_path()?;
    if !path.exists() {
        // If config file doesn't exist, create and save default settings.
        let default_settings = DifficultySettings::default();
        if let Err(e) = save_settings(&default_settings) {
            eprintln!(
                "Couldn't save default settings to {}: {}",
                path.display(),
                e
            );
        }
        return Ok(default_settings);
    }
    let json = fs::read_to_string(path)?;
    let settings: DifficultySettings = serde_json::from_str(&json)?;
    Ok(settings)
}
