#!/bin/bash
cd /volume1/docker/audio_webcontrol
. venv/bin/activate
nohup python app.py > server.log 2>&1 &
