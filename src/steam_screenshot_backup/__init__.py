#!/usr/bin/env python3
import binascii
import os
import json
import re
import struct
import vdf
import urllib.request
import shutil
import argparse
import tomllib

ap = argparse.ArgumentParser()
ap.add_argument("--config", nargs="?", help="The location of the config file", default="$HOME/.config/steam_screenshot_backup/config.toml")
opts = ap.parse_args()

CONFIG_FILE = os.path.expandvars(opts.config)

CONFIG_STEAM_USERID = ""
CONFIG_DEST = "$HOME/Pictures/Steam"
CONFIG_CACHE = "$HOME/.config/steam_screenshot_backup/namecache.tsv"

if os.path.isfile(CONFIG_FILE):
    with open(CONFIG_FILE, "rb") as f:
        conf = tomllib.load(f)
        CONFIG_STEAM_USERID = conf["Options"]["SteamUserID"]
        CONFIG_DEST = conf["Options"]["Destination"]
        CONFIG_CACHE = conf["Options"]["Cache"]

        print(f"Loaded config file {CONFIG_FILE}")
        print(f"Steam User ID: {CONFIG_STEAM_USERID}")
        print(f"Screenshot Destination: {os.path.expandvars(CONFIG_DEST)}")
        print(f"Name Cache: {os.path.expandvars(CONFIG_CACHE)}")
        print()
else:
    print(f"No config file at {opts.config}")
    print("Please add a config file, or specify the config file with --config option")
    exit()


STEAM_USERDATA = os.path.expandvars(f"$HOME/.local/share/Steam/userdata/{CONFIG_STEAM_USERID}")

SCREENSHOT_SRC = os.path.join(STEAM_USERDATA, "760/remote")
SCREENSHOT_DST = os.path.expandvars(CONFIG_DEST)

APPMANIFEST = os.path.expandvars("$HOME/.local/share/Steam/steamapps")
SHORTCUTS = os.path.join(STEAM_USERDATA, "config/shortcuts.vdf")

CACHE = os.path.expandvars(CONFIG_CACHE)

cache_data = {}
shortcuts_data = {}


def get_name(appid):
    # step 1: check cache
    if appid in cache_data:
        print(f"{appid} → {cache_data[appid]} (cache)")
        return cache_data[appid]

    # step 2: try app manifest:
    manifest_name = os.path.join(APPMANIFEST, f"appmanifest_{appid}.acf")
    if os.path.isfile(manifest_name):
        with open(manifest_name) as m:
            manifest_text = m.read()

            match = re.search(r'\t"name"\t+"(.*)"', manifest_text, re.MULTILINE)
            if match is not None:
                name = match.groups()[0]
                cache_data[appid] = name
                print(f"{appid} → {name} (manifest)")
                return name

    # step 3: try shortcuts (for non steam games)
    if appid in shortcuts_data:
        cache_data[appid] = shortcuts_data[appid]
        print(f"{appid} → {shortcuts_data[appid]} (shortcuts)")
        return shortcuts_data[appid]

    # step 4: check online
    res = urllib.request.urlopen(f"https://store.steampowered.com/api/appdetails?appids={appid}")
    body = json.load(res)
    if body[appid]["success"]:
        cache_data[appid] = body[appid]["data"]["name"]
        print(f"{appid} → {body[appid]["data"]["name"]} (api)")
        return body[appid]["data"]["name"]

    # step 5: fallback to id
    print(f"{appid} → unknown. please set manually")
    cache_data[appid] = appid
    return appid


def read_cache():
    if os.path.isfile(CACHE):
        with open(CACHE, "r") as f:
            for line in f.readlines():
                k, v = line.split("\t")
                cache_data[k] = v.rstrip()


def write_cache():
    with open(CACHE, "w") as f:
        for k, v in cache_data.items():
            f.write(f"{k}\t{v}" + os.linesep)


# https://gaming.stackexchange.com/a/386883
def read_shortcuts():
    with open(SHORTCUTS, "rb") as f:
        shortcuts = vdf.binary_load(f)

    root = shortcuts["shortcuts"]
    for shortcut in root.values():
        appid = shortcut.get("appid")
        name = shortcut.get("AppName")

        # https://github.com/ValvePython/vdf/issues/62#issuecomment-2371764316
        int32 = struct.Struct("<i")
        bin_appid = int32.pack(appid)
        hex_appid = binascii.hexlify(bin_appid).decode()

        reversed_hex = bytes.fromhex(hex_appid)[::-1].hex()
        long_appid = int(reversed_hex, 16) << 32 | 0x02000000
        # print(f"{long_appid} {name}")

        shortcuts_data[str(long_appid)] = name


def main():
    read_shortcuts()
    read_cache()

    if not os.path.isdir(SCREENSHOT_DST):
        os.mkdir(SCREENSHOT_DST)

    for folder in os.scandir(SCREENSHOT_SRC):
        if os.path.isdir(folder):
            bn = os.path.basename(folder)
            game_name = get_name(bn)

            for screenshot in os.scandir(os.path.join(folder, "screenshots")):
                folder_dest = os.path.join(SCREENSHOT_DST, game_name)
                if not os.path.isdir(folder_dest):
                    os.mkdir(folder_dest)

                if os.path.isfile(screenshot):
                    screenshot_fn = os.path.basename(screenshot)

                    screenshot_dest = os.path.join(folder_dest, screenshot_fn)
                    if not os.path.isfile(screenshot_dest):
                        print(f"Copied {screenshot_dest}")
                        shutil.copy2(screenshot, screenshot_dest)

    write_cache()


if __name__ == "__main__":
    main()
