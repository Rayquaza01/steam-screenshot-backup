# Steam Screenshot Backup

Backup your Steam screenshots to a separate location, and convert the appids into a readable name

Steam stores its screenshots in `~/.local/share/Steam/userdata/<STEAM USERID>/760/remote`, with each subfolder from there corresponding to an appid for a game. While you *could* copy this folder directly, it is difficult to tell what folder corresponds to which game (unless you memorize each appid). This tool maps each appid to the name of the game before copying, making it more convenient to browse your screenshots.

# Installation

## Automatic

To install Steam Screenshot Backup, simply run `install.sh` from this repo. This will set up the python script, config file, and systemd timer all in one.

```bash
git clone https://github.com/Rayquaza01/steam-screenshot-backup
cd steam-screenshot-backup
./install.sh
```


## Manual

### Python

To install the Python script:

```bash
pip install .
```

The executable script should be installed as `~/.local/bin/steam-screenshot-backup`. The script expects the config file (`config.toml`) to be at `~/.config/steam_screenshot_backup/config.toml` by default.

### Systemd Timer

To install the systemd timer, copy the `.service` and `.timer` file to `~/.config/systemd/user/`.

```bash
cp steam-screenshot-backup.service ~/.config/systemd/user
cp steam-screenshot-backup.timer ~/.config/systemd/user
```

Then, to enable the timer, run:

```bash
systemctl --user daemon-reload
systemctl --user enable --now steam-screenshot-backup.timer`
```

If you want to disable it, you can run:

```bash
systemctl --user stop steam-screenshot-backup.timer
systemctl --user disable steam-screenshot-backup.timer
```

Examples for setting the timer to run every hour, every half hour, and every 15 minutes are included in the timer file. Every 15 minutes is the default.

# Usage

If installed with default settings, the script will run automatically in the background every 15 minutes, copying your Steam screenshots to `~/Pictures/Steam`.

To run manually, simply run `steam-screenshot-backup` (or, if you're feeling fancy, `systemctl --user start steam-screenshot-backup.service`)

You can specify a different config file with the `--config` option.

## Config File

The config file has 3 main options:

### `SteamUserID`

Your Steam User ID. If you use the install script, this should be determined automatically. To find it manually: check `~/.local/share/Steam/userdata`. If you only have one Steam account set up on your system, there should only be one folder, and its name will be your user ID.

This script only handles one account at a time. If you have multiple Steam accounts you want to back up screenshots for, you should make an additional config file for the other account, and run the script with the `--config` option.

### `Destination`

This is where your screenshots will be copied to. Defaults to `~/Pictures/Steam`.

### `Cache`

This is a file that caches previous name lookups. Defaults to `~/.config/steam_screenshot_backup/namecache.tsv`. You *probably* don't want to change this.

Since non-Steam game appids are account and installation specific, you *probably* shouldn't use this file on multiple computers/with multiple Steam accounts. There could be collisions with non-Steam games. (Haven't tested that, so no idea how likely that actually is...)
