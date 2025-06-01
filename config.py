#!/usr/bin/env python3

import sys
import json
from pathlib import Path

def prompt(store: dict, key: str):
    while True:
        res = input(f"Give {key}: ")
        ack = input(f"Value for '{key}' is '{res}'. Is this ok? (y/n)")
        if ack.lower() == "y":
            store[key] = res
            return

data = {}



def main():
    prompt(data, "target_ip")
    prompt(data, "user")
    prompt(data, "passwor

    thisdir = Path(sys.argv[0]).parent
    config = thisdir / ".config.json"

    with open(config , "w") as f:
        json.dump(data, f)

if __name__ == "__main__":
    sys.exit(main() or 0)

