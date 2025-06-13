#!/usr/bin/env python3

import os
import sys
import argparse

from pathlib import Path
import jinja2

THISDIR=Path(__name__).parent.resolve()

def _read(path: os.PathLike):
    with open(path) as f:
        return f.read()

SCRIPT_TEMPLATE = _read(THISDIR / "bootstrap.sh.in")

def read_units():
    units = []
    patterns = ["*.service", "*.timer"]
    for pat in patterns:
        for unit in (THISDIR/ "systemd").glob(pat):
            with open(unit) as f:
                content = f.read()
            units.append({"file": unit.name, "content": content})
    return units

def read_nm():
    cfgs = []
    for cfg in (THISDIR/"NetworkManager").glob("*.nmconnection"):
        cfgs.append({"file": cfg.name, "content": _read(cfg)})
    return cfgs

def parse_cli() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--ssid", help="WLAN SSID. Set to '' to disable", required=True)
    p.add_argument("--wifi-pw", help="WLAN password. Set to empty to disable")
    ns = p.parse_args()
    if ns.ssid and ns.wifi_pw is None:
        raise ValueError("WIFI password required. Set to empty to disable")
    return ns

def main():
    units = read_units()
    tmpl = jinja2.Template(SCRIPT_TEMPLATE)
    ns = parse_cli()
    print(tmpl.render(units=units, wifi={"ssid": ns.ssid, "pw": ns.wifi_pw}, nm_configs=read_nm()))

if __name__ == "__main__":
    sys.exit(main() or 0)
