#!/usr/bin/env python3

import os
import sys
import argparse
import base64

from pathlib import Path
from typing import overload, Literal
from subprocess import run, PIPE

import jinja2

THISDIR=Path(__name__).parent.resolve()

@overload
def _read(path, *, binary: Literal[True]) -> bytes: ...
@overload
def _read(path, *, binary: Literal[False]) -> str: ...
@overload
def _read(path) -> str: ...

def _read(path: os.PathLike, *, binary=False):
    if binary:
        with open(path, "rb") as f:
            return f.read()
    else:
        with open(path) as f:
            return f.read()

SCRIPT_TEMPLATE = _read(THISDIR / "setup.sh.in")

def read_units():
    units = []
    patterns = ["**/*.service", "**/*.socket", "**/*.timer", "**/*.conf"]
    root = THISDIR / "systemd"
    for pat in patterns:
        for unit in root.rglob(pat):
            content = _read(unit)
            file = unit.relative_to(root)
            units.append({"file": file, "content": content})
    return units

def read_nm():
    cfgs = []
    for cfg in (THISDIR/"NetworkManager").glob("*.nmconnection"):
        cfgs.append({"file": cfg.name, "content": _read(cfg)})
    return cfgs

def read_rclone(nm: str):
    res = run(["rclone", "config", "show", nm], stdout=PIPE, check=True)
    return res.stdout.decode()

def read_mplayer_conf():
    return _read(THISDIR / "mplayer" / "config.toml")
def read_mplayer_sched():
    return _read(THISDIR / "mplayer" / "schedule.toml")

def populate_resources(enabled: bool):
    if not enabled:
        return []
    out = []
    for resource in (THISDIR/"resources").glob("*"):
        b64 = base64.b64encode(_read(resource, binary=True))
        out.append({"file": resource.name, "data": b64.decode()})
    return out


def parse_cli() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--ssid", help="WLAN SSID. Set to '' to disable", required=True)
    p.add_argument("--wifi-pw", help="WLAN password. Set to empty to disable")
    p.add_argument("--plai", help="Plai reference to compile and install. Set to empty to disable.", required=True)
    p.add_argument("--mplayer", help="Mplayer reference to install. Set to empty to disable.", required=True)
    p.add_argument("--rclone", help="Name of the rclone config to use. Set to empty to disable", required=True)
    p.add_argument("--resources", action=argparse.BooleanOptionalAction, default=True, help="Embed resources into the setup script")
    ns = p.parse_args()
    if ns.ssid and ns.wifi_pw is None:
        raise ValueError("WIFI password required. Set to empty to disable")
    return ns

def main():
    units = read_units()
    tmpl = jinja2.Template(SCRIPT_TEMPLATE)
    ns = parse_cli()
    rclone_cfg = read_rclone(ns.rclone) if ns.rclone else ""
    weston_ini = _read(THISDIR / "weston.ini")
    print(tmpl.render(
        units=units,
        wifi={"ssid": ns.ssid, "pw": ns.wifi_pw},
        nm_configs=read_nm(),
        plai=ns.plai,
        mplayer=ns.mplayer,
        mplayer_conf=read_mplayer_conf(),
        mplayer_sched=read_mplayer_sched(),
        rclone=ns.rclone,
        rclone_cfg=rclone_cfg,
        weston_ini=weston_ini,
        resources=populate_resources(ns.resources),
        )
    )

if __name__ == "__main__":
    sys.exit(main() or 0)
