#! /bin/bash
cd ~/agua
source bin/activate
./daemons/watering.py &
./app.py
