#!/bin/bash
#####################
##
##
##  Autoinstallation script
##	for pi Deskboard
##	(c) Mathieu Légar <levelkro@yahoo.ca> https://levelkro.com

## USER REQUIREMENT
## -RASPBIAN OS LITE (BUSTER)
## -HOSTNAME CONFIGURED
## -WIFI/LAN CONFIGURED AND ACTIVE
## -AUTOLOGIN CLI

echo "### Installation of piDeskboard v1.0 alpha"
echo ">> You must have a active Internet connection before continue this installation"
echo ">> Also, you must configure the auto-login via the raspi-ci=onfig program"
read -p "Are you ready? " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
	sleep 1
	#MAJ Système
	echo "Ok, starting to update system before all..." -n 1
	sudo apt update && sudo apt upgrade -y >/dev/null 2>&1 &
	echo "... done" -n 1
	echo "Installing requirements, step 1/4" -n 1
	sudo apt install -y python3-dev python3-pip yasm wget git samba espeak >/dev/null 2>&1 &
	echo "... done" -n 1
	echo "Installing requirements, step 2/4" -n 1
	sudo apt install -y apache2 php php-cli php-imap php-curl php-xml php-xmlrpc libapache2-mod-php >/dev/null 2>&1 &
	echo "... done" -n 1
	echo "Installing requirements, step 3/4" -n 1
	sudo apt install -y python-gi-dev python-gi python-gi-cairo python3-gi python3-gi-cairo libgirepository1.0-dev gir1.2-gtk-3.0 python3-gst-1.0 gir1.2-gstreamer-1.0 gstreamer1.0-tools gstreamer1.0-gtk3 python3-opencv python3-numpy >/dev/null 2>&1 &
	echo "... done" -n 1
	echo "Installing requirements, step 4/4" -n 1
	sudo apt install -y gir1.2-gst-plugins-base-1.0 gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly-amr  >/dev/null 2>&1 &
	echo "... done" -n 1
	echo "Now downloading external requirements" -n 1
	## DOWNLOAD from external sources
	wget -q https://raspberry-pi.fr/download/espeak/mbrola3.0.1h_armhf.deb -O mbrola.deb
	git clone --depth=1 https://gitlab.com/DarkElvenAngel/initramfs-splash.git >/dev/null 2>&1 &
	git clone https://github.com/levelKro/pideskboard.git >/dev/null 2>&1 &
	echo "... done" -n 1
	echo "Installing external requirements" -n 1
	sudo dpkg -i mbrola.deb >/dev/null 2>&1 &
	echo "... Installing extra for French support ... " -n 1
	sudo apt install -y mbrola-fr* >/dev/null 2>&1 &
	echo "... Python requirements installation ... " -n 1
	pip3 install opencv-contrib-python numpy >/dev/null 2>&1 &
	echo "... done" -n 1
	echo "Now installing the X server for the GUI..." -n 1	
	## X11 SERVER
	sudo apt install -y --no-install-recommends xserver-xorg x11-xserver-utils xinit openbox >/dev/null 2>&1 &
	echo "... done" -n 1
	echo "Now need to prepare files from piDeskboard before use it ..." -n 1	
	##	BOOT SCREEN INSTALL
	sudo cp /home/pi/initramfs-splash/boot/initramfs.img /boot/initramfs.img >/dev/null 2>&1 &
	sudo cp /home/pi/pideskboard/splash.png /boot/splash.png >/dev/null 2>&1 &
	sudo cp /home/pi/pideskboard/__install/boot/splash.txt /boot/splash.txt >/dev/null 2>&1 &
	sudo cp -r /home/pi/pideskboard/__install/home/_fonts /home/pi/.fonts >/dev/null 2>&1 &
	chmod -x /home/pi/pideskboard/sh/*.sh
	cd /home/pi/pideskboard
	git remote add upstream https://github.com/levelKro/pideskboard.git >/dev/null 2>&1 &
	git pull upstream main >/dev/null 2>&1 &

	## APACHE 2 CONFIG
	sudo sed -i 's|/var/www/html|/home/pi/pideskboard/www|g' /etc/apache2/sites-enabled/000-default.conf
	sudo sed -i 's|/var/www|/home/pi/pideskboard|g' /etc/apache2/apache2.conf

	sleep 1
	## SAMBA SHARE
	sudo -s cat >> /etc/samba/smb.conf << EOF
	[home$]
	  path = /home/pi
	  guest ok = yes
	  force user = pi
	  force group = pi
	  browseable = yes
	  writable = yes
	  read only = no

	[configs]
	  path = /home/pi/pideskboard/configs
	  guest ok = yes
	  force user = pi
	  force group = pi
	  browseable = yes
	  writable = yes
	  read only = no
EOF
	
	sudo -s cat >> /home/pi/.profile << EOF
	[[ -z $DISPLAY && $XDG_VTNR -eq 1 ]] && /home/pi/pideskboard/sh/dm_start.sh
EOF
	sudo -s cat >> /etc/xdg/openbox/autostart << EOF
	xset s off
	xset s noblank
	xset -dpms
	setxkbmap -option terminate:ctrl_alt_bksp
	DISPLAY=:0 nohup /home/pi/pideskboard/sh/cli_deskboard.sh >/dev/null 2>&1 &
EOF
	echo "*** ALL IS DONE !!"
	echo "PLEASE NOTE: For safety, this script do not edit 'config.txt' and 'cmdline.txt'."
	echo "\tFor use the Splash screen, you need to add at the end of '/boot/cmdline.txt' this parameters; "
	echo "\t\t splash silent quiet"
	echo "\tYou need also to add this line in the '/boot/config.txt';"
	echo "\t\tinitramfs initramfs.img"
	echo 
	echo "Thank you to use the piDeskboard, when you have finish, reboot to enjoy"
fi


