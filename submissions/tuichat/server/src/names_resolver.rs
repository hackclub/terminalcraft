use std::{
    collections::HashSet,
    sync::{Arc, Mutex},
};

#[derive(Clone)]
pub struct Names(Arc<Mutex<HashSet<String>>>);

impl Names {
    pub fn new() -> Self {
        Self(Arc::new(Mutex::new(HashSet::new())))
    }
    // returns true if name was inserted.
    pub fn insert(&self, name: String) -> bool {
        let mut names = self.0.lock().unwrap();

        // The return value of the insertion command
        names.insert(name)
    }

    pub fn remove_name(&self, name: &str) -> bool {
        let mut names = self.0.lock().unwrap();
        names.remove(name)
    }
}
