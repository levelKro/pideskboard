#!/bin/sh
while inotifywait -rq /var/log/apache2/error.log -e modify; do { 
	/home/pi/pideskboard/sh/cli_icon.sh 2000 bug 3
}; done
