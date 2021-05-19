#!/bin/bash
#####################
##
##
##  Autoinstallation script
##for pi Deskboard
##(c) Mathieu Légar <levelkro@yahoo.ca> https://levelkro.com

## USER REQUIREMENT
## -RASPBIAN OS LITE (BUSTER) 2020-02-14 (2020-02-13)
## -HOSTNAME CONFIGURED
## -WIFI/LAN CONFIGURED AND ACTIVE

echo "### Installation of piDeskboard v1.0 alpha"
echo ">> You must have a active Internet connection before continue this installation"
cd /home/pi
#Autologin - from RASPI-CONFIG
sudo systemctl set-default multi-user.target
sudo ln -fs /lib/systemd/system/getty@.service /etc/systemd/system/getty.target.wants/getty@tty1.service
#sudo cat > /etc/systemd/system/getty@tty1.service.d/autologin.conf << EOF
#[Service]
#ExecStart=
#ExecStart=-/sbin/agetty --autologin pi --noclear %I \$TERM
#EOF
sleep 1

#MAJ Système
echo "Ok, starting to update system before all..."
sudo apt -qq update
echo "... done"
echo "Installing requirements, step 1/4"
sudo apt -qq install -y python3-dev python3-pip yasm wget git samba espeak
echo "... done"
echo "Installing requirements, step 2/4"
sudo apt -qq install -y php php-cli php-imap php-curl php-xml php-xmlrpc 
#apache2 libapache2-mod-php
echo "... done"
echo "Installing requirements, step 3/4"
sudo apt -qq install -y python-gi-dev python-gi python-gi-cairo python3-gi python3-gi-cairo libgirepository1.0-dev gir1.2-gtk-3.0 python3-gst-1.0 gir1.2-gstreamer-1.0 gstreamer1.0-tools gstreamer1.0-gtk3 python3-opencv python3-numpy
echo "... done"
echo "Installing requirements, step 4/4"
sudo apt -qq install -y gir1.2-gst-plugins-base-1.0 gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly-amr vlc python3-vlc
echo "... done"
echo "Now downloading external requirements"
wget -q https://raspberry-pi.fr/download/espeak/mbrola3.0.1h_armhf.deb -O mbrola.deb
git clone --depth=1 https://gitlab.com/DarkElvenAngel/initramfs-splash.git
#git clone https://github.com/levelKro/pideskboard.git
echo "... done"
echo "Installing external requirements"
echo "... Installing extra for French support ... "
sudo dpkg -i mbrola.deb
sudo apt -qq install -y mbrola-fr*
echo "... Python requirements installation ... "
sudo pip3 install opencv-contrib-python numpy python-vlc psutil gpiozero
echo "... done"
echo "Now installing the X server for the GUI..."
sudo apt -qq install -y --no-install-recommends xserver-xorg x11-xserver-utils xinit openbox
echo "... done"
echo "Now need to prepare files from piDeskboard before use it ..."

##piDeskboard install
sudo cp /home/pi/initramfs-splash/boot/initramfs.img /boot/initramfs.img
sudo cp /home/pi/pideskboard/splash.png /boot/splash.png
sudo cp /home/pi/pideskboard/__install/boot/splash.txt /boot/splash.txt
sudo cp /home/pi/pideskboard/__install/webctrl.sh /etc/init.d/webctrl.sh
sudo cp -r /home/pi/pideskboard/__install/home/_fonts /home/pi/.fonts
sudo chmod +x /home/pi/pideskboard/sh/*.sh
sudo chmod +x /etc/init.d/webctrl.sh
sudo systemctl enable webctrl.sh
cd /home/pi/pideskboard
git remote add upstream https://github.com/levelKro/pideskboard.git
git pull upstream main

#sudo sed -i 's|/var/www/html|/home/pi/pideskboard/www|g' /etc/apache2/sites-enabled/000-default.conf
#sudo sed -i 's|/var/www|/home/pi/pideskboard|g' /etc/apache2/apache2.conf

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
[[ -z \$DISPLAY && \$XDG_VTNR -eq 1 ]] && /home/pi/pideskboard/sh/dm_start.sh
EOF
sudo -s cat >> /etc/xdg/openbox/autostart << EOF
xset s off
xset s noblank
xset -dpms
setxkbmap -option terminate:ctrl_alt_bksp
DISPLAY=:0 nohup /home/pi/pideskboard/sh/cli_deskboard.sh
EOF
echo "*** ALL IS DONE !!"
echo "PLEASE NOTE: For safety, this script do not edit 'config.txt' and 'cmdline.txt'."
echo "\tFor use the Splash screen, you need to add at the end of '/boot/cmdline.txt' this parameters; "
echo "\t\t splash silent quiet"
echo "\tYou need also to add this line in the '/boot/config.txt';"
echo "\t\tinitramfs initramfs.img"
echo 
echo "Also, you need complete configurations inside the Windows share 'configs' and 'configs/db', remove in name the '.dist' extension."
echo "If you can't access by the Windows share, is stored in the '/home/pi/pideskboard/configs' folder."
echo 
echo "Thank you to use the piDeskboard, when you have finish, reboot to enjoy."