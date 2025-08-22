use std::{env, process::Command};

pub fn is_tool_installed(tool: &str) -> bool {
    if env::var("FAKE_UNINSTALLED").is_ok() {
        return false;
    }
    Command::new(tool)
        .arg("--version")
        .output()
        .map(|output| output.status.success())
        .unwrap_or(false)
}
