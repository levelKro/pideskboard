#!/bin/bash
# Other parameter : -p 30
#/home/pi/pideskboard/cli_icon.sh 5000 sound
nohup /usr/bin/espeak -s 100 -l 1 -a 125 -b 1 -v $1 "$2" >/dev/null 2>&1 &
