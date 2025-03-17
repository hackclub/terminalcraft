use std::env;
use std::fs;
use std::path::Path;
use std::process::Command;

use crate::database::model::Project;
use crate::state::languages::ProgrammingLanguage;
use crate::ui::{grab_string::ask, yn};
use crate::util::is_tool_installed;

pub fn setup(project_name: Option<&str>) {
    if !is_tool_installed("gcc") || !is_tool_installed("make") {
        let choice = yn::ask("GCC or Make is not installed. Would you like to install them? (y/n)")
            .expect("Failed to get user input");

        if choice {
            if cfg!(target_os = "windows") {
                let install_choice = ask("Would you like to install Visual Studio or manually set up MinGW/Cygwin? (vs/mingw)")
                    .expect("Failed to get user input");

                if install_choice.trim().eq_ignore_ascii_case("vs") {
                    let temp_dir = env::temp_dir().join("vs_install");
                    if temp_dir.exists() {
                        fs::remove_dir_all(&temp_dir)
                            .expect("Failed to remove existing temp directory");
                    }
                    fs::create_dir_all(&temp_dir).expect("Failed to create temp directory");

                    let vs_installer_path = temp_dir.join("vs_installer.exe");
                    Command::new("curl")
                        .args(&[
                            "-o",
                            vs_installer_path.to_str().unwrap(),
                            "https://c2rsetup.officeapps.live.com/c2r/downloadVS.aspx?sku=community&channel=Release&version=VS2022&source=VSLandingPage&cid=2030",
                        ])
                        .status()
                        .expect("Failed to download Visual Studio installer");

                    Command::new(vs_installer_path)
                        .status()
                        .expect("Failed to execute Visual Studio installer");

                    fs::remove_dir_all(&temp_dir).expect("Failed to remove temp directory");
                } else {
                    println!("Please manually set up MinGW or Cygwin for GCC and Make.");
                }
            } else {
                Command::new("sh")
                    .arg("-c")
                    .arg("sudo apt-get update && sudo apt-get install -y build-essential")
                    .status()
                    .expect("Failed to execute command to install GCC and Make");
            }
            println!("Note: You will have to run the projector setup again due to new environment files. Please restart your terminal.");
        } else {
            println!("Exiting as GCC or Make is not installed.");
        }
        return;
    }

    match project_name {
        Some(name) => {
            let path = Path::new(name)
                .canonicalize()
                .expect("Failed to get full path");
            fs::create_dir(name).expect("Failed to create project directory");
            println!("Project {} created successfully", name);
            let mut project =
                Project::new(ProgrammingLanguage::C, name.to_string(), path.as_path());
            crate::post_setup::run_post_setup(&mut project).expect("Failed to run post setup");
        }
        None => {
            let answer = ask("Project name? (leave blank to use current directory)")
                .expect("Failed to get project name");

            if answer.trim().is_empty() {
                let path = Path::new(".")
                    .canonicalize()
                    .expect("Failed to get full path");
                println!("Initialized current directory as a C project");
                let mut project = Project::new(
                    ProgrammingLanguage::C,
                    path.file_name().unwrap().to_str().unwrap().to_string(),
                    path.as_path(),
                );
                crate::post_setup::run_post_setup(&mut project).expect("Failed to run post setup");
            } else {
                let path = Path::new(answer.trim())
                    .canonicalize()
                    .expect("Failed to get full path");
                fs::create_dir(answer.trim()).expect("Failed to create project directory");
                println!("Project {} created successfully", answer.trim());
                let mut project = Project::new(
                    ProgrammingLanguage::C,
                    path.file_name().unwrap().to_str().unwrap().to_string(),
                    path.as_path(),
                );
                crate::post_setup::run_post_setup(&mut project).expect("Failed to run post setup");
            }
        }
    }
}
