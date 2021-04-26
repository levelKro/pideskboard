#!/bin/bash
#
## Only work if raspidmx is present and you use the HDMI port for the icon
case "$3" in
  1)
	/usr/bin/screen -h 10 -dmS Icon /home/pi/raspidmx/pngview/pngview -x 10 -y 30 -b 0 -l 3 -n -t $1 /home/pi/pideskboard/icons/$2.png  > /dev/null 2>&1    
    ;;
  2)
	/usr/bin/screen -h 10 -dmS Icon /home/pi/raspidmx/pngview/pngview -x 30 -y 10 -b 0 -l 3 -n -t $1 /home/pi/pideskboard/icons/$2.png  > /dev/null 2>&1
    ;;
  3)
	/usr/bin/screen -h 10 -dmS Icon /home/pi/raspidmx/pngview/pngview -x 10 -y 10 -b 0 -l 3 -n -t $1 /home/pi/pideskboard/icons/$2.png  > /dev/null 2>&1
    ;;
  *)
	/usr/bin/screen -h 10 -dmS Icon /home/pi/raspidmx/pngview/pngview -x 10 -y 10 -b 0 -l 1 -n -t $1 /home/pi/pideskboard/icons/$2.png  > /dev/null 2>&1  
    ;;
esac
