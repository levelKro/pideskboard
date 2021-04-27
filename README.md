# piDeskboard
The piDeskboard is a project about creation of interactive informations panel for your Raspberry Pi.

Firstly created only a Web interface, new improvement make it better with a new UI in Python with GTK.
See the feature list for all possibilities;

* Wheater informations with OpenWheather API (https://openweathermap.org/)
* Mailbox reads and unreads messages counter (imap based)
* Internet Radio player (now from https://radio.levelkro.net/, but add option to change it in future version)
* Todo list (read doc of the day system)
* Time & Date (And tell the current time using eSpeak)
* IP Camera streams (up to 5 MJpeg cameras) (currently in development, but add option to change it in future version, but available into Web UI with unlimited number)
* Web interface for use with any recent Web browser on your network
* Calendar (WebUI only, version python planned)
* Network & Servers status (WebUI only, version python not planned)
* List reader (WebUI only, version python planned)
* Text reader (WebUI only, version python planned)
* Weather forecast (WebUI only, version python planned)
* For working with LCD panel with touch (HDMI and/or SPI)

## About this current version
This version have a stable Web UI version and work-in-progress version for Python. 
The project is currently in Alpha stage, many bug and unfinished or missing features are present.
You can use this files now, but at your own risk. You can report any feedback about this project and execution of this for helping to made a better product.

## Minimum requirements
Please note to use a Fresh new install of the Raspbian OS on your SD card, with SSH enabled, network configured with the hostname, and auto-login to CLI.
After installation, you must not use the device for other thing of project for best performances and security reasons.

* Raspbian OS Lite (not the Desktop, only CLI) (tested with image from december 2020)
* Minimum 4Gb MicroSD card, 8Gb suggested
* Raspberry Pi 0,1,2,3 (tested with Raspberry Pi Zero W)
* Audio output for use with eSPeak (optionnal) (BT for RPi0, BT/HDMI or Analog for RPi1,2,3)
* Video output (HDMI or LCD by GPIO)
* Touch input (for use the player and cameras)
* Raspberry Pi 0,1,2,3 headless ready to use, with SSH enabled and available
* Internet connection

## Raspberry Pi 4
It can be installed on a Raspberry Pi 4, but given the hardware difference and my inability to test it, I can't guarantee the files and guide will work.

## Headless startup
In the "__install\boot" folder you can copy the "ssh" to your MicroSD card "/boot" partition for enabling the SSH.
You can also copy the "wpa_supplicant.conf.dist" into "wpa_supplicant.conf" inside the "/boot" and edit it for activate the Wifi with Raspberry Pi 0 W/WH and Raspberry Pi 3.

## Install
Please refer to this Wiki page; https://levelkro.xyz/wiki/RPi-piDeskboard (French)

## Credits
Please note, this pâckage includes ressources from;

* font-awesome
* MusicTicker - XML
* SCXML object
* GTK+ 
* GStreamer
* OpenCV
* 3D Cube rotating CSS
* Icons from Flat Icon (https://www.flaticon.com/)
* And others (add them when is possible)

Do not distribute any part of this codes without permissions. 
