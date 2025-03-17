use crate::post_setup;

use super::languages::ProgrammingLanguage;
use ratatui::widgets::ListState;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct Config {
    pub editor: post_setup::editor::ValidEditors,
    pub open_editor_after_setup: bool,
}

impl Default for Config {
    fn default() -> Self {
        Config {
            editor: post_setup::editor::ValidEditors::Code,
            open_editor_after_setup: false,
        }
    }
}

pub struct App {
    pub selected_lang: Option<ProgrammingLanguage>,
    pub selected_lang_index: usize,
    pub list_state: ListState,
    pub settings: Vec<Setting>,
    pub selected_setting_index: usize,
}

impl App {
    pub fn new() -> App {
        let mut list_state = ListState::default();
        list_state.select(Some(0));
        App {
            selected_lang: ProgrammingLanguage::all_langs().first().cloned(),
            selected_lang_index: 0,
            list_state,
            settings: vec![
                Setting::new("Editor", vec!["VSCode", "IntelliJ"]),
                Setting::new("Open After Setup", vec!["true", "false"]),
            ],
            selected_setting_index: 0,
        }
    }

    pub fn load_settings(&mut self) -> color_eyre::Result<()> {
        let cfg: Config = confy::load("projector", None)?;
        self.settings[0].selected_option_index = match cfg.editor {
            post_setup::editor::ValidEditors::Code => 0,
            post_setup::editor::ValidEditors::Intellij => 1,
        };
        self.settings[1].selected_option_index = if cfg.open_editor_after_setup { 1 } else { 0 };
        Ok(())
    }

    pub fn save_settings(&self) -> color_eyre::Result<()> {
        let editor = match self.settings[0].value() {
            "vscode" => post_setup::editor::ValidEditors::Code,
            "intellij" => post_setup::editor::ValidEditors::Intellij,
            _ => post_setup::editor::ValidEditors::Code,
        };
        let cfg = Config {
            editor,
            open_editor_after_setup: self.settings[1].value() == "true",
        };
        confy::store("projector", None, cfg)?;
        Ok(())
    }

    /// Moves down to the next available programming lang for the project.
    pub fn next_item(&mut self) {
        let all_langs = ProgrammingLanguage::all_langs();
        self.selected_lang_index = (self.selected_lang_index + 1) % all_langs.len();
        self.selected_lang = Some(all_langs[self.selected_lang_index].clone());
        self.list_state.select(Some(self.selected_lang_index));
    }

    /// Moves up to the previous available programming lang for the project. Circles back to the bottom if at the top.
    pub fn prev_item(&mut self) {
        let all_langs = ProgrammingLanguage::all_langs();
        if self.selected_lang_index == 0 {
            self.selected_lang_index = all_langs.len() - 1;
        } else {
            self.selected_lang_index -= 1;
        }
        self.selected_lang = Some(all_langs[self.selected_lang_index].clone());
        self.list_state.select(Some(self.selected_lang_index));
    }

    pub fn next_option(&mut self) {
        if let Some(setting) = self.settings.get_mut(self.selected_setting_index) {
            setting.next_option();
        }
    }

    pub fn prev_option(&mut self) {
        if let Some(setting) = self.settings.get_mut(self.selected_setting_index) {
            setting.prev_option();
        }
    }

    pub fn next_setting(&mut self) {
        self.selected_setting_index = (self.selected_setting_index + 1) % self.settings.len();
    }

    pub fn prev_setting(&mut self) {
        if self.selected_setting_index == 0 {
            self.selected_setting_index = self.settings.len() - 1;
        } else {
            self.selected_setting_index -= 1;
        }
    }
}

pub struct Setting {
    pub name: String,
    pub options: Vec<String>,
    pub selected_option_index: usize,
}

impl Setting {
    pub fn new(name: &str, options: Vec<&str>) -> Setting {
        Setting {
            name: name.to_string(),
            options: options.into_iter().map(String::from).collect(),
            selected_option_index: 0,
        }
    }

    pub fn next_option(&mut self) {
        self.selected_option_index = (self.selected_option_index + 1) % self.options.len();
    }

    pub fn prev_option(&mut self) {
        if self.selected_option_index == 0 {
            self.selected_option_index = self.options.len() - 1;
        } else {
            self.selected_option_index -= 1;
        }
    }

    pub fn value(&self) -> &str {
        &self.options[self.selected_option_index]
    }
}
