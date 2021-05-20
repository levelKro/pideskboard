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
    let pid=$(pgrep -f webctrl.py)
    echo "Found PID: $pid"
    if [[ ! -z "$pid" ]]
    then
      echo "Kill process"
      sudo kill -9 $pid
    fi
    ;;
  restart)
    let pid=$(pgrep -f webctrl.py)
    echo "Found PID: $pid"
    if [[ ! -z "$pid" ]]
    then
      echo "Kill process"
      sudo kill -9 $pid
    fi
	echo "Start process"
    /home/pi/pideskboard/sh/cli_webctrl.sh &
    ;;        
  *)
    echo $"Usage: piwebctrl.sh {start} {stop} {restart}"
    RETVAL=2
esac

exit $RETVAL