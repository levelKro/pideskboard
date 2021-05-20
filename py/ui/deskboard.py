#PiDeskboard by Mathieu Légaré <levelkro@yahoo.ca> https://levelkro.com
#
import json, requests, threading, configparser
import gi, re, os, datetime, time, cairo
import cv2
import numpy as np
import libvlc as vlc
gi.require_version("Gtk", "3.0")
gi.require_version('Gst', '1.0')
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf, InterpType
from datetime import datetime

#Main Class
class Deskboard():
    def __init__(self):
        #pre-init
        self.loadConfig()
        self.loadUI()
        self.loadNames()
        self.loadActions()
        self.setUpdates()
        self.loadPlayer()
        self.startMarquee()
        GLib.timeout_add_seconds(5, self.setUpdates)        
        Gtk.main()        
        
    def getApi(self,action):
        jsonUrl = self.apiUrl + action
        url = requests.get(jsonUrl)
        return url.text

    def getImage(self,url):
        response = requests.get(url)
        fname = url.split("/")[-1]
        f = open(fname, "wb")
        f.write(response.content)
        f.close()
        response.close()
        return fname

    def cleanhtml(self,raw_html):
        cleanr = re.compile('<.*?>')
        cleantext = re.sub(cleanr, '', raw_html)
        return cleantext
    
    def readJson(self,path):
        with open(path) as json_file:
            return json.load(json_file)
    
    def imageText(self,pixbuf, text, x, y):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, pixbuf.get_width(), pixbuf.get_height())
        context = cairo.Context(surface)
        Gdk.cairo_set_source_pixbuf(context, pixbuf, 0, 0)
        context.paint()
        fontsize= self.camTimeSize
        context.move_to(x, y+fontsize)
        context.set_font_size(fontsize)
        context.set_source_rgba(255,255,255,1)
        context.show_text(text)
        surface= context.get_target()
        pixbuf= Gdk.pixbuf_get_from_surface(surface, 0, 0, surface.get_width(), surface.get_height())
        return pixbuf

    # Marquee effect
    def marquee(self, text):
        if text is None:
            text = "Error META"
        if self.a < len(text):
            self.a = self.a + 1
            self.z = self.z + 1
            if self.a >= len(text):
                self.a = 0
                self.z = self.mwmarquee
        return str(text[self.a:self.z])

    def displayMarquee(self):
        self.dataPlayerDetails.set_label(self.marquee(self.radioInfo))
        return True

    def startMarquee(self):
        GLib.timeout_add(500, self.displayMarquee)

    def loadConfig(self):
        try:
            self.config = configparser.ConfigParser()
            self.config.read('../../configs/config.ini')
            self.weatherUrl = ""
            self.count = 0        
            self.statePlayer = False
            self.stateCamera = False
            self.radioStreamUrl = "http://radio.levelkro.net:8000/1"; #default value, refreshed with API
            self.defaultPath = self.config['system']['path']+"ui/"
            self.radioInfo = "Loading . . ."
            self.radioInfoShadow = "Loading . . ."
            if self.config['system']['resolution'] == "1024x600":
                #1024x600
                self.mwmarquee = 25
                self.resoWidth = 1024
                self.resoHeight = 600
                self.camResizeWidth=640
                self.camResizeHeight=480
                self.camTimeSize=20            
                self.camTimePosition=120
            elif self.config['system']['resolution'] == "800x480":
                #800x480
                self.mwmarquee = 23
                self.resoWidth = 800
                self.resoHeight = 480
                self.camResizeWidth=320
                self.camResizeHeight=240
                self.camTimeSize=10            
                self.camTimePosition=60
            else:
                #480x320, default
                self.mwmarquee = 17
                self.resoWidth = 480
                self.resoHeight = 320
                self.camResizeWidth=320
                self.camResizeHeight=240
                self.camTimeSize=10            
                self.camTimePosition=60
            self.pathUI = self.defaultPath + self.config['system']['resolution'] + "/"
            self.a = 0
            self.z = self.mwmarquee 
        except:
            print("Cant't load configurations datas")
            exit()
        
    def saveConfig(self):
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
            
    def loadUI(self):
        self.root = Gtk.Builder()
        self.root.add_from_file(self.pathUI + "deskboard.glade")
        self.window = self.root.get_object("window")
        self.window.set_default_size(self.resoWidth, self.resoHeight)        
        self.window.set_title("PiDeskboard in Python")
        self.window.connect("destroy", Gtk.main_quit, "WM destroy")
        self.window.show_all()
        self.windowMJpeg = self.root.get_object("windowMJpeg")
        self.windowCtrl = self.root.get_object("windowControl")
        
    def loadNames(self):
        self.dataDate =  self.root.get_object("dataDate")
        self.dataTime =  self.root.get_object("dataTime")
        self.dataWeatherTemp =  self.root.get_object("dataWeatherTemp")
        self.dataWeatherFeel =  self.root.get_object("dataWeatherFeel")
        self.dataWeatherTempMin =  self.root.get_object("dataWeatherTempMin")
        self.dataWeatherTempMax =  self.root.get_object("dataWeatherTempMax")
        self.dataWeatherClouds =  self.root.get_object("dataWeatherClouds")
        self.dataWeatherRain =  self.root.get_object("dataWeatherRain")
        self.dataWeatherSnow =  self.root.get_object("dataWeatherSnow")
        self.dataWeatherDetails =  self.root.get_object("dataWeatherDetails")
        self.dataWeatherIcon =  self.root.get_object("dataWeatherIcon")
        self.dataMailboxRead =  self.root.get_object("dataMailboxRead")
        self.dataMailboxUnread =  self.root.get_object("dataMailboxUnread")
        self.textToday =  self.root.get_object("textToday")
        self.listToday =  self.root.get_object("listToday")
        self.templateTextA = self.root.get_object("templateTextA")
        self.buttonPlayerAction = self.root.get_object("buttonPlayerAction")
        self.imagePlayerAction = self.root.get_object("imagePlayerAction")
        self.dataPlayerTime = self.root.get_object("dataPlayerTime")
        self.dataPlayerDetails = self.root.get_object("dataPlayerDetails")
        #UI:Ctrl
        self.buttonCtrlOpen = self.root.get_object("buttonCtrlOpen")
        self.ButtonCtrlClose = self.root.get_object("buttonCtrlClose")
        self.ButtonCtrlClose.connect("clicked", self.triggerCtrlClose)
        self.buttonCtrlPoweroff = self.root.get_object("buttonCtrlPoweroff")
        self.buttonCtrlPoweroff.connect("clicked", self.triggerPoweroff)
        self.buttonCtrlReboot = self.root.get_object("buttonCtrlReboot")
        self.buttonCtrlReboot.connect("clicked", self.triggerReboot)
        self.buttonCtrlBluetooth = self.root.get_object("buttonCtrlBluetooth")
        self.buttonCtrlBluetooth.connect("clicked", self.triggerBluetooth)
        self.buttonCtrlRestart = self.root.get_object("buttonCtrlRestart")
        self.buttonCtrlRestart.connect("clicked", self.triggerRestart)
        #UI:MJpeg
        self.placeButtonCameras = self.root.get_object("placeButtonCameras")
        self.buttonMJpegClose = self.root.get_object("buttonMJpegClose")
        self.buttonMJpegClose.connect("clicked", self.triggerMJpegClose)
        self.imageMJpegStream = self.root.get_object("imageMJpegStream")
        self.buttonMJpegOpen = self.root.get_object("buttonMJpegOpen")
        self.buttonMJpegOpen.connect("clicked", self.triggerMJpegOpen)
        self.textMJpegStream = self.root.get_object("textMJpegStream")
        
    def loadActions(self):
        self.buttonCtrlOpen.connect("clicked", self.triggerCtrl)
        self.buttonCtrlOpen.show()
        i=1
        self.buttonIPCam = []
        while i <= 5:
            if 'cam' + str(i) in self.config['cameras']:
                thisTmp = Gtk.Button()
                thisTmp.add(Gtk.Image.new_from_file(self.pathUI + "cam" + str(i) + ".png"))
                if self.config['cameras']['mode'] == "live":
                    thisTmp.connect("clicked", self.triggerMJpegCamera,i)
                else:
                    thisTmp.connect("clicked", self.triggerMJpegCameraPreview,i)
                thisTmp.props.relief = Gtk.ReliefStyle.NONE
                self.buttonIPCam.append(thisTmp)
            i += 1
        for x in self.buttonIPCam:
            self.placeButtonCameras.add(x)
        self.placeButtonCameras.show_all()
        
    #Cameras
    def triggerMJpegOpen(self,w):
        self.imageMJpegStream.set_from_file(self.pathUI + "nocamera.jpg")
        self.windowMJpeg.show_all()
        self.stream = ''

    def triggerMJpegClose(self,w):
        self.stateCamera=False
        self.id = 0
        self.windowMJpeg.hide()
   
    #Mode Preview (Less CPU usage)
        
    def triggerMJpegCameraPreview(self,w,id):
        try:
            self.windowMJpeg.show_all()
            self.textMJpegStream.set_text("Camera " + str(id))
            self.id=id
            self.stream = self.config['cameras']['camImage' + str(id)]
            self.threadCamera = threading.Thread(target=self.startCameraPreview)
            self.stateCamera = True
            self.threadCamera.daemon=True 
            self.threadCamera.start()          
        except:
            print("Cant't load camera process")
        
    def startCameraPreview(self):
        try:
            id=self.id
            error = 0
            while(True):
                if id != self.id or self.stateCamera == False:
                    GLib.idle_add(self.imageMJpegStream.set_from_file,self.pathUI + "nocamera.jpg")
                    break
                thisFrame = self.getImage(self.stream)
                thisFrameFile = Pixbuf.new_from_file(thisFrame)
                if thisFrameFile is None and error >= 3:
                    GLib.idle_add(self.imageMJpegStream.set_from_file,self.pathUI + "nocamera.jpg")
                    break
                elif thisFrameFile is None:
                    error += 1
                else:
                    error = 0
                    thisFrameFileResize = thisFrameFile.scale_simple(self.camResizeWidth, self.camResizeHeight, InterpType.BILINEAR)
                    dateTimeObj = datetime.datetime.now()
                    dateString = dateTimeObj.strftime("%H:%M:%S")
                    thisFrameFileTimestamp = self.imageText(thisFrameFileResize,dateString,self.camResizeWidth-self.camTimePosition,10)
                    GLib.idle_add(self.imageMJpegStream.set_from_pixbuf,thisFrameFileTimestamp)
                time.sleep(5)
        except:
            print("Cant't load camera preview process")
    
    #Mode Live (More CPU Usage)
    def triggerMJpegCamera(self,w,id):
        try:
            self.windowMJpeg.show_all()
            self.textMJpegStream.set_text("Camera " + str(id))
            self.id=id
            self.stream = self.config['cameras']['cam' + str(id)]
            self.threadCamera = threading.Thread(target=self.startCamera)
            self.stateCamera = True
            self.threadCamera.daemon=True 
            self.threadCamera.start()
        except:
            print("Cant't load camera process")
        
    def startCamera(self):
        try:
            id=self.id
            jump = 0
            self.capture_video = cv2.VideoCapture(self.stream)
            while(True):
                if id != self.id or self.stateCamera == False:
                    GLib.idle_add(self.imageMJpegStream.set_from_file,self.pathUI + "nocamera.jpg")
                    break
                ret, img = self.capture_video.read()
                if img is None:
                    GLib.idle_add(self.imageMJpegStream.set_from_file,self.pathUI + "nocamera.jpg")
                    break
                if jump == 0:
                    jump = 1
                    img=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    imgResize = cv2.resize(img, (self.camResizeWidth, self.camResizeHeight))
                    imageWorked = np.array(imgResize).ravel()
                    imagePixbuf = GdkPixbuf.Pixbuf.new_from_data(imageWorked,GdkPixbuf.Colorspace.RGB, False, 8, self.camResizeWidth, self.camResizeHeight, 3*self.camResizeWidth)
                    dateTimeObj = datetime.datetime.now()
                    dateString = dateTimeObj.strftime("%H:%M:%S")
                    imagePixbufTimestamp = self.imageText(imagePixbuf,dateString,self.camResizeWidth-self.camTimePosition,10)                
                    GLib.idle_add(self.imageMJpegStream.set_from_pixbuf,imagePixbufTimestam)
                elif jump >= 5:
                    jump = 0
                else:
                    jump += 1
                #time.sleep(0.2)         
        except:
            print("Cant't load camera view process")
            
    #Controls
    def triggerCtrl(self,w):
        self.windowCtrl.show_all()
    def triggerCtrlClose(self,w):
        self.windowCtrl.hide()
        
    def triggerPoweroff(self,w):
        os.system(self.config['cli']['poweroff'])
    def triggerReboot(self,w):
        os.system(self.config['cli']['reboot'])
    def triggerRestart(self,w):
        os.system(self.config['cli']['restart'])
    def triggerBluetooth(self,w):
        os.system(self.config['cli']['bluetooth'])

    #Updates
    def setUpdates(self):
        attText = self.templateTextA.get_attributes()
        try:
            mailbox=self.readJson(self.config['system']['cache'] + "mailbox.json")
            self.dataMailboxUnread.set_text(str(mailbox["unread"]))
            self.dataMailboxRead.set_text(str(mailbox["read"]))
        except:
            print("Cant't read mailbox datas")
        try:
            dateToday=self.readJson(self.config['system']['cache'] + "date.json")
            today = datetime.now()
            self.dataDate.set_text(str(dateToday["today"]))
            self.dataTime.set_text(today.strftime("%H:%M"))
            self.textToday.set_text(dateToday["today_text"])
        except:
            print("Cant't read date and time datas")
        try:
            todoToday=self.readJson(self.config['system']['cache'] + "todo.json")
            for row in self.listToday:
                self.listToday.remove(row)
            row = Gtk.Box()
            for todoItem in todoToday:
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
                toAdd = Gtk.Label()
                toAdd.set_text("- " + self.cleanhtml(todoItem))
                toAdd.set_attributes(attText)
                toAdd.set_line_wrap(True)
                box.pack_start(toAdd, True, True, 0)
                row.add(box)
                self.listToday.add(row)
            self.listToday.show_all()
        except:
            print("Cant't read todo datas")
        try:        
            radio=self.readJson(self.config['system']['cache'] + "radio.json")
            self.radioStreamUrl=radio["url"]
            self.radioInfo=radio["title"] + " - " + radio["songTitle"]
        except:
            print("Cant't read radio datas")
        try:
            weather=self.readJson(self.config['system']['cache'] + "weather.json")
            self.dataWeatherTemp.set_text(weather["temp"])
            self.dataWeatherFeel.set_text(weather["feel"])
            self.dataWeatherTempMin.set_text(weather["min"])
            self.dataWeatherTempMax.set_text(weather["max"])
            self.dataWeatherClouds.set_text(str(weather["clouds"]))
            self.dataWeatherDetails.set_text(weather["name"])        
            rain = "rain" in weather
            snow = "snow" in weather
            if rain:
                self.dataWeatherRain.set_text(str(weather["rain"]))
            else:
                self.dataWeatherRain.set_text("-")
            if snow:    
                self.dataWeatherSnow.set_text(str(weather["snow"]))
            else:
                self.dataWeatherSnow.set_text("-")
            if weather["ico"] != self.weatherUrl :
                imageData=self.getImage(weather["ico"])
                self.weatherUrl = weather["ico"]
                self.dataWeatherIcon.set_from_pixbuf(Pixbuf.new_from_file(imageData))
        except:
            print("Cant't read weather datas")  
        return True
    
    # Music Player
    # With VLC libs
    def loadPlayer(self):
        self.imagePlayerAction.set_from_file(self.pathUI + "play.png")
        self.buttonPlayerAction.connect("clicked", self.triggerPlayer)
        self.buttonPlayerAction.show()
        self.threadPlayer = threading.Thread(target=self.threadPlayer)
        self.threadPlayer.daemon=True 
        self.threadPlayer.start()
        
    def threadPlayer(self):
        try:
            self.statePlayer = False
            self.vlcInstance = vlc.Instance("--no-xlib --quiet")
            self.player = self.vlcInstance.media_player_new()        
            self.player.set_mrl(self.radioStreamUrl)
            self.player.audio_set_volume(100)
        except:
            print("Cant't load player process")
        
    def setPlayerUpdates(self):
        if(self.statePlayer == False):
            return False
        posTimeNano = self.player.get_time()
        posTimeSec = float(posTimeNano / 1000)
        self.dataPlayerTime.set_text(str(datetime.timedelta(seconds=round(posTimeSec))))
        return True
    
    def triggerPlayer(self, widget, data=None):
        if self.statePlayer == False:        
            self.player.set_mrl(self.radioStreamUrl)
            self.player.audio_set_volume(100)
            self.player.play()
            self.buttonPlayerAction.get_child().set_from_file(self.pathUI + "stop.png")
            self.statePlayer = True
            GLib.timeout_add(500, self.setPlayerUpdates)

        elif self.statePlayer == True:
            self.player.stop()
            self.buttonPlayerAction.get_child().set_from_file(self.pathUI + "play.png")
            self.statePlayer = False
            self.dataPlayerTime.set_text("0:00:00")
        else:
            pass        

# End of Class
# Run the main app
app=Deskboard()        