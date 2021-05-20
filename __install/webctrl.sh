#!/bin/bash
#
### BEGIN INIT INFO
# Provides:          piwebctrl.py
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Start daemon at boot time
# Description:       Enable service provided by daemon.
### END INIT INFO

PATH=/usr/local/bin/:$PATH
RETVAL=0

# See how we were called.
case "$1" in
  start)
    echo "Start process"
    /home/pi/pideskboard/sh/cli_webctrl.sh &
    ;;
  stop)
    echo "Stop process"
	/home/pi/pideskboard/sh/cli_killCtrl.sh &
    ;;
  restart)
    echo "Re-Start process"
    /home/pi/pideskboard/sh/cli_restartCtrl.sh &
    ;;        
  *)
    echo $"Usage: piwebctrl.sh {start} {stop} {restart}"
    RETVAL=2
esac

exit $RETVAL