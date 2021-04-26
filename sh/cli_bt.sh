#!/bin/bash
#/home/pi/pideskboard/sh/cli_icon.sh 3000 disconnect 3
sudo systemctl stop bluetooth
sudo systemctl start bluetooth
sleep 2
#/home/pi/pideskboard/sh/cli_icon.sh 3000 sound_mute 3
pulseaudio -k
pulseaudio -D
sleep 2
#/home/pi/pideskboard/sh/cli_icon.sh 3000 sound 3
echo "Reload Bluetooth PulseAudio policy"
pactl unload-module module-bluetooth-policy
pactl load-module module-bluetooth-policy
sleep 2
while read x ; do sleep 2s ; echo $x ; done <<eof | bluetoothctl
power on
agent on
default-agent
connect 18:15:DA:D9:87:37
quit
eof
#/home/pi/pideskboard/sh/cli_icon.sh 3000 connect 3