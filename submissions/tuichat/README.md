# TUIChat

_I know, yet another chat app made by me..._

Welcome to TUIChat! This is a fast (nope), memory safe, efficient (not actually), asynchonous, cross-platform chat program written in under 2000 lines of memory safe Rust and running entirely in your terminal. It has a custom server with a custom protocol (based off of Serde and JSON), and a client made with Ratatui. The async runtime used is the wonderful Tokio.

## Running
To run this project, start by cloning the repository or downloading a zip. Then, start the server by running `cargo run --bin server [ADDRESS:PORT]`. Then, run the client in another window with `cargo run --bin client [ADDRESS:PORT]`. Here is what it might look like to test it on your local machine.

Server:
```
cargo run --bin server localhost:6000
```
And for the client:
```
cargo run --bin client localhost:6000
```

## Notes
This project has several missing features, known major bugs, and security and performance issues. This was meant
to be a fun project where I could learn more about Tokio, and not a fully finished program.


## Resources
Below are some resources I found very helpful when designing TUIChat. No code was copied directly, but the closest project to my source is [this](https://github.com/pretzelhammer/rust-blog/blob/master/posts/chat-server.md) (also linked directly below).
 * https://github.com/pretzelhammer/rust-blog/blob/master/posts/chat-server.md
 * https://tokio.rs/tokio/tutorial
 * https://ratatui.rs/tutorials/hello-ratatui/