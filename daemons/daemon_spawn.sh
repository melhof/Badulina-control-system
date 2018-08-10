#! /bin/bash
# this file envoked by systemd via agua.service
# this spawns all necessary processes

cd ~/Badulina-control-system
source bin/activate
./daemons/watering.py &
./daemons/data_collector.py &
./app.py
