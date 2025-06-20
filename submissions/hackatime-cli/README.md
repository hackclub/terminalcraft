# hackatime-cli

Fire terminal-craft ysws submission

## Installation

Please check out the [Releases](https://github.com/tobycm/hackatime-cli/releases) page.

## Keybinds

- Press `q` anywhere to quit (except for the input prompt)
- Press `Enter` to submit the input
- Press `Space` or `k` to toggle pause the animation

## Build

### Prerequisites

- [Bun](https://bun.sh)

### Step 1: Install dependencies

```sh
bun install
```

### Step 2: Build

Build JS file:

```sh
bun build --minify --target=node index.tsx --outfile=hackatime-cli.js
```

Build JS file and bundle with Bun to make exe for your platform:

```sh
bun build --compile --outfile=hackatime-cli --minify index.tsx
```

For Windows:

```sh
bun build --compile --outfile=hackatime-cli --minify --target=bun-windows-amd64 index.tsx
```

For Linux:

```sh
bun build --compile --outfile=hackatime-cli --minify --target=bun-linux-amd64 index.tsx
```

For MacOS:

```sh
bun build --compile --outfile=hackatime-cli --minify --target=bun-darwin-arm64 index.tsx
```

## Development

Do step 1 of the build process

To run the program:

```sh
bun run start
```

With hot restart:

```sh
bun run dev
```
