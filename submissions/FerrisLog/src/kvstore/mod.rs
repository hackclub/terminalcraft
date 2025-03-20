use std::{
    collections::HashMap,
    fs::{self, create_dir, File},
    io::{BufRead, BufReader, Read, Seek, SeekFrom, Write},
    path::{Path, PathBuf},
    str::FromStr,
};
pub mod command;
pub mod error;

use chrono::Local;
use command::Command;
use error::{KvError, KvResult};
use tempfile::TempDir;

// Consts
const COMPACTION_THRESHOLD: u64 = 1024;

#[derive(Debug)]
pub struct KvStore {
    path: PathBuf,
    pub table: HashMap<String, u64>,
}

impl KvStore {
    pub fn new(path: PathBuf) -> KvStore {
        KvStore {
            path,
            table: HashMap::new(),
        }
    }
    pub fn nocompactionset(&mut self, key: String, val: String) -> KvResult<()> {
        let cmd = Command::set(key.clone(), val.clone());

        let mut f = File::options()
            .read(true)
            .append(true)
            .open(&self.path)
            .unwrap();

        let start_pos = f.seek(SeekFrom::End(0)).unwrap();
        let _ = serde_json::to_writer(&mut f, &cmd);
        let _ = f.write_all(b"\n");
        self.table.insert(key, start_pos);

        Ok(())
    }

    pub fn set(&mut self, key: String, val: String) -> KvResult<()> {
        let cmd = Command::set(key.clone(), val.clone());

        let mut f = File::options()
            .read(true)
            .append(true)
            .open(&self.path)
            .unwrap();

        let start_pos = f.seek(SeekFrom::End(0)).unwrap();
        let _ = serde_json::to_writer(&mut f, &cmd);
        let _ = f.write_all(b"\n");
        self.table.insert(key, start_pos);

        let size = fs::metadata(&self.path);

        let length = size.unwrap().len();

        if length > COMPACTION_THRESHOLD {
            let _ = self.compaction();
        }

        Ok(())
    }

    pub fn get(&self, key: String) -> KvResult<Option<String>> {
        let val = self.table.get(&key);
        match &val {
            Some(_) => (),
            None => return Ok(None),
        }

        let file = File::options().read(true).open(&self.path).unwrap();

        let mut f = BufReader::new(file);

        // Seek from val to the \n
        let _ = f.seek(SeekFrom::Start(*val.unwrap()));
        let mut line = String::new();
        let _ = f.read_line(&mut line);
        let res = serde_json::from_str::<Command>(&line.to_string());
        match res {
            Ok(re) => match re {
                Command::Set { key: _, val } => Ok(Some(val)),
                _ => Ok(None),
            },
            Err(_) => Err(KvError::ParseError),
        }
    }

    pub fn remove(&mut self, key: String) -> KvResult<()> {
        let cmd = Command::rm(key.clone());

        let mut f = File::options()
            .read(true)
            .append(true)
            .open(&self.path)
            .unwrap();

        let _ = serde_json::to_writer(&mut f, &cmd);
        let _ = f.write_all(b"\n");
        match self.table.remove(&key) {
            Some(_) => Ok(()),
            None => Err(KvError::RemoveError),
        }
    }

    pub fn open(path: impl Into<PathBuf> + AsRef<Path> + Copy) -> KvResult<KvStore> {
        let f = match File::open(path.into().join("log.txt")) {
            Ok(f) => f,
            Err(_) => {
                let _ = File::create(path.into().join("log.txt"));
                File::open(path.into().join("log.txt")).unwrap()
            }
        };
        let mut hash: HashMap<String, u64> = HashMap::new();
        let mut buffer = BufReader::new(&f);
        let mut pos = buffer.seek(SeekFrom::Start(0)).unwrap();

        loop {
            let mut line = String::new();

            let length = buffer.read_line(&mut line).unwrap();
            if length == 0 {
                break;
            }
            let res = serde_json::from_str::<Command>(&line.to_string());

            match res {
                Ok(re) => {
                    match re {
                        Command::Set { key, val: _ } => hash.insert(key, pos),
                        Command::Remove { key } => hash.remove(&key),
                    };
                }

                Err(_) => return Err(KvError::ParseError),
            }

            pos = buffer.seek(SeekFrom::Start(pos + length as u64)).unwrap();
        }

        // This is the error, cause recursive
        Ok(KvStore {
            path: path.into().join("log.txt"),
            table: hash,
        })
    }

    pub fn compaction(&mut self) -> KvResult<()> {
        let temp_dir = TempDir::new().expect("Unable to create temporary working directory");
        let mut store = KvStore::open(temp_dir.path()).unwrap();

        for key in self.table.keys() {
            let _ = store.nocompactionset(
                key.to_string(),
                self.get(key.to_string()).unwrap().unwrap().to_string(),
            );
        }

        let mut f = File::options()
            .read(true)
            .truncate(true)
            .write(true)
            .open(&self.path)
            .unwrap();

        let mut fr = File::options().read(true).open(&store.path).unwrap();

        self.table = store.table;

        let mut buffer = String::new();
        let _ = fr.read_to_string(&mut buffer);
        let _ = f.write_all(buffer.as_bytes());

        Ok(())
    }

    pub fn list_key(&mut self) {
        if self.table.is_empty() {
            println!("No key is found");
        }
        print!("Keys: ");
        for i in self.table.clone().into_keys() {
            print!("{}, ", i);
        }
    }

    pub fn count(&mut self) -> u32 {
        self.table.clone().into_keys().count() as u32
    }

    pub fn create_snapshot(&mut self) -> KvResult<PathBuf> {
        let binding = PathBuf::from_str("/").unwrap();
        let parent_dir = self.path.parent().unwrap_or(binding.as_ref());
        let cur_date: chrono::DateTime<chrono::Local> = Local::now();
        let mut f = File::options().read(true).open(&self.path).unwrap();

        let new_log_path: PathBuf = parent_dir.join("snapshots").join(format!(
            "log_{}.txt",
            cur_date.format("%Y-%m-%d_%H-%M-%S").to_string()
        ));

        let _ = create_dir(parent_dir.join("snapshots"));
        let _ = File::create(&new_log_path);

        let mut cur_f = File::options()
            .write(true)
            .truncate(true)
            .open(&new_log_path)
            .unwrap();

        let mut buffer = Vec::new();

        let _ = f.read_to_end(&mut buffer);

        let _ = cur_f.write_all(buffer.as_ref());

        Ok(new_log_path)
    }

    pub fn load_snapshot(&mut self, path: PathBuf) -> KvResult<()> {
        let mut f = File::options()
            .truncate(true)
            .write(true)
            .open(&self.path)
            .unwrap();

        let mut fr = File::options().read(true).open(path).unwrap();

        let mut buffer: Vec<u8> = Vec::new();

        let _ = fr.read_to_end(&mut buffer);

        let _ = f.write(&buffer);

        Ok(())
    }
}
