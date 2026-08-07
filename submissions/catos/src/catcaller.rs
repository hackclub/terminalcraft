use reqwest::Client;
use serde_json::json;
use tokio;

use crate::consts::cat_system_def;

pub struct Catcaller {
    client: Client
}

impl Catcaller {
    pub fn new() -> Self {
        Catcaller {
            client: Client::new()
        }
    }

    #[tokio::main]
    pub async fn call_cat(&mut self, user_content: String, sys_content: Option<String>) -> Result<String, reqwest::Error> {
        let response = self.client.post("https://ai.hackclub.com/chat/completions")
            .header("Content-Type", "application/json")
            .json(&json!({
                "messages": [
                    {
                        "role": "system",
                        "content": sys_content.unwrap_or(cat_system_def().to_string())
                    },

                    { 
                        "role": "user", 
                        "content": user_content
                    }
                ]
            }))
            .send()
            .await?
            .text()
            .await?;
        
        Ok(response)
    }
}