use std::{env::current_dir, path::PathBuf, process::exit, str::FromStr};

use clap::{Parser, Subcommand};
use ferris::kvstore::KvStore;

#[derive(Parser)]
#[command(version, about)]
struct Cli {
    #[command(subcommand)]
    command: Option<Commands>,
}

#[derive(Subcommand)]

enum Commands {
    #[allow(non_camel_case_types)]
    /// Set a key-value pair
    set { key: String, val: String },
    #[allow(non_camel_case_types)]
    /// Get the value for a key
    get { key: String },

    #[allow(non_camel_case_types)]
    /// Remove a key-value pair
    rm { key: String },

    #[allow(non_camel_case_types)]
    /// List all keys in the store
    list_key,

    #[allow(non_camel_case_types)]
    /// Count the number of keys in the store
    count,

    #[allow(non_camel_case_types)]
    /// Create a backup of the current database state
    create_snapshot,

    #[allow(non_camel_case_types)]
    /// Load a database from a snapshot file
    load_snapshot { path: String },
}

fn main() {
    let cli = Cli::parse();
    let mut store = KvStore::open(current_dir().unwrap().as_path()).unwrap();

    if cli.command.is_none() {
        Cli::parse_from(["kvs", "--help"]);
        return;
    }

    // Your implementation here
    match &cli.command.unwrap() {
        Commands::get { key } => {
            let val = store.get(key.to_string());
            match val.unwrap() {
                Some(d) => println!("{}", d),
                None => println!("Key not found"),
            }
        }
        Commands::rm { key } => {
            let res = store.remove(key.to_string());
            match res {
                Ok(_) => (),
                Err(_) => {
                    println!("Key not found");
                    exit(1);
                }
            }
            println!("Key removed succesfully");
        }
        Commands::set { key, val } => {
            let _ = store.set(key.to_string(), val.to_string());
            println!("Key set succesfully");
        }
        Commands::list_key => {
            store.list_key();
        }
        Commands::count => {
            println!("{}", store.count());
        }
        Commands::create_snapshot => {
            let snapshot_dir = store.create_snapshot();
            println!(
                "Snapshot Created at {}",
                snapshot_dir.unwrap().to_str().unwrap()
            );
        }
        Commands::load_snapshot { path } => {
            let pathb = PathBuf::from_str(path);
            match pathb {
                Ok(_) => (),
                Err(e) => {
                    println!("Path is invalid, error: {:?}", e);
                    println!("Path inputed {}", path);
                }
            }

            let _ = store.load_snapshot(pathb.unwrap());
            println!("Snapshot Loaded");
        }
    }
}
