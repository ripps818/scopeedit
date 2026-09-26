# scopeedit

An editor for [ScopeBuddy](https://github.com/HikariKnight/ScopeBuddy) configs. It lists your per-game configs by game name instead of AppID and opens them in your editor. There's a terminal UI (`scopeedit`) and a GTK4 app (`scopeedit-gui`).

> **Note:** this project is vibecoded. It was written mostly with an AI coding assistant, and I've tested it on my own setup. Expect rough edges, and read the code before trusting it with anything important.

## Features

- Lists the configs in `~/.config/scopebuddy/AppID/` by game name. Names come from the Steam store API and are cached in `scopeedit.db`.
- Create a config by searching Steam for a game or by entering an AppID.
- Disable a config without deleting it: it's renamed to `<appid>.conf.disabled`. You can enable it again later.
- Edits the global configs (`scb.conf`, `common.conf` and so on) too.
- The GUI has a built-in editor with shell syntax highlighting and a resizable **Variables** panel with these tabs:
  - **ScopeBuddy**: `SCB_*` options.
  - **Proton**, **GE-Proton**, **Proton-CachyOS** and **Proton-EM**: the `PROTON_*` variables supported by the newest build of each that you have installed. They're read from the build's `proton` script when the GUI starts, so they stay current as the builds change.
  - **DXVK / VKD3D**: common DXVK, DXVK-NVAPI, VKD3D-Proton, low latency layer, Mesa and MangoHud variables.

## Requirements

- Python 3
- ScopeBuddy
- CLI: [`pick`](https://pypi.org/project/pick/) (`pip install --user pick`)
- GUI: GTK 4 and PyGObject (`python-gobject` on Arch, `python3-gobject` on Fedora)

## Install

```sh
make install                          # installs to ~/.local
sudo make install PREFIX=/usr/local   # system-wide
make uninstall                        # pass the same PREFIX you installed with
```

This installs `scopeedit` and `scopeedit-gui` into `$PREFIX/bin` and adds a **scopeedit** entry to your app menu. Make sure `~/.local/bin` is on your `PATH`.

You can also run `./scopeedit` or `./scopeedit-gui` straight from the repo.

## Usage

```sh
scopeedit        # terminal UI; arrow keys to move, Right on a game for Edit/Disable
scopeedit -d     # the same, with debug output
scopeedit-gui    # GTK app
```

The CLI opens files in the editor set under **Options**, or in `$EDITOR` if none is set (`nano` if neither is). scopeedit keeps its own settings in `~/.config/scopebuddy/scopeedit.json`.
