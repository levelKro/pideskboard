#!/bin/bash
/home/pi/pideskboard/sh/cli_splash.sh
#/home/pi/pideskboard/sh/cli_icon.sh 60000 hourglass 0
nohup /home/pi/pideskboard/sh/cli_bt.sh >/dev/null 2>&1 &
/home/pi/pideskboard/sh/dm_monitor.sh &
#nohup php /home/pi/pideskboard/php/espeak.php >/dev/null 2>&1 &
#nohup php /home/pi/pideskboard/php/cron.php >/dev/null 2>&1 &
startx -- -nocursor -quiet