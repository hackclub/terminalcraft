use lettre::{Message, SmtpTransport, Transport, transport::smtp::authentication::Credentials};
use std::io::{self, Write};


const CREDS_FILE: &str = "smtp_creds.json";

pub fn ask(phrase: &str) -> String {
    print!("{} ", phrase);
    io::stdout().flush().unwrap();

    let mut input = String::new();
    io::stdin().read_line(&mut input).unwrap();

    input.trim().to_string()
}

pub fn sendMail(to: &str, subject: &str, body: &str) -> Result<(), Box<dyn std::error::Error>> {
        let creds = read_creds();

        let email = Message::builder()
            .from(creds.smtp_username.parse().unwrap())
            .to(to.parse().unwrap())
            .subject(subject)
            .body(body.to_string())
            .unwrap();

        let creds = Credentials::new(creds.smtp_username.clone(), creds.smtp_password.clone());

        let mailer = SmtpTransport::relay(&creds.smtp_host)
            .unwrap()
            .port(creds.smtp_port)
            .credentials(creds)
            .build();

        match mailer.send(&email) {
            Ok(_) => println!("Email sent successfully."),
            Err(e) => eprintln!("Failed to send email: {e}"),
        }
    }
