#!/bin/bash
clear
sudo nohup /usr/bin/fbi -T 2 -d /dev/fb1 -noverbose -a /home/pi/pideskboard/splash.png >/dev/null 2>&1 & 