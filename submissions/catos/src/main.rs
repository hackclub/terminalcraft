mod consts;
mod catcaller;
mod filesys;

use consts::*;
use catcaller::Catcaller;
use std::{thread, time};
use crossterm::{cursor, execute, terminal};
use std::io::{self, Write};
use filesys::FileSys;
use regex::Regex;

fn cat_saying(msg: &str) {
    let mut stdout = io::stdout();
    execute!(stdout, terminal::Clear(terminal::ClearType::All)).unwrap();

    let mut displayed_text = String::new();
    let mut frame_index = 0;
    let mouth_change_interval = 2;

    for (i, ch) in msg.chars().enumerate() {
        displayed_text.push(ch);

        if i % mouth_change_interval == 0 {
            frame_index = 1 - frame_index;
        }

        execute!(stdout, cursor::MoveTo(0, 0)).unwrap();
        println!("{}", CAT_FRAMES[frame_index][0]);
        println!("{}", CAT_FRAMES[frame_index][1]);
        println!("{}", CAT_FRAMES[frame_index][2]);
        println!("~ {}", displayed_text);

        io::stdout().flush().unwrap();

        thread::sleep(time::Duration::from_millis(50));
    }

    execute!(stdout, cursor::MoveTo(0, 0)).unwrap();
    frame_index = 0;
    println!("{}", CAT_FRAMES[frame_index][0]);
    println!("{}", CAT_FRAMES[frame_index][1]);
    println!("{}", CAT_FRAMES[frame_index][2]);
    println!("~ {}", displayed_text);
    
}

fn get_input() -> String {
    let mut input = String::new();
    std::io::stdin().read_line(&mut input).expect("Failed to read line");
    input
}

fn func_locator(msg: &str) -> (String, Vec<String>) {
    let mut funcs = Vec::new();

    let re = Regex::new(r":::.*?:::").unwrap();
    for mat in re.find_iter(msg) {
        funcs.push(mat.as_str().to_string());
    }

    let mut processed_msg = msg.to_string();
    for func in funcs.clone() {
        processed_msg = processed_msg.replace(&func, "");
    }
    
    (processed_msg, funcs)
}

fn main() {
    let mut stdout = io::stdout();
    let mut catcaller = Catcaller::new();
    let filesys = FileSys::new("CatOS").unwrap();

    let mut prev_msgs: Vec<(String, String)> = Vec::new();

    cat_bootup_msg();
    cat_saying("CatOS is activated! What's up?");

    loop {
        println!();
        print!("You: "); stdout.flush().unwrap();
        let input = get_input();
        
        if input.trim().is_empty() {
            execute!(stdout, terminal::Clear(terminal::ClearType::All)).unwrap();
            print(CAT);
            continue;
        }

        prev_msgs.push(("user".to_string(), input.clone()));

        match catcaller.call_cat(input, None) {
            Ok(r) => {
                let json: serde_json::Value = serde_json::from_str(&r).unwrap();
                let sys_resp = json["choices"][0]["message"]["content"].as_str().unwrap();

                println!("RAW: {}", sys_resp);

                prev_msgs.push(("assistant".to_string(), sys_resp.to_string()));

                let process_resp = func_locator(sys_resp);
                
                let new_sys_resp = process_resp.0;
                let funcs = process_resp.1;

                cat_saying(&new_sys_resp);

                println!();

                for func in funcs {
                    let func_pseudoparsed = func.replace(":::", "").replace("[![", "|~|").replace("]!]", "");
                    let parts: Vec<&str> = func_pseudoparsed.split("|~|").collect();
                    
                    let func_name = parts[0].to_string();
                    let func_args: Vec<String> = if parts.len() > 1 { parts[1].split("<$>").map(|s| s.trim().to_string()).collect() } else { Vec::new() };

                    match &*func_name {
                        "exit" => {
                            cat_print("Goodbye!");
                            return;
                        },
                        "create_file" => {
                            if func_args.len() < 2 {
                                cat_error_print("Not enough arguments for create_file!");
                                continue;
                            }

                            let file_name = &func_args[0];
                            let content = &func_args[1];
                            match filesys.create_file(file_name, content) {
                                Ok(_) => cat_print(&format!("File created: {}", file_name)),
                                Err(e) => cat_error_print(&format!("File creation failed: {}", e))
                            }
                        },
                        "read_file" => {
                            if func_args.len() < 1 {
                                cat_error_print("Not enough arguments for read_file!");
                                continue;
                            }

                            let file_name = &func_args[0];
                            match filesys.read_file(file_name) {
                                Ok(content) => cat_print(&format!("File read: {}", content)),
                                Err(e) => cat_error_print(&format!("File read failed: {}", e))
                            }
                        },
                        "modify_file" => {
                            if func_args.len() < 2 {
                                cat_error_print("Not enough arguments for modify_file!");
                                continue;
                            }

                            let file_name = &func_args[0];
                            let new_content = &func_args[1];
                            match filesys.modify_file(file_name, new_content) {
                                Ok(_) => cat_print(&format!("File modified: {}", file_name)),
                                Err(e) => cat_error_print(&format!("File modification failed: {}", e))
                            }
                        },
                        "delete_file" => {
                            if func_args.len() < 1 {
                                cat_error_print("Not enough arguments for delete_file!");
                                continue;
                            }

                            let file_name = &func_args[0];
                            match filesys.delete_file(file_name) {
                                Ok(_) => cat_print(&format!("File deleted: {}", file_name)),
                                Err(e) => cat_error_print(&format!("File deletion failed: {}", e))
                            }
                        },
                        "create_folder" => {
                            if func_args.len() < 1 {
                                cat_error_print("Not enough arguments for create_folder!");
                                continue;
                            }

                            let folder_name = &func_args[0];
                            match filesys.create_folder(folder_name) {
                                Ok(_) => cat_print(&format!("Folder created: {}", folder_name)),
                                Err(e) => cat_error_print(&format!("Folder creation failed: {}", e))
                            }
                        },
                        "delete_folder" => {
                            if func_args.len() < 1 {
                                cat_error_print("Not enough arguments for delete_folder!");
                                continue;
                            }

                            let folder_name = &func_args[0];
                            match filesys.delete_folder(folder_name) {
                                Ok(_) => cat_print(&format!("Folder deleted: {}", folder_name)),
                                Err(e) => cat_error_print(&format!("Folder deletion failed: {}", e))
                            }
                        },
                        "print_contents" => {
                            if func_args.len() < 1 {
                                cat_error_print("Not enough arguments for print_contents!");
                                continue;
                            }

                            let dir_path = &func_args[0];
                            match filesys.print_contents(dir_path) {
                                Ok(contents) => cat_print(&format!("Contents of {}: {}", dir_path, contents)),
                                Err(e) => cat_error_print(&format!("Failed to print contents of {}: {}", dir_path, e))
                            }
                        },
                        _ => cat_error_print(&format!("Function not found: {}", func_name))
                    }
                    //return;
                }
            },
            Err(e) => {
                cat_error_print(&format!("~ meow meow meow- {}", e));
                continue;
            }
        }
    }
}
