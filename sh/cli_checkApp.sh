#!/bin/bash
if pgrep -f "deskboard.py" > /dev/null 
then
	#is running
	exit 
else
	#not running, restart them
	nohup /home/pi/pideskboard/sh/cli_deskboard.sh >/dev/null 2>&1 &
fi

