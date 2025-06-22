use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct SmtpCreds {
    pub smtp_host: String,
    pub smtp_username: String,
    pub smtp_password: String,
    pub smtp_port: u16,
}