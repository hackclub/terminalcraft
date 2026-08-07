use std::{
    collections::HashMap,
    sync::{Arc, RwLock},
};
use tokio::sync::broadcast::{self, Sender};

pub const DEFAULT_CHANNEL_NAME: &str = "general";

struct Channel {
    pub tx: Sender<String>,
}

impl Channel {  
    pub fn new() -> Self {
        let (tx, _) = broadcast::channel(32);
        Self { tx }
    }
}

#[derive(Clone)]
pub struct Channels(Arc<RwLock<HashMap<String, Channel>>>);

impl Channels {
    pub fn new() -> Self {
        Self(Arc::new(RwLock::new(HashMap::new())))
    }

    pub fn join(&self, channel_name: &str) -> Sender<String> {
        if let Some(channel) = self.0.read().unwrap().get(channel_name) {
            return channel.tx.clone();
        }

        let mut write_guard = self.0.write().unwrap();
        write_guard
            .entry(channel_name.to_owned())
            .or_insert_with(Channel::new)
            .tx
            .clone()
    }
}
