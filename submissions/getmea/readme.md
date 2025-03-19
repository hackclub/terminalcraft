# GetMeA

> Don't you just want to get a bun ?

![Automated installation of bun](assets/demo.gif)

> Only supports Linux!

GetMeA is an AI-powered software installer. It aims to combat the recent trend of not putting software into the distro-specific registries (looking at you, Deno or Bun :p), which leads to developers wasting their precious time googling ~~and getting sidetracked~~ the fricking `curl <someaddress> | sh` command.

Just run getmea and tell it what to install. It will use your system package manager if possible but fall back to searching the web for you and coming up with a plan. Because AI has proven itself to be extremely not reliable, you'll, of course, be asked for confirmation before it runs any commands to protect your highly customized Linux installation.

Planned features:

- Multiple concurrent research attempts
- Automatically search package registry to confirm AI's decision
- Automatically try to debug failed commands
- Replace crawl4ai due to it's giant dependency tree

## ~~Installation~~ Currently broken due to giant blob of dependencies from crawl4ai -> Please use the development setup

- Download the [latest build artifact](https://nightly.link/playlogo/GetMeA/workflows/nuitka.yaml/main/Linux%20build.zip) and unzip it:

```bash
wget -O linux_build.zip https://nightly.link/playlogo/GetMeA/workflows/nuitka.yaml/main/Linux%20build.zip && unzip -j linux_build.zip && rm linux_build.zip
```

- Run it: `./getmea.bin setup`
- Enjoy!

> Note: You might encounter this issue if your linux installation is not up-to-date: `/lib/x86_64-linux-gnu/libm.so.6: version 'GLIBC_2.38' not found`. Please manually run the python files or compile it on your machine.

## Development

```bash
# Recommended: Python 3.13

# Install deps
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Debug project
python src/main.py # <- Works!

# Compile project
nuitka src/main.py # Currently takes around 1 hour.... Need to find a better solution for crawl4ai
```

## Attribution

This product includes software developed by UncleCode (<https://x.com/unclecode>) as part of the Crawl4AI project (<https://github.com/unclecode/crawl4ai>).
