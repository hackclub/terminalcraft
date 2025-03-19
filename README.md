# Conway's Game of Life TUI in Rust

## Installation 

-   there are pre-built binaries for mainstream platforms: [releases](https://github.com/JeromeSchmied/cgol-tui-rs/releases/latest)

### having the [Rust toolchain](https://rustup.rs) installed
-   `cargo install cgol-tui`
-   `cargo install --locked --git "https://github.com/JeromeSchmied/cgol-tui-rs"`
-   clone the repo (`git clone https://github.com/jeromeschmied/cgol-tui-rs`) and run `cargo install --locked --path .`

## Usage

`cgol-tui --help`  

eg.:
-   `cgol-tui` run the app with builtin patterns
-   `curl https://conwaylife.com/patterns/fx153.cells | cgol-tui -` the `-` stands for `stdin`, run the app with the builtin patterns and the fx153 fetched with `curl`
-   `cgol-tui my_own_pattern.cells fx153.cells` run defaults and two more, own patterns

### Script

there is a [fish][fish-home] script provided under [scripts](./scripts/pattern.fish) for viewing patterns from [conwaylife.com][conway-patterns]</br>

see `fish scripts/pattern.fish --help`

#### needed tools

- [fish][fish-home]: shell
- [curl](https://curl.se/): download

## Sample

![Sample][1]

## Todos

-   [x] initial tui support
-   [x] renaming on gh
-   [x] error handling
-   [x] publishing on crates.io
-   [x] changing to `Canvas` for rendering viewer block
-   [x] the ability to parse `.cells` files, from [conwaylife.com][conway-patterns]
-   [x] display the names of patterns

## Acknowledgements

-   The core of this app is adapted from the [Rust-Wasm tutorial](https://rustwasm.github.io/docs/book/).
-   main dependencies:
    -   [ratatui](https://ratatui.rs): ui
    -   [crossterm](https://github.com/crossterm-rs/crossterm): ratatui backend

## License

Licensed under either of

-   Apache License, Version 2.0, ([LICENSE-APACHE](LICENSE_APACHE) or http://www.apache.org/licenses/LICENSE-2.0)
-   MIT license ([LICENSE-MIT](LICENSE_MIT) or http://opensource.org/licenses/MIT)

at your option.

### Contribution

Unless you explicitly state otherwise, any contribution intentionally
submitted for inclusion in the work by you, as defined in the Apache-2.0
license, shall be dual licensed as above, without any additional terms or
conditions.

[1]: assets/0.4.0.png "Image of using cgol-tui in Alacritty on Arch Linux btw"
[fish-home]: https://fishshell.com
[conway-patterns]: https://conwaylife.com/patterns/
