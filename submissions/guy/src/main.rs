use std::env;
use std::fs;
use std::process::exit;
use std::path::{Path};
use dialoguer::{theme::ColorfulTheme, Select};

fn main() {
    let mut current_dir = std::env::current_dir().unwrap();

    loop {
        let (mut menu, ui) = getfiles(&current_dir);

        if ui {
            let selection = Select::with_theme(&ColorfulTheme::default())
                .default(0)
                .items(&menu[..])
                .interact()
                .unwrap();

            if menu[selection] == "🚪: exit".to_string() {
                break;
            }
            else if menu[selection] == "⇦: ..".to_string() {
                if let Some(parent_dir) = current_dir.parent() {
                    current_dir = parent_dir.to_path_buf();
                }
            }
            else if menu[selection].chars().next() == Some('📁') {
                current_dir.push(&menu[selection].chars().skip(3).collect::<String>());
            }
        } else {
            menu.remove(0);
            menu.remove(0);
            for item in menu {
                println!("{}", item)
            }
            break;
        }
    }
}

fn getfiles(current_dir: &Path) -> (Vec<String>, bool) {
    let mut dirs: Vec<String> = vec![];
    let mut files: Vec<String> = vec![];
    let mut menu: Vec<String> = vec!["🚪: exit".to_string(), "⇦: ..".to_string()];
    let mut ui: bool = true;

    println!("Current directory: {}", current_dir.display());

    if let Ok(entries) = fs::read_dir(current_dir) {
        for entry in entries {
            if let Ok(entry) = entry {
                if let Some(file_name) = entry.file_name().to_str() {
                    if entry.file_type().unwrap().is_file() {
                        files.push(format!("📄: {}", file_name));
                    } else if entry.file_type().unwrap().is_dir() {
                        dirs.push(format!("📁: {}", file_name));
                    }
                }
            }
        }
    }

    let args: Vec<String> = env::args().collect();
    if args.len() != 1 {
        if args[1] == "dir" {
            for item in dirs {
                menu.push(item);
            }
        } else if args[1] == "fil" {
            for item in files {
                menu.push(item);
            }
        } else if args[1] == "noui" {
            ui = false;
            for item in dirs {
                menu.push(item);
            }
            for item in files {
                menu.push(item);
            }
        } else {
            println!("command not found");
            exit(1);
        }
    } else {
        for item in dirs {
            menu.push(item);
        }
        for item in files {
            menu.push(item);
        }
    }

    (menu, ui)
}
