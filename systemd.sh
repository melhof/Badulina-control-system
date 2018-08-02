#! /bin/bash
cd ~/agua
source bin/activate
./water_daemon.py &
./app.py
