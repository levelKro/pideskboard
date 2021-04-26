#!/bin/bash
	if pgrep -f "$1.php" > /dev/null
	then
		#is running
		exit
	else
		#not running, restart them
		nohup php /home/pi/pideskboard/php/$1.php >/dev/null 2>&1 &
	fi
