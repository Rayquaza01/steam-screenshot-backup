#!/usr/bin/env bash
echo "Installing python module"
pip install .

mkdir -p ~/.config/steam_screenshot_backup
cp -v config.toml ~/.config/steam_screenshot_backup

USER_IDS=$(ls -1q ~/.local/share/Steam/userdata/)
USER_ID_COUNT=$(echo "$USER_IDS" | wc -l)
USER_ID=$(echo "$USER_IDS" | head -n 1)

if test "$USER_ID_COUNT" -ne 1; then
    echo "Found multiple user ids! Using first one..."
    echo "$USER_ID"
fi

sed -i "s/<YOUR STEAM USER ID>/$USER_ID/" ~/.config/steam_screenshot_backup/config.toml

mkdir -p ~/.config/systemd/user

echo "Installing systemd service"
cp -v steam-screenshot-backup.service ~/.config/systemd/user
cp -v steam-screenshot-backup.timer ~/.config/systemd/user

systemctl --user daemon-reload
systemctl --user enable --now steam-screenshot-backup.timer
