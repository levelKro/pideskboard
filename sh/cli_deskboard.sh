#!/bin/bash
cd /home/pi/pideskboard/py/ui
DISPLAY=:0 nice python3 ./deskboard.py >/home/pi/pideskboard/py/deskboard.log  2>&1 &
