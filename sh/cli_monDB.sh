#!/bin/sh
while inotifywait -qr /home/pi/pideskboard/www/configs -e modify,create,delete; do { 
	/home/pi/pideskboard/sh/cli_icon.sh 1000 disk 2
}; done
