use std::fs;
use lettre::{Message, SmtpTransport, Transport, transport::smtp::authentication::Credentials};
use std::io::{self, Write};
use crate::models::smtpcreds::SmtpCreds;

const CREDS_FILE: &str = "smtp_creds.json";

pub fn ask(phrase: &str) -> String {
    print!("{} ", phrase);
    io::stdout().flush().unwrap();

    let mut input = String::new();
    io::stdin().read_line(&mut input).unwrap();

    input.trim().to_string()
}

fn read_creds() -> SmtpCreds {
    let data = fs::read_to_string(CREDS_FILE).unwrap();
    serde_json::from_str(&data).unwrap()
}

fn send_mail(to: &str, subject: &str, body: &str) -> Result<(), Box<dyn std::error::Error>> {
    let creds: SmtpCreds = crate::utils::read_creds();

    let email = Message::builder()
        .from(creds.smtp_username.parse()?)
        .to(to.parse()?)
        .subject(subject)
        .body(body.to_string())?;

    let smtp_creds = Credentials::new(creds.smtp_username.clone(), creds.smtp_password.clone());

    let mailer = SmtpTransport::relay(&creds.smtp_host)?
        .port(creds.smtp_port)
        .credentials(smtp_creds)
        .build();

    mailer.send(&email)?;
    Ok(())
}