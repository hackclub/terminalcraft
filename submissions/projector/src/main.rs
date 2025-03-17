use clap::{Parser, Subcommand};
use std::io::{self, Write};
use std::process::Command;
use ui::{interactive_setup, not_implemented_warning, settings, yn};

mod database;
mod post_setup;
mod scaffold;
mod state;
mod ui;
pub mod util;

#[derive(Parser)]
#[command(name = "projector")]
#[command(about = "Projector CLI")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    New {
        lang: Option<String>,
        project_name: Option<String>,
    },
    Settings,
    Gallery,
    Add,
    Clear,
}

fn main() -> color_eyre::Result<()> {
    let cli = Cli::parse();

    match &cli.command {
        Commands::New { lang, project_name } => {
            if lang.is_none() {
                interactive_setup::show()?;
                return Ok(());
            }
            if lang.as_deref() != Some("rust") {
                not_implemented_warning::show(format!(
                    "Scaffolding for language '{}' is not implemented yet.",
                    lang.as_deref().expect("Language is required")
                ))?;
                return Ok(());
            }
            let name = match project_name {
                Some(n) => n.trim().to_string(),
                None => {
                    print!("Project name? (press Enter to use current directory): ");
                    io::stdout().flush()?;
                    let mut input = String::new();
                    io::stdin().read_line(&mut input)?;
                    input.trim().to_string()
                }
            };
            if name.is_empty() {
                let status = Command::new("cargo").arg("init").status()?;
                if !status.success() {
                    eprintln!("Failed to run cargo init in current directory");
                }
            } else {
                std::fs::create_dir_all(&name)?;
                let status = Command::new("cargo")
                    .args(["init", "--name", &name, &name])
                    .status()?;
                if !status.success() {
                    eprintln!("Failed to run cargo init");
                }
            }
        }
        Commands::Settings => {
            settings::show()?;
            let file_path = confy::get_configuration_file_path("projector", None)?;
            let file_path_str = file_path.to_string_lossy().replace("\\", "/");
            println!("Settings stored at: {:?}", file_path_str);
        }
        Commands::Gallery => {
            ui::gallery::show()?;
        }
        Commands::Add => {
            println!("Add command is not implemented yet.");
        }
        Commands::Clear => {
            if yn::ask("Are you sure you want to clear the database?")? {
                database::manage::clear()?;
            } else {
                println!("Aborted clearing the database.");
            }
        }
    }

    Ok(())
}
