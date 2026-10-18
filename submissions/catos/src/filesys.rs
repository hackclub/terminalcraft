use std::fs::{self, File, OpenOptions};
use std::io::{self, Read, Write};
use std::path::PathBuf;
use dirs::data_dir;

pub struct FileSys {
    pub root: PathBuf,
}

impl FileSys {
    pub fn new(app_name: &str) -> io::Result<Self> {
        let base_path = data_dir().ok_or_else(|| io::Error::new(io::ErrorKind::NotFound, "No data directory found"))?;
        let app_path = base_path.join(app_name);
        fs::create_dir_all(&app_path)?;
        Ok(Self { root: app_path })
    }

    pub fn create_file(&self, file_name: &str, content: &str) -> io::Result<()> {
        let path = self.root.join(file_name);
        let mut file = File::create(&path)?;
        file.write_all(content.as_bytes())?;
        //println!("File created: {:?}", path);
        Ok(())
    }

    pub fn read_file(&self, file_name: &str) -> io::Result<String> {
        let path = self.root.join(file_name);
        let mut file = File::open(&path)?;
        let mut content = String::new();
        file.read_to_string(&mut content)?;
        //println!("File read: {:?}", path);
        Ok(content)
    }

    pub fn modify_file(&self, file_name: &str, new_content: &str) -> io::Result<()> {
        let path = self.root.join(file_name);
        let mut file = OpenOptions::new().write(true).append(true).open(&path)?;
        file.write_all(new_content.as_bytes())?;
        //println!("File modified: {:?}", path);
        Ok(())
    }

    pub fn delete_file(&self, file_name: &str) -> io::Result<()> {
        let path = self.root.join(file_name);
        if path.exists() {
            fs::remove_file(&path)?;
            //println!("File deleted: {:?}", path);
            Ok(())
        } else {
            //println!("File not found: {:?}", path);
            Err(io::Error::new(io::ErrorKind::NotFound, "File not found"))
        }
    }

    pub fn create_folder(&self, folder_name: &str) -> io::Result<()> {
        let path = self.root.join(folder_name);
        fs::create_dir_all(&path)?;
        //println!("Folder created: {:?}", path);
        Ok(())
    }

    pub fn delete_folder(&self, folder_name: &str) -> io::Result<()> {
        let path = self.root.join(folder_name);
        if path.exists() {
            fs::remove_dir_all(&path)?;
            println!("Folder deleted: {:?}", path);
            Ok(())
        } else {
            println!("Folder not found: {:?}", path);
            Err(io::Error::new(io::ErrorKind::NotFound, "Folder not found"))
        }
        //Ok(())
    }

    pub fn print_contents(&self, dir_path: &str) -> io::Result<String> {
        let mut str_out = String::new();
        let path = self.root.join(dir_path);
        let entries = fs::read_dir(&path)?;
        for entry in entries {
            let entry = entry?;
            let path = entry.path();
            let name = path.file_name().unwrap().to_str().unwrap();
            let file_type = if path.is_dir() { "Folder" } else { "File" };
            str_out.push_str(&format!("{}: {}\n", file_type, name));
        }
        Ok(str_out)
    }
}