#!/bin/bash
let pid=$(pgrep -f webctrl.py)
echo "Found PID: $pid"
if [[ ! -z "$pid" ]]
then
	echo "Kill and restart"
	sudo kill -9 $pid
	sleep 2
	/home/pi/pideskboard/sh/cli_webctrl.sh
fi