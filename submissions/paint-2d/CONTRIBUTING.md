# Contributing to Paint 2D

## Cross-compilation

We use [`cross`](https://github.com/cross-rs/cross) to build the app for different platforms. Follow their instructions to install it, and then build the app for the desired platform, e.g.

```bash
cross build --release --target aarch64-unknown-linux-gnu
```

Building for macOS targets requires some [convoluted steps](https://github.com/cross-rs/cross-toolchains#apple-targets) to be followed if you're not using a macOS device (blame Apple licences).

## Tested terminals

Here's a list of terminals that Paint 2D has been tested in. Please test the app on your own platforms and favourite terminals so that the results can be added to the list, and any compatibility issues fixed!

### Linux

- ✅ Xfce Terminal Emulator
  - Subjectively looks the nicest in this one
- ✅ Konsole
- ✅ Visual Studio Code integrated terminal
- ✅ Kitty

### Windows

- ✅ Default Windows console
- ❌ WINE console
  - Doesn't seem to support ANSI escape codes

### macOS

- ✅ macOS Terminal
