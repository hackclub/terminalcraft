# nix-sweeper
## A minesweeper clone written (almost) entirely in nix!

![image](https://github.com/user-attachments/assets/43b70d8a-3971-47c2-a4c8-a1ff712b5018)

### Running

First, if you haven't already, [install nix](https://github.com/DeterminateSystems/nix-installer)

```shell
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | \
  sh -s -- install
```

Once you're done, simply run

```shell
nix run github:dj-laser/nix-sweeper
```

After it compiles, it will start the minesweeper game!
Running it again will not recompile it, as it is saved to the nix store!

### Controls
- `WASD` and `Arrow Keys`: move cursor
- `F`: flag as mine
- `Space`: Reveal tile
- `R`: Reset board
- `Q`: Quit
