use std::{fs, io};

pub fn random() -> io::Result<usize> {
    let file_path = "/proc/sys/kernel/random/uuid";

    let random_uuid = fs::read_to_string(file_path);
    let random_uuid = match random_uuid {
        Ok(random_uuid) => random_uuid,
        Err(error) => {
            return Err(io::Error::new(
                error.kind(),
                format!("Could not read file {}: {:?}", file_path, error),
            ));
        }
    };

    let random_number = match usize::from_str_radix(&random_uuid[28..36], 16) {
        Ok(random_number) => random_number,
        Err(error) => {
            return Err(io::Error::new(
                io::ErrorKind::InvalidData,
                format!("Could parse random number from {}: {:?}", file_path, error),
            ));
        }
    };

    return Ok(random_number);
}
