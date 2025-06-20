use std::{env, env::temp_dir, fs, path::Path, process::Command};

use crate::{
    database::model::Project,
    state::languages::ProgrammingLanguage,
    ui::{grab_string::ask, yn},
};

pub fn setup(project_name: Option<&str>) {
    if env::var("FAKE_UNINSTALLED").is_ok() {
        return;
    }
    if !is_python_installed() {
        install_python().expect("Failed to install Python");
        return;
    }

    match project_name {
        Some(name) => {
            let path = Path::new(name);
            if !path.exists() {
                fs::create_dir(name).expect("Failed to create project directory");
            }
            let canonical_path = path.canonicalize().expect("Failed to get full path");
            println!("Project {} created successfully", name);
            if yn::ask("Create a virtual environment? (y/n)").unwrap_or(false) {
                let python_cmd = if cfg!(target_os = "windows") {
                    "python"
                } else {
                    "python3"
                };
                Command::new(python_cmd)
                    .arg("-m")
                    .arg("venv")
                    .arg("venv")
                    .arg("--upgrade-deps")
                    .current_dir(&canonical_path)
                    .status()
                    .expect("Failed to create virtual environment");
            }
            let main_path = canonical_path.join("main.py");
            fs::write(&main_path, include_str!("./pre-made-code/python/main.py"))
                .expect("Failed to create main.py");
            if yn::ask("Create requirements.txt? (y/n)").unwrap_or(false) {
                let requirements_path = canonical_path.join("requirements.txt");
                fs::write(&requirements_path, "").expect("Failed to create requirements.txt");
            }
            if yn::ask("Set up Git for this project? (y/n)").unwrap_or(false) {
                Command::new("git")
                    .arg("init")
                    .current_dir(&canonical_path)
                    .status()
                    .expect("Failed to init git repository");
                if yn::ask("Create a .gitignore file? (y/n)").unwrap_or(false) {
                    let gitignore_path = canonical_path.join(".gitignore");
                    fs::write(&gitignore_path, "venv/\n").expect("Failed to create .gitignore");
                }
            }
            let mut project = Project::new(
                ProgrammingLanguage::Python,
                name.to_string(),
                canonical_path.as_path(),
            );
            crate::post_setup::run_post_setup(&mut project).expect("Failed to run post setup");
        }
        None => {
            let answer = ask("Project name? (leave blank to use current directory)")
                .expect("Failed to get project name");

            if answer.trim().is_empty() {
                let path = Path::new(".");
                let canonical_path = path.canonicalize().expect("Failed to get full path");
                println!("Initialized current directory as a Python project");
                if yn::ask("Create a virtual environment? (y/n)").unwrap_or(false) {
                    let python_cmd = if cfg!(target_os = "windows") {
                        "python"
                    } else {
                        "python3"
                    };
                    Command::new(python_cmd)
                        .arg("-m")
                        .arg("venv")
                        .arg("venv")
                        .arg("--upgrade-deps")
                        .current_dir(&canonical_path)
                        .status()
                        .expect("Failed to create virtual environment");
                }
                let main_path = canonical_path.join("main.py");
                fs::write(&main_path, include_str!("./pre-made-code/python/main.py"))
                    .expect("Failed to create main.py");
                if yn::ask("Create requirements.txt? (y/n)").unwrap_or(false) {
                    let requirements_path = canonical_path.join("requirements.txt");
                    fs::write(&requirements_path, "").expect("Failed to create requirements.txt");
                }
                if yn::ask("Set up Git for this project? (y/n)").unwrap_or(false) {
                    Command::new("git")
                        .arg("init")
                        .current_dir(&canonical_path)
                        .status()
                        .expect("Failed to init git repository");
                    if yn::ask("Create a .gitignore file? (y/n)").unwrap_or(false) {
                        let gitignore_path = canonical_path.join(".gitignore");
                        fs::write(&gitignore_path, "venv/\n").expect("Failed to create .gitignore");
                    }
                }
                let mut project = Project::new(
                    ProgrammingLanguage::Python,
                    canonical_path
                        .file_name()
                        .unwrap()
                        .to_str()
                        .unwrap()
                        .to_string(),
                    canonical_path.as_path(),
                );
                crate::post_setup::run_post_setup(&mut project).expect("Failed to run post setup");
            } else {
                let path = Path::new(answer.trim());
                if !path.exists() {
                    fs::create_dir(answer.trim()).expect("Failed to create project directory");
                }
                let canonical_path = path.canonicalize().expect("Failed to get full path");
                println!("Project {} created successfully", answer.trim());
                if yn::ask("Create a virtual environment? (y/n)").unwrap_or(false) {
                    let python_cmd = if cfg!(target_os = "windows") {
                        "python"
                    } else {
                        "python3"
                    };
                    let status = std::process::Command::new(python_cmd)
                        .args(&["-m", "venv", "venv", "--upgrade-deps"])
                        .current_dir(&canonical_path)
                        .status()
                        .expect("Failed to create virtual environment");
                    if !status.success() {
                        eprintln!(
                            "Error: Creating the virtual environment failed (exit code: {:?})",
                            status.code()
                        );
                    }
                }

                let main_path = canonical_path.join("main.py");
                fs::write(&main_path, include_str!("./pre-made-code/python/main.py"))
                    .expect("Failed to create main.py");
                if yn::ask("Create requirements.txt? (y/n)").unwrap_or(false) {
                    let requirements_path = canonical_path.join("requirements.txt");
                    fs::write(&requirements_path, "").expect("Failed to create requirements.txt");
                }
                if yn::ask("Set up Git for this project? (y/n)").unwrap_or(false) {
                    Command::new("git")
                        .arg("init")
                        .current_dir(&canonical_path)
                        .status()
                        .expect("Failed to init git repository");
                    if yn::ask("Create a .gitignore file? (y/n)").unwrap_or(false) {
                        let gitignore_path = canonical_path.join(".gitignore");
                        fs::write(&gitignore_path, "venv/\n").expect("Failed to create .gitignore");
                    }
                }
                let mut project = Project::new(
                    ProgrammingLanguage::Python,
                    canonical_path
                        .file_name()
                        .unwrap()
                        .to_str()
                        .unwrap()
                        .to_string(),
                    canonical_path.as_path(),
                );
                crate::post_setup::run_post_setup(&mut project).expect("Failed to run post setup");
            }
        }
    }
}

fn is_python_installed() -> bool {
    if cfg!(target_os = "windows") {
        if let Ok(o) = std::process::Command::new("where").arg("python").output() {
            if o.status.success() && !String::from_utf8_lossy(&o.stdout).is_empty() {
                return true;
            }
        }
        if let Ok(o) = std::process::Command::new("where").arg("python3").output() {
            if o.status.success() && !String::from_utf8_lossy(&o.stdout).is_empty() {
                return true;
            }
        }
        if let Ok(local_appdata) = std::env::var("LOCALAPPDATA") {
            let path = std::path::Path::new(&local_appdata)
                .join("Microsoft")
                .join("WindowsApps")
                .join("python.exe");
            if path.exists() {
                return true;
            }
        }
        false
    } else if cfg!(target_os = "linux") {
        std::path::Path::new("/usr/bin/python3").exists()
    } else if cfg!(target_os = "macos") {
        unimplemented!("Python installation check for macOS is not implemented yet.");
    } else {
        eprintln!("Unsupported OS. Please install Python manually.");
        false
    }
}

fn install_python() -> color_eyre::Result<()> {
    println!("Python is not installed. Installing Python...");
    if cfg!(target_os = "windows") {
        // TODO: Find a better way to get the latest version of Python
        let installer_link = "https://www.python.org/ftp/python/3.13.2/python-3.13.2-amd64.exe";

        let temp_path = temp_dir().join("python-3.13.2-amd64.exe");
        let temp_path_str = temp_path
            .to_str()
            .expect("Failed to convert path to string");

        let output = Command::new("curl")
            .arg("-o")
            .arg(temp_path_str)
            .arg(installer_link)
            .output()
            .expect("Failed to download Python installer");
        if !output.status.success() {
            eprintln!(
                "Failed to download Python installer: {}",
                String::from_utf8_lossy(&output.stderr)
            );
            Ok(())
        } else {
            let output = Command::new(temp_path_str)
                .output()
                .expect("Failed to run Python installer");

            if !output.status.success() {
                eprintln!(
                    "Failed to run Python installer: {}",
                    String::from_utf8_lossy(&output.stderr)
                );
            } else {
                println!("Python installed successfully. Please relaunch the terminal.");
                if yn::ask("Would you like to remove the installer file? (y/n)").unwrap_or(false) {
                    fs::remove_file(temp_path_str).expect("Failed to remove Python installer");
                }
            }
            Ok(())
        }
    } else if cfg!(target_os = "linux") {
        println!("Please install Python using your package manager.");

        let output = Command::new("uname")
            .arg("-a")
            .output()
            .expect("Failed to get system information");
        if output.status.success() {
            let os_info = String::from_utf8_lossy(&output.stdout);
            match os_info.as_ref() {
                info if info.contains("Ubuntu") => {
                    println!("Installing Python on Ubuntu...");
                    Command::new("sudo")
                        .arg("apt-get")
                        .arg("install")
                        .arg("python3")
                        .status()
                        .expect("Failed to install Python on Ubuntu");
                }
                info if info.contains("Fedora") => {
                    println!("Installing Python on Fedora...");
                    Command::new("sudo")
                        .arg("dnf")
                        .arg("install")
                        .arg("python3")
                        .status()
                        .expect("Failed to install Python on Fedora");
                }
                info if info.contains("Arch") => {
                    println!("Installing Python on Arch...");
                    Command::new("sudo")
                        .arg("pacman")
                        .arg("-S")
                        .arg("python")
                        .status()
                        .expect("Failed to install Python on Arch");
                }
                _ => println!("Unsupported Linux distribution. Please install Python manually."),
            }
            Ok(())
        } else {
            eprintln!(
                "Failed to get system information: {}",
                String::from_utf8_lossy(&output.stderr)
            );
            Ok(())
        }
    } else if cfg!(target_os = "macos") {
        println!("Please install Python using Homebrew: brew install python");
        Ok(())
    } else {
        println!("Unsupported OS. Please install Python manually.");
        Ok(())
    }
}
