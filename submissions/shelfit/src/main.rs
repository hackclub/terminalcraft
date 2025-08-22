use clap::{Parser, Subcommand};
use std::path::PathBuf;
use crate::error::Result;
use colored::Colorize;
mod db;
mod clipboard;
mod error;

#[derive(Parser)]
#[command(name = "shelfit")]
#[command(about = "Local knowledge base for notes and snippets", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Save a new note
    Save {
        content: String,
        url: Option<String>,
        #[arg(short, long)]
        tags: Option<String>,
    },
    /// List all notes
    List,
    /// Search notes
    Search {
        query: String,
    },
    /// Copy note to clipboard
    Copy {
        id: i64,
    },
    /// Delete a note
    Delete {
        id: i64,
    },
    /// Export notes to JSON
    Export {
        path: PathBuf,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();

    match cli.command {
        Commands::Save { content, url, tags } => {
            let id = db::save_note(&content, url.as_deref(), tags.as_deref())?;
            println!("Note saved with ID: {}", id);
        }
        Commands::List => {
            let notes = db::list_notes()?;
            for note in notes {
                println!(
                    "{} {} [{}]",
                    format!("{}.", note.id).blue().bold(),
                    note.content.green(),
                    note.tags.unwrap_or_default().yellow()
                );
                if let Some(url) = note.url {
                    println!("   URL: {}", url.cyan());
                }
            }
        }
        Commands::Search { query } => {
            let notes = db::search_notes(&query)?;
            if notes.is_empty() {
                println!("No notes found for query: {}", query.red());
            } else {
                for note in notes {
                    println!(
                        "{} {} [{}]",
                        format!("{}.", note.id).blue().bold(),
                        note.content.green(),
                        note.tags.unwrap_or_default().yellow()
                    );
                }
            }
        }
        Commands::Copy { id } => {
            let note = db::get_note(id)?;
            clipboard::copy_to_clipboard(&note.content)?;
            println!("Note {} copied to clipboard", id.to_string().green());
        }
        Commands::Delete { id } => {
            db::delete_note(id)?;
            println!("Note {} deleted", id.to_string().green());
        }
        Commands::Export { path } => {
            db::export_notes(&path)?;
            println!("Notes exported to {}", path.display().to_string().green());
        }
    }

    Ok(())
}