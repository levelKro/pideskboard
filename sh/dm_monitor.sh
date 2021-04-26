#!/bin/sh
#
## Only work if raspidmx is present and you use the HDMI port for the icon
#nohup /home/pi/pideskboard/sh/cli_monError.sh >/dev/null 2>&1 &
#nohup /home/pi/pideskboard/sh/cli_monDB.sh >/dev/null 2>&1 &
watch -n60 /home/pi/pideskboard/sh/cli_checkScript.sh espeak >/dev/null 2>&1 &
watch -n60 /home/pi/pideskboard/sh/cli_checkScript.sh cron >/dev/null 2>&1 &

