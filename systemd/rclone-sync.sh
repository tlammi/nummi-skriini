#!/bin/bash

REMOTE="skriini"

rclone sync --drive-shared-with-me "$REMOTE:/ScreenReel" ~/skriini
