#!/usr/bin/env bash
echo "Installing python module"
pip install .

mkdir -p ~/.config/systemd/user

echo "Installing systemd service"
cp -v steam-screenshot-backup.service ~/.config/systemd/user
cp -v steam-screenshot-backup.timer ~/.config/systemd/user

systemctl --user daemon-reload
systemctl --user enable --now steam-screenshot-backup.timer
