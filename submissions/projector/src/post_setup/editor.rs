use serde::{Deserialize, Serialize};
use std::env;
use std::fs;
use std::path::Path;
use std::process::Command;

use crate::ui::{not_implemented_warning, yn};

#[derive(Debug, Serialize, Deserialize)]
pub enum ValidEditors {
    #[serde(rename = "vscode")]
    Code,
    #[serde(rename = "intellij")]
    Intellij,
}

#[derive(Debug, Serialize, Deserialize)]
struct Config {
    open_editor_after_setup: bool,
    editor: ValidEditors,
}

impl Default for Config {
    fn default() -> Self {
        Config {
            open_editor_after_setup: false,
            editor: ValidEditors::Code,
        }
    }
}

pub fn run_editor_setup(project_dir: &Path) -> color_eyre::Result<()> {
    let cfg: Config = confy::load("projector", None)?;
    println!("Config loaded: {:?}", cfg); // Debug print

    if !cfg.open_editor_after_setup {
        println!("Open editor after setup option is disabled.");
        return Ok(());
    }

    println!("Opening editor: {:?}", cfg.editor);

    match cfg.editor {
        ValidEditors::Code => {
            if !project_dir.exists() {
                eprintln!(
                    "Project directory does not exist: {}",
                    project_dir.display()
                );
                return Ok(());
            }

            let code_command = if cfg!(target_os = "windows") {
                "powershell"
            } else {
                "code"
            };

            let code_output = if cfg!(target_os = "windows") {
                std::process::Command::new(code_command)
                    .arg("-Command")
                    .arg("code --version")
                    .output()?
            } else {
                std::process::Command::new(code_command)
                    .arg("--version")
                    .output()?
            };

            let code_available = code_output.status.success();
            println!("VS Code available: {}", code_available); // Debug print

            if code_available {
                let output = if cfg!(target_os = "windows") {
                    std::process::Command::new(code_command)
                        .arg("-Command")
                        .arg(format!("code {}", project_dir.display()))
                        .output()
                        .expect("Failed to execute 'code' command")
                } else {
                    std::process::Command::new(code_command)
                        .arg(project_dir)
                        .output()
                        .expect("Failed to execute 'code' command")
                };

                if !output.status.success() {
                    eprintln!(
                        "Failed to open VS Code in directory: {}",
                        project_dir.display()
                    );
                } else {
                    println!("VS Code opened successfully."); // Debug print
                }
            } else {
                let choice =
                    yn::ask("VS Code is not installed. Would you like to install it? (y/n)")
                        .expect("Failed to get user input");
                if choice {
                    if cfg!(target_os = "windows") {
                        let temp_dir = env::temp_dir().join("vscode_install");
                        if temp_dir.exists() {
                            fs::remove_dir_all(&temp_dir)
                                .expect("Failed to remove existing temp directory");
                        }
                        fs::create_dir_all(&temp_dir).expect("Failed to create temp directory");

                        let vscode_installer_path = temp_dir.join("VSCodeSetup.exe");
                        Command::new("curl")
                            .args(&[
                                "-o",
                                vscode_installer_path.to_str().unwrap(),
                                "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user",
                            ])
                            .status()
                            .expect("Failed to download VS Code installer");

                        Command::new(vscode_installer_path)
                            .status()
                            .expect("Failed to execute VS Code installer");

                        fs::remove_dir_all(&temp_dir).expect("Failed to remove temp directory");
                    } else {
                        let hostname = hostname::get().unwrap_or_default();
                        match hostname.to_string_lossy().as_ref() {
                            "debian" | "ubuntu" => {
                                Command::new("sudo")
                                    .arg("apt")
                                    .arg("install")
                                    .arg("-y")
                                    .arg("code")
                                    .status()
                                    .expect("Failed to install VS Code using apt");
                            }
                            "fedora" => {
                                Command::new("sudo")
                                    .arg("dnf")
                                    .arg("install")
                                    .arg("-y")
                                    .arg("code")
                                    .status()
                                    .expect("Failed to install VS Code using dnf");
                            }
                            "arch" => {
                                Command::new("sudo")
                                    .arg("pacman")
                                    .arg("-S")
                                    .arg("--noconfirm")
                                    .arg("code")
                                    .status()
                                    .expect("Failed to install VS Code using pacman");
                            }
                            _ => {
                                println!("Please install VS Code using your package manager. For example:");
                                println!("Debian/Ubuntu: sudo apt install code");
                                println!("Fedora: sudo dnf install code");
                                println!("Arch: sudo pacman -S code");
                            }
                        }
                    }
                }
            }
        }
        _ => not_implemented_warning::show(format!(
            "Editor '{:?}' is not supported yet.",
            cfg.editor
        ))?,
    }

    Ok(())
}
