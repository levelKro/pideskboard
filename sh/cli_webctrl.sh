#!/bin/bash
cd /home/pi/pideskboard/py/ctrl
sudo -E python3 ./webctrl.py >/home/pi/pideskboard/py/webctrl.log  2>&1 &