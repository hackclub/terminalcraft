use std::fs;
use crate::models::smtpcreds::SmtpCreds;
use crate::utils::ask;

const CREDS_FILE: &str = "smtp_creds.json";

pub fn save_creds() {
    let creds = SmtpCreds {
        smtp_host: ask("SMTP Host:"),
        smtp_port: ask("SMTP Port:").parse().unwrap(),
        smtp_username: ask("Username:"),
        smtp_password: ask("Password:"),
    };
    fs::write(CREDS_FILE, serde_json::to_string_pretty(&creds).unwrap()).unwrap();
    println!("Credentials saved.");
}