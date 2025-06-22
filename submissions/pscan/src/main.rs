use clap::Parser;
use std::env::consts;

mod delegates;

#[derive(Parser)]
#[command(name = "pscan")]
#[command(about = "Retrieves important information about the target process")]
#[command(disable_version_flag = true)]
struct Cli {
    #[arg(short, long, help = "Process ID to scan")]
    pid: Option<u32>,

    #[arg(short = 'v', long, help = "Show version information")]
    version: bool,
}

trait ProcessScanner {
    fn scan(&self, pid: u32) -> Result<(), Box<dyn std::error::Error>>;
}

pub(crate) struct ScannerDelegate;

impl ScannerDelegate {
    fn version(&self) -> Result<(), Box<dyn std::error::Error>> {
        println!(
            "pscan {} ({} {})",
            env!("CARGO_PKG_VERSION"),
            consts::ARCH,
            consts::OS
        );
        Ok(())
    }
}

fn main() {
    let cli = Cli::parse();
    let scanner = ScannerDelegate;

    let result = if cli.version {
        scanner.version()
    } else if let Some(pid) = cli.pid {
        scanner.scan(pid)
    } else {
        eprintln!("Error: Process ID is required");
        std::process::exit(1);
    };

    if let Err(e) = result {
        eprintln!("Error: {}", e);
        std::process::exit(1);
    }
}