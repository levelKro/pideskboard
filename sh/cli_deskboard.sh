#!/bin/bash
cd /home/pi/pideskboard/py/ui
#DISPLAY=:0 nohup python3 /home/pi/piDeskboard/app.py >/dev/null 2>&1 &
DISPLAY=:0 nice python3 ./app.py &
