# cli
## What is this ?
this is the one cli with the useful tool like github checking or components and page (coming soon) tool 
## How to use
### Prerequisites

- [Bun](https://bun.sh)

### Step 1: Install dependencies

```sh
bun install
```

### Step 2: Build

Build JS file:

```sh
bun build --minify --target=node index.tsx --outfile=helper-cli.js
```

Build JS file and bundle with Bun to make exe for your platform:

```sh
bun build --compile --outfile=helper-cli --minify index.tsx
```

For Windows:

```sh
bun build --compile --outfile=helper-cli --minify --target=bun-windows-amd64 index.tsx
```

For Linux:

```sh
bun build --compile --outfile=helper-cli --minify --target=bun-linux-amd64 index.tsx
```

For MacOS:

```sh
bun build --compile --outfile=helper-cli --minify --target=bun-darwin-arm64 index.tsx
```

## Development

Do step 1 of the build process

To run the program:

```sh
bun run start
```

With hot restart (for dev only don't try this):

```sh
bun run dev
```

note: you can make the builded file can be run anywhere by this docs
[windows](https://stackoverflow.com/questions/4822400/register-an-exe-so-you-can-run-it-from-any-command-line-in-windows) or [macOs](https://stackoverflow.com/questions/41187657/excute-program-from-anywhere-in-terminal) or [linux](https://stackoverflow.com/questions/56981754/how-to-make-a-programme-executable-anywhere-in-the-shell)


**bun.js runtime needed**


## Important
- This cli tool depends on the [Components Repository](https://github.com/code-ga/helper-cli-tool-repository) so they need the internet to run

- If you have the good component feeling free to pr into the repository and i will merge that btw