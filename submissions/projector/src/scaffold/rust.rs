use std::env;
use std::fs;
use std::path::Path;
use std::process::Command;

use crate::database::model::Project;
use crate::state::languages::ProgrammingLanguage;
use crate::ui::{grab_string::ask, yn};

pub fn setup(project_name: Option<&str>) {
    if !is_tool_installed("rustc") || !is_tool_installed("cargo") {
        // Ask if they'd like to install Rust
        let choice = yn::ask("Rust is not installed. Would you like to install it? (y/n)")
            .expect("Failed to get user input");

        if choice {
            if cfg!(target_os = "windows") {
                let temp_dir = env::temp_dir().join("rustup_install");
                if temp_dir.exists() {
                    fs::remove_dir_all(&temp_dir)
                        .expect("Failed to remove existing temp directory");
                }
                fs::create_dir_all(&temp_dir).expect("Failed to create temp directory");

                let rustup_path = temp_dir.join("rustup-init.exe");
                let rustup_url = if cfg!(target_arch = "aarch64") {
                    "https://win.rustup.rs/aarch64"
                } else {
                    "https://win.rustup.rs/x86_64"
                };
                Command::new("curl")
                    .args(&["-o", rustup_path.to_str().unwrap(), rustup_url])
                    .status()
                    .expect("Failed to download rustup-init.exe");

                Command::new(rustup_path)
                    .status()
                    .expect("Failed to execute rustup-init.exe");

                fs::remove_dir_all(&temp_dir).expect("Failed to remove temp directory");
            } else {
                Command::new("sh")
                    .arg("-c")
                    .arg("curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh")
                    .status()
                    .expect("Failed to execute command to install Rust");
            }
            println!("Note: You will have to run the projector setup again due to new environment files. Please restart your terminal.");
        } else {
            println!("Exiting as Rust is not installed.");
        }
        return;
    }

    match project_name {
        Some(name) => {
            if name.trim().is_empty() {
                println!("Exiting as no project name was provided.");
                return;
            }
            if name == "." {
                let status = Command::new("cargo")
                    .arg("init")
                    .status()
                    .expect("Failed to execute cargo init");
                if !status.success() {
                    eprintln!("Failed to run cargo init in current directory");
                } else {
                    println!("Initialized current directory as a Rust project");
                    let project_path = env::current_dir()
                        .expect("Failed to get current directory")
                        .canonicalize()
                        .expect("Failed to get full path");
                    let project_name = project_path
                        .file_name()
                        .expect("Failed to get project name");
                    let mut project = Project::new(
                        ProgrammingLanguage::Rust,
                        project_name.to_str().unwrap().to_string(),
                        &project_path,
                    );
                    if let Err(e) = crate::post_setup::run_post_setup(&mut project) {
                        eprintln!("Post setup failed: {}", e);
                    }
                }
            } else {
                let output = Command::new("cargo")
                    .arg("new")
                    .arg(name)
                    .output()
                    .expect("Failed to execute cargo new");

                if !output.status.success() {
                    eprintln!("Error: {}", String::from_utf8_lossy(&output.stderr));
                } else {
                    println!("Project {} created successfully", name);
                    let project_path = Path::new(name)
                        .canonicalize()
                        .expect("Failed to get full path");
                    let project_name = project_path.file_name().unwrap().to_str().unwrap();
                    let mut project = Project::new(
                        ProgrammingLanguage::Rust,
                        project_name.to_string(),
                        project_path.as_path(),
                    );
                    if let Err(e) = crate::post_setup::run_post_setup(&mut project) {
                        eprintln!("Post setup failed: {}", e);
                    }
                }
            }
        }
        None => {
            let answer = ask("Project name? (use '.' to use current directory)")
                .expect("Failed to get project name");

            if answer.trim().is_empty() {
                println!("Exiting as no project name was provided.");
                return;
            }

            if answer.trim() == "." {
                let status = Command::new("cargo")
                    .arg("init")
                    .status()
                    .expect("Failed to execute cargo init");
                if !status.success() {
                    eprintln!("Failed to run cargo init in current directory");
                } else {
                    println!("Initialized current directory as a Rust project");
                    let project_path = env::current_dir()
                        .expect("Failed to get current directory")
                        .canonicalize()
                        .expect("Failed to get full path");
                    let project_name = project_path
                        .file_name()
                        .expect("Failed to get project name")
                        .to_str()
                        .expect("Failed to convert project name to string");
                    let mut project = Project::new(
                        ProgrammingLanguage::Rust,
                        project_name.to_string(),
                        &project_path,
                    );
                    if let Err(e) = crate::post_setup::run_post_setup(&mut project) {
                        eprintln!("Post setup failed: {}", e);
                    }
                }
            } else {
                let output = Command::new("cargo")
                    .arg("new")
                    .arg(answer.trim())
                    .output()
                    .expect("Failed to execute cargo new");

                if !output.status.success() {
                    eprintln!("Error: {}", String::from_utf8_lossy(&output.stderr));
                } else {
                    println!("Project {} created successfully", answer.trim());
                    let project_path = Path::new(answer.trim())
                        .canonicalize()
                        .expect("Failed to get full path");
                    let project_name = project_path.file_name().unwrap().to_str().unwrap();
                    let mut project = Project::new(
                        ProgrammingLanguage::Rust,
                        project_name.to_string(),
                        project_path.as_path(),
                    );
                    if let Err(e) = crate::post_setup::run_post_setup(&mut project) {
                        eprintln!("Post setup failed: {}", e);
                    }
                }
            }
        }
    }
}

fn is_tool_installed(tool: &str) -> bool {
    if env::var("FAKE_UNINSTALLED").is_ok() {
        return false;
    }
    Command::new(tool)
        .arg("--version")
        .output()
        .map(|output| output.status.success())
        .unwrap_or(false)
}
