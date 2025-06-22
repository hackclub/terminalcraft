use crate::{ProcessScanner, ScannerDelegate};
use clap::builder::styling::{AnsiColor, Effects, Styles};
use std::{
    error::Error,
    fs,
    io::{BufRead, BufReader},
};

fn get_task_name(pid: u32) -> Result<String, Box<dyn Error>> {
    let path = format!("/proc/{}/comm", pid);
    let name = fs::read_to_string(&path)
        .map_err(|e| format!("Failed to read process name from {}: {}", path, e))?;
    Ok(name.trim().to_string())
}

fn get_base_address(pid: u32) -> Result<Option<u64>, Box<dyn Error>> {
    let maps_path = format!("/proc/{}/maps", pid);
    let file = fs::File::open(&maps_path)
        .map_err(|e| format!("Failed to open {}: {}", maps_path, e))?;
    
    let reader = BufReader::new(file);
    
    for line in reader.lines() {
        let line = line.map_err(|e| format!("Failed to read line from {}: {}", maps_path, e))?;
        
        let parts: Vec<&str> = line.split_whitespace().collect();
        if parts.len() >= 6 {
            let address_range = parts[0];
            let permissions = parts[1];
            let pathname = parts[5];
            
            if permissions.contains('x') && !pathname.starts_with('[') && !pathname.contains(".so") {
                if let Some(start_addr_str) = address_range.split('-').next() {
                    if let Ok(base_addr) = u64::from_str_radix(start_addr_str, 16) {
                        return Ok(Some(base_addr));
                    }
                }
            }
        }
    }
    
    Ok(None)
}

fn check_aslr_enabled() -> Result<bool, Box<dyn Error>> {
    let aslr_setting = fs::read_to_string("/proc/sys/kernel/randomize_va_space")
        .map_err(|e| format!("Failed to read ASLR setting: {}", e))?;
    
    let setting = aslr_setting.trim().parse::<u32>()
        .map_err(|e| format!("Failed to parse ASLR setting: {}", e))?;
    
    Ok(setting > 0)
}

impl ProcessScanner for ScannerDelegate {
    fn scan(&self, pid: u32) -> Result<(), Box<dyn Error>> {
        let name = get_task_name(pid)?;
        let aslr_enabled = check_aslr_enabled()?;
        let base_address = get_base_address(pid)?;

        let styles = Styles::styled()
            .header(AnsiColor::Blue.on_default() | Effects::BOLD)
            .literal(AnsiColor::White.on_default())
            .valid(AnsiColor::Green.on_default())
            .invalid(AnsiColor::Red.on_default());

        let pipe_style = styles.get_header();
        let white_style = styles.get_literal();
        let green_style = styles.get_valid();
        let red_style = styles.get_invalid();

        fn print_border(style: &clap::builder::styling::Style, content: &str) {
            println!("{}{}{}", style.render(), content, style.render_reset());
        }

        fn print_row(
            pipe_style: &clap::builder::styling::Style,
            value_style: &clap::builder::styling::Style,
            label: &str,
            value: &str,
        ) {
            print!("{}{}", pipe_style.render(), "│ ");
            print!("{:<19}", label);
            print!(" {}", pipe_style.render());
            print!("│ {}", value_style.render());
            print!("{:<36}", value);
            print!(
                "{} {}│{}",
                value_style.render_reset(),
                pipe_style.render(),
                pipe_style.render_reset()
            );
            println!();
        }

        print_border(
            &pipe_style,
            "┌─────────────────────┬──────────────────────────────────────┐",
        );
        print_border(
            &pipe_style,
            "│ Property            │ Value                                │",
        );
        print_border(
            &pipe_style,
            "├─────────────────────┼──────────────────────────────────────┤",
        );
        print_row(&pipe_style, &white_style, "Task Name", &name);
        print_row(
            &pipe_style,
            if aslr_enabled { &green_style } else { &red_style },
            "ASLR Enabled",
            &aslr_enabled.to_string(),
        );

        let base_address_value = match base_address {
            Some(addr) => format!("0x{:016x}", addr),
            None => "N/A".to_string(),
        };
        let base_address_style = match base_address {
            Some(_) => &white_style,
            None => &red_style,
        };
        print_row(
            &pipe_style,
            base_address_style,
            "Base Address",
            &base_address_value,
        );

        print_border(
            &pipe_style,
            "└─────────────────────┴──────────────────────────────────────┘",
        );

        Ok(())
    }
}