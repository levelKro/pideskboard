#!/bin/bash
#
# pi Deskboard Installer
#
# Revision 2 - 12-2021
# 

clear
echo "*** piDeskboard installation script ***"
echo "*** Starting in 5 seconds, press CTRLC for cancel."
echo " "
echo " "
sleep 5

echo "** Step 1/5 : Pre-requirement and system setup for installation"
echo "** .. Updating the system"
# Pre-requirement for this script
sudo apt -qq update
sudo apt -qq upgrade -y
echo "** .. Install requirements"
sudo apt -qq install -y git wget
echo "** .. Move to 'pi' directory"
# Move to user folder
cd /home/pi
sleep 1
echo "** Step 2/5 : Download required files"
# Download files without apt process
wget -q https://raspberry-pi.fr/download/espeak/mbrola3.0.1h_armhf.deb -O mbrola.deb
git clone --depth=1 https://gitlab.com/DarkElvenAngel/initramfs-splash.git
git clone https://github.com/levelKro/pideskboard.git
sudo dpkg -i mbrola.deb
sleep 1
echo "** Step 3/5 : Download and install required apps"
# Install by apt process
echo "** .. Installing with apt-get (for system) ..."
echo "** .. .. Installing X Server ..."
sudo apt -qq install -y --no-install-recommends xserver-xorg x11-xserver-utils xinit openbox
echo "** .. .. Installing Python 3, Samba, eSpeak and Yasm ..."
sudo apt -qq install -y python3-dev python3-pip yasm samba espeak espeak-ng mbrola-fr* mbrola-en* mbrola-ca*
echo "** .. .. Installing PHP for cli ..."
sudo apt -qq install -y php php-cli php-imap php-curl php-xml php-xmlrpc
echo "** .. .. Installing Python 3 modules ..."
sudo apt -qq install -y python3-gi python3-gi-cairo libgirepository1.0-dev gir1.2-gtk-3.0 python3-gst-1.0 gir1.2-gstreamer-1.0 gstreamer1.0-tools gstreamer1.0-gtk3 python3-opencv python3-numpy
sudo apt -qq install -y gir1.2-gst-plugins-base-1.0 gstreamer1.0-plugins-good gstreamer1.0-plugins-ugly gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly-amr vlc python3-vlc
echo "** .. Installing with pip (for python) ..."
pip3 install --upgrade pip setuptools wheel
pip3 install numpy python-vlc psutil gpiozero Pillow
pip3 install --no-use-pep517 opencv-python
sleep 1
echo "** Step 4/5 : Installing piDeskboard"
# Install piDeskboard
echo "** .. Copying files for system ..."
sudo cp -r /home/pi/pideskboard/__install/_fonts /home/pi/.fonts
sudo cp /home/pi/initramfs-splash/boot/initramfs.img /boot/initramfs.img
sudo cp /home/pi/pideskboard/splash.png /boot/splash.png
sudo cp /home/pi/pideskboard/__install/boot/splash.txt /boot/splash.txt
echo "** .. Enabling scripts ..."
sudo chmod +x /home/pi/pideskboard/sh/*.sh
echo "** .. Register piDeskboard for update with GIT"
cd /home/pi/pideskboard
git remote add upstream https://github.com/levelKro/pideskboard.git
git pull upstream main
sleep 1
echo "** Step 5/5 : Editing system files"
# Edit files
echo "** .. Enable the Samba Share for configs and pi home ..."
sudo -s sudo cat >> /etc/samba/smb.conf << EOF
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
echo "** .. Adding start of X server for GUI ..."
sudo -s sudo cat >> /home/pi/.profile << EOF
[[ -z \$DISPLAY && \$XDG_VTNR -eq 1 ]] && /home/pi/pideskboard/sh/dm_start.sh
EOF
echo "** .. Adding autostart option for display and piDeskboard ..."
sudo -s sudo cat >> /etc/xdg/openbox/autostart << EOF
xset s off
xset s noblank
xset -dpms
setxkbmap -option terminate:ctrl_alt_bksp
DISPLAY=:0 nohup /home/pi/pideskboard/sh/cli_deskboard.sh >/dev/null 2>&1 &
EOF
sleep 1
echo "All is done. Now rebooting in 10 secondes."
echo "Please read the documentation for configuration, visit http://<ip-of-this-pi>:9000/ for controling it."
sleep 10
# End, reboot
sudo reboot