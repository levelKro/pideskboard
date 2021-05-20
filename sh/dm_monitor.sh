#!/bin/sh
#
watch -n60 /home/pi/pideskboard/sh/cli_checkScript.sh espeak >/dev/null 2>&1 &
watch -n60 /home/pi/pideskboard/sh/cli_checkScript.sh cron >/dev/null 2>&1 &