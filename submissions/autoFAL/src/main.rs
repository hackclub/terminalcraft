use clap::{Args, Parser, Subcommand};

mod utils;

mod commands;

mod models;

#[derive(Parser)]
#[command(name = "autoFAL")]
#[command(about = "CLI tool to get reminded to take the train", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    Search,
    Smtp,
}

pub fn main() {
    let args = Cli::parse();
    match args.command {
        Commands::Search => {
            let id = utils::ask("Enter the ID of the train you want to Search for:");
            let action = utils::ask("Enter the action (fetch):");

            if action == "fetch" {
                // commands::Search::run(id);
            } else {
                println!("Unknown action: {}", action);
            }
        },
        Commands::Smtp => {
            commands::smtp::save_creds();
        }
    }
}


