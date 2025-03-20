use serde::{Serialize, Deserialize};
use serde_json::{to_string, from_str};
use serde_json::Result;

#[derive(Serialize, Deserialize, Debug, Eq, PartialEq)]
pub struct Message {
    pub user: User,
    pub contents: String,
    pub timestamp: u64,
}

#[derive(Serialize, Deserialize, Debug, Eq, PartialEq)]
pub struct User {
    pub username: String,
}

#[derive(Serialize, Deserialize, Debug, Eq, PartialEq)]
pub struct UsernameRequestResponse {
    pub status: u8,
}

pub fn encode_message(message: &Message) -> String {
    to_string(message).unwrap()
}

pub fn decode_message(data: &str) -> Result<Message> {
    let message: Message = from_str(data)?;
    Ok(message)
}

pub fn encode_user(user: &User) -> String {
    to_string(user).unwrap()
}

pub fn decode_user(data: &str) -> Result<User> {
    let user: User = from_str(data)?;
    Ok(user)
}

pub fn encode_user_response(response: &UsernameRequestResponse) -> String {
    to_string(response).unwrap()
}

pub fn decode_user_response(data: &str) -> Result<UsernameRequestResponse> {
    let response: UsernameRequestResponse = from_str(data)?;
    Ok(response)
}