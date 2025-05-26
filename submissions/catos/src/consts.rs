use std::{thread, time};

pub const CAT: &str = r#"
 /\_/\  
( o.o )
 > ^ <"#;
pub const CAT_FRAMES: [[&str; 3]; 2] = [[r#"
 /\_/\  "#,
r#"( o.o )"#,
r#" > ^ <"#], [r#"
 /\_/\  "#,
r#"( oOo )"#,
r#" > ^ <"#]];
//pub const CAT_ERROR: [&str; 3] = [r#"
// /\_/\  "#,
//r#"( x_x )"#,
//r#" > ^ <"#];

pub const FUNCTIONS: [&str; 8] = ["exit", "create_file(file_name, content)", "read_file(file_name)", "modify_file(file_name, new_content)", "delete_file(file_name)", 
                                  "create_folder(folder_name)", "delete_folder(folder_name)", "print_contents(dir_path)"];

pub fn cat_system_def() -> String {
    format!(
        "You are CatOS, a cute and funny cat-themed operating system. \
        You are here to help the user with their tasks, answer their questions, and run functions if asked.\n\
        To run a function, surround the function name with two colons, \
        If it takes parameters, place them in [![]!] seperated by <$>, i.e. like this: :::function_name[![val1<$>val2]!]:::\n
        You don't need to highlight the running of the function to the user (instances will be stripped from the responce)\
        Functions: [{}];",
        FUNCTIONS.join(", ")
    )
}

pub fn print(m: &str) {println!("{}", m);}
pub fn cat_print(m: &str) {
    print(r#" /\_/\ "#);
    print(&format!(r#"( o.o )  ~ {}"#, m));
    print(r#" > ^ <"#);
}
pub fn cat_error_print(m: &str) {
    print(r#" /\_/\ "#);
    print(&format!(r#"( x_x )  {}"#, m));
    print(r#" > ^ <"#);
}
pub fn cat_bootup_msg() {
    let delay = time::Duration::from_secs(1);
    
    println!(r#"
  /\_/\  
 ( z_z )  ~ Snooze...
  > ^ <
"#);
    thread::sleep(delay);
    
    println!(r#"
  /\_/\  
 ( O_o )  ~ Stretching...
  > ^ <
"#);
    thread::sleep(delay);
    
    println!(r#"
  /\_/\  
 ( ^_^ )  ~ CatOS activated!
  > ^ <
"#);

    thread::sleep(delay);
}