#!/bin/bash

set -e

# This sets up raspberry pi for running plai and mplayerd

ip=$(jq .target_ip .config.sh)
user=$(jq .user .config.sh)
pw=$(jq .password .config.sh)

# TODO: Check if cage can be used. It would be lighter than weston.
sshpass -p $pw ssh ${user}@${ip} 'sudo bash -e' <<EOF
export DEBIAN_FRONTEND=noninteractive
apt update
apt install -y libavcodec-dev libavformat-dev libavutil-dev libswscale-dev libsdl2-dev libsqlite3-dev libssl-dev libboost-dev libfmt-dev
apt install -y rclone python3 python3-pip weston
EOF
