// Main file for the chat client.
// KNOWN BUGS (FIXME) (More in other files):
//  - Backspace when arrow keys have been used previously is unpredictable.
//  - The client does not know when the user changes their name.

use std::io;
use std::io::Stdout;

use ratatui::{backend::CrosstermBackend, Terminal};
use tokio::net::TcpStream;
use tokio::sync::mpsc;
use tokio_util::codec::{FramedRead, FramedWrite, LinesCodec};
use futures::SinkExt;
use futures::StreamExt;
use crossterm::event::KeyCode;
use common::{decode_user_response, encode_message, decode_message, encode_user, User, Message};
use std::env;

use crate::{
    app::{App, AppResult},
    event::{Event, EventHandler},
    handler::handle_key_events,
    tui::Tui,
};

pub mod app;
pub mod event;
pub mod handler;
pub mod tui;
pub mod ui;


async fn get_username(tui: &mut Tui<CrosstermBackend<Stdout>>) -> AppResult<String> {
    let mut username = String::new();
    loop {
        tui.draw_username_input(&username)?;
        if let Event::Key(key_event) = tui.events.next().await? {
            match key_event.code {
                KeyCode::Enter => break,
                KeyCode::Char(c) => username.push(c),
                KeyCode::Backspace => { username.pop(); },
                _ => {}
            }
        }
    }
    Ok(username)
}


#[tokio::main]
async fn main() -> AppResult<()> {
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        println!("Usage: {} <SERVER IP>:<PORT>", args[0]);
        return Ok(());
    }

    let mut app = App::new();

    // TUI stuff -- not init, that is below
    let backend = CrosstermBackend::new(io::stdout());
    let terminal = Terminal::new(backend)?;
    let events = EventHandler::new(250);
    let mut tui = Tui::new(terminal, events);

    // Network stuff
    let tcp_stream = TcpStream::connect(&args[1]).await?;
    let (reader, writer) = tcp_stream.into_split();
    let mut reader = FramedRead::new(reader, LinesCodec::new());
    let mut writer = FramedWrite::new(writer, LinesCodec::new());

    let mut username: String;

    // The above is somewhat error-prone, so we only init the TUI here.
    // That way, if it fails, it doesn't mess up the terminal.
    tui.init()?;

    loop {
        username = get_username(&mut tui).await?;
        let user_requested = User { username: username.clone() };
        writer.send(&encode_user(&user_requested)).await?;

        let response = reader.next().await;
        if let Some(Ok(response)) = response {
            let status = decode_user_response(&response)?.status;
            if status == 1 {
                username.clear();
            } else if status == 0 {
                break;
            } else {
                tui.exit()?;
                println!("Expected status to equal 0 or 1 but got `{}` instead.", status);
            }
        }
    }
    let (tx, mut rx) = mpsc::channel(32);

    while app.running {
        tui.draw(&mut app)?;

        tokio::select! {
            event = tui.events.next() => {
                match event? {
                    Event::Tick => app.tick(),
                    Event::Key(key_event) => handle_key_events(key_event, &mut app, &tx)?,
                    Event::Mouse(_) => {},
                    Event::Resize(_, _) => {}
                }
            }
            Some(message) = reader.next() => {
                if let Ok(message) = message {
                    let decoded_message = decode_message(&message)?;
                    app.add_message(format!("<{}> {}", decoded_message.user.username, decoded_message.contents));
                }
            }
            Some(message) = rx.recv() => {
                writer.send(encode_message(&Message {
                    user: User {
                        username: username.clone(),
                    },
                    contents: message,
                    timestamp: 0,
                })).await?;
            }
        }
    }

    tui.exit()?;

    Ok(())
}
