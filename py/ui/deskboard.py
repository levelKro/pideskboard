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
from datetime import datetime as dt
from PIL import Image

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
        print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Deskboard started")
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

    def getImageResize(self,url,basewidth,baseheight):
        response = requests.get(url)
        fname = url.split("/")[-1]
        f = open(fname, "wb")
        f.write(response.content)
        f.close()
        response.close()
        img = Image.open(fname)
        img = img.resize((basewidth, baseheight), Image.ANTIALIAS)
        frname = str(basewidth)+"x"+str(baseheight)+"-"+fname
        img.save(frname)
        return frname

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
        if self.a < len(text) and self.z <= len(text):
            self.a = self.a + 1
            self.z = self.z + 1
        else:
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
            self.weatherUrlFC1 = ""
            self.weatherUrlFC2 = ""
            self.weatherUrlFC3 = ""
            self.weatherUrlFC4 = ""
            self.weatherUrlFC5 = ""
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
                self.forecastResize=100
            elif self.config['system']['resolution'] == "800x480":
                #800x480
                self.mwmarquee = 20
                self.resoWidth = 800
                self.resoHeight = 480
                self.camResizeWidth=320
                self.camResizeHeight=240
                self.camTimeSize=10            
                self.camTimePosition=60
                self.forecastResize=100
            else:
                #480x320, default
                self.mwmarquee = 15
                self.resoWidth = 480
                self.resoHeight = 320
                self.camResizeWidth=320
                self.camResizeHeight=240
                self.camTimeSize=10            
                self.camTimePosition=60
                self.forecastResize=64
            self.pathUI = self.defaultPath + self.config['system']['resolution'] + "/"
            self.a = 0
            self.z = self.mwmarquee
            print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Configuration loaded")
        except:
            print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Cant't load configurations datas")
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
        self.windowForecast = self.root.get_object("windowForecast")
        self.windowForecastNext = self.root.get_object("windowForecastNext")
        print(dt.now().strftime("%m-%d-%y %H:%M > ") + "UI loaded")
        
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
        #UI:Forecast        
        self.buttonForecastOpen = self.root.get_object("buttonForecast")
        self.buttonForecastOpen.connect("clicked", self.triggerForecastOpen)
        self.ButtonForecastClose = self.root.get_object("buttonForecastClose")
        self.ButtonForecastClose.connect("clicked", self.triggerForecastClose)        
        self.buttonForecastNextOpen = self.root.get_object("buttonForecastNext")
        self.buttonForecastNextOpen.connect("clicked", self.triggerForecastNextOpen)
        self.ButtonForecastNextClose = self.root.get_object("buttonForecastNextClose")
        self.ButtonForecastNextClose.connect("clicked", self.triggerForecastNextClose)
        self.fcToday1ico = self.root.get_object("fcToday1ico")
        self.fcToday1temp = self.root.get_object("fcToday1temp")
        self.fcToday1feel = self.root.get_object("fcToday1feel")
        self.fcToday1min = self.root.get_object("fcToday1min")
        self.fcToday1max = self.root.get_object("fcToday1max")
        self.fcToday1clouds = self.root.get_object("fcToday1clouds")
        self.fcToday1wind = self.root.get_object("fcToday1wind")
        self.fcToday1snow = self.root.get_object("fcToday1snow")
        self.fcToday1rain = self.root.get_object("fcToday1rain")
        self.fcToday1humidity = self.root.get_object("fcToday1humidity")
        self.fcToday1details = self.root.get_object("fcToday1details")
        self.fcToday1time = self.root.get_object("fcToday1time")
        self.fcToday2ico = self.root.get_object("fcToday2ico")
        self.fcToday2temp = self.root.get_object("fcToday2temp")
        self.fcToday2feel = self.root.get_object("fcToday2feel")
        self.fcToday2min = self.root.get_object("fcToday2min")
        self.fcToday2max = self.root.get_object("fcToday2max")
        self.fcToday2clouds = self.root.get_object("fcToday2clouds")
        self.fcToday2wind = self.root.get_object("fcToday2wind")
        self.fcToday2snow = self.root.get_object("fcToday2snow")
        self.fcToday2rain = self.root.get_object("fcToday2rain")
        self.fcToday2humidity = self.root.get_object("fcToday2humidity")
        self.fcToday2details = self.root.get_object("fcToday2details")
        self.fcToday2time = self.root.get_object("fcToday2time")
        self.fcToday3ico = self.root.get_object("fcToday3ico")
        self.fcToday3temp = self.root.get_object("fcToday3temp")
        self.fcToday3feel = self.root.get_object("fcToday3feel")
        self.fcToday3min = self.root.get_object("fcToday3min")
        self.fcToday3max = self.root.get_object("fcToday3max")
        self.fcToday3clouds = self.root.get_object("fcToday3clouds")
        self.fcToday3wind = self.root.get_object("fcToday3wind")
        self.fcToday3snow = self.root.get_object("fcToday3snow")
        self.fcToday3rain = self.root.get_object("fcToday3rain")
        self.fcToday3humidity = self.root.get_object("fcToday3humidity")
        self.fcToday3details = self.root.get_object("fcToday3details")
        self.fcToday3time = self.root.get_object("fcToday3time")
        self.fcToday4ico = self.root.get_object("fcToday4ico")
        self.fcToday4temp = self.root.get_object("fcToday4temp")
        self.fcToday4feel = self.root.get_object("fcToday4feel")
        self.fcToday4min = self.root.get_object("fcToday4min")
        self.fcToday4max = self.root.get_object("fcToday4max")
        self.fcToday4clouds = self.root.get_object("fcToday4clouds")
        self.fcToday4wind = self.root.get_object("fcToday4wind")
        self.fcToday4snow = self.root.get_object("fcToday4snow")
        self.fcToday4rain = self.root.get_object("fcToday4rain")
        self.fcToday4humidity = self.root.get_object("fcToday4humidity")
        self.fcToday4details = self.root.get_object("fcToday4details")
        self.fcToday4time = self.root.get_object("fcToday4time")
        self.fcToday5ico = self.root.get_object("fcToday5ico")
        self.fcToday5temp = self.root.get_object("fcToday5temp")
        self.fcToday5feel = self.root.get_object("fcToday5feel")
        self.fcToday5min = self.root.get_object("fcToday5min")
        self.fcToday5max = self.root.get_object("fcToday5max")
        self.fcToday5clouds = self.root.get_object("fcToday5clouds")
        self.fcToday5wind = self.root.get_object("fcToday5wind")
        self.fcToday5snow = self.root.get_object("fcToday5snow")
        self.fcToday5rain = self.root.get_object("fcToday5rain")
        self.fcToday5humidity = self.root.get_object("fcToday5humidity")
        self.fcToday5details = self.root.get_object("fcToday5details")
        self.fcToday5time = self.root.get_object("fcToday5time")
        self.fcNext1day = self.root.get_object("forecastNextDay1")
        self.fcNext1min = self.root.get_object("forecastNextMin1")
        self.fcNext1max = self.root.get_object("forecastNextMax1")
        self.fcNext1snow = self.root.get_object("forecastNextSnow1")
        self.fcNext1rain = self.root.get_object("forecastNextRain1")
        self.fcNext1month = self.root.get_object("forecastNextMonth1")
        self.fcNext1week = self.root.get_object("forecastNextWeek1")
        self.fcNext2day = self.root.get_object("forecastNextDay2")
        self.fcNext2min = self.root.get_object("forecastNextMin2")
        self.fcNext2max = self.root.get_object("forecastNextMax2")
        self.fcNext2snow = self.root.get_object("forecastNextSnow2")
        self.fcNext2rain = self.root.get_object("forecastNextRain2")
        self.fcNext2month = self.root.get_object("forecastNextMonth2")
        self.fcNext2week = self.root.get_object("forecastNextWeek2")
        self.fcNext3day = self.root.get_object("forecastNextDay3")
        self.fcNext3min = self.root.get_object("forecastNextMin3")
        self.fcNext3max = self.root.get_object("forecastNextMax3")
        self.fcNext3snow = self.root.get_object("forecastNextSnow3")
        self.fcNext3rain = self.root.get_object("forecastNextRain3")
        self.fcNext3month = self.root.get_object("forecastNextMonth3")
        self.fcNext3week = self.root.get_object("forecastNextWeek3")
        self.fcNext4day = self.root.get_object("forecastNextDay4")
        self.fcNext4min = self.root.get_object("forecastNextMin4")
        self.fcNext4max = self.root.get_object("forecastNextMax4")
        self.fcNext4snow = self.root.get_object("forecastNextSnow4")
        self.fcNext4rain = self.root.get_object("forecastNextRain4")
        self.fcNext4month = self.root.get_object("forecastNextMonth4")
        self.fcNext4week = self.root.get_object("forecastNextWeek4")
        
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
    
    
    #Forecast
    def triggerForecastOpen(self,w):
        self.windowForecast.show_all()

    def triggerForecastClose(self,w):
        self.windowForecast.hide()
    
    #Forecast Next days
    def triggerForecastNextOpen(self,w):
        self.windowForecastNext.show_all()

    def triggerForecastNextClose(self,w):
        self.windowForecastNext.hide()
        
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
        self.windowMJpeg.show_all()
        self.textMJpegStream.set_text("Camera " + str(id))
        self.id=id
        self.stream = self.config['cameras']['camImage' + str(id)]
        self.threadCamera = threading.Thread(target=self.startCameraPreview)
        self.stateCamera = True
        self.threadCamera.daemon=True 
        self.threadCamera.start()          
        
    def startCameraPreview(self):
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
    
    #Mode Live (More CPU Usage)
    def triggerMJpegCamera(self,w,id):
        self.windowMJpeg.show_all()
        self.textMJpegStream.set_text("Camera " + str(id))
        self.id=id
        self.stream = self.config['cameras']['cam' + str(id)]
        self.threadCamera = threading.Thread(target=self.startCamera)
        self.stateCamera = True
        self.threadCamera.daemon=True 
        self.threadCamera.start()
        
    def startCamera(self):
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
            print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Cant't read mailbox datas")
        try:
            dateToday=self.readJson(self.config['system']['cache'] + "date.json")
            today = dt.now()
            self.dataDate.set_text(str(dateToday["today"]))
            self.dataTime.set_text(today.strftime("%H:%M"))
            self.textToday.set_text(dateToday["today_text"])
        except:
            print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Cant't read date and time datas")
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
            print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Cant't read todo datas")
        try:        
            radio=self.readJson(self.config['system']['cache'] + "radio.json")
            self.radioStreamUrl=radio["url"]
            self.radioInfo=radio["title"] + " - " + radio["songTitle"]
        except:
            print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Cant't read radio datas")
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
            print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Cant't read weather datas")
        try:
            forecast=self.readJson(self.config['system']['cache'] + "forecast.json")
            if forecast["today"][0]["ico"] != self.weatherUrlFC1 :
                imageData=self.getImageResize(forecast["today"][0]["ico"],self.forecastResize,self.forecastResize)
                self.weatherUrlFC1 = forecast["today"][0]["ico"]
                self.fcToday1ico.set_from_pixbuf(Pixbuf.new_from_file(imageData))
            self.fcToday1temp.set_text(forecast["today"][0]['temp'])
            self.fcToday1feel.set_text(forecast["today"][0]['feel'])
            self.fcToday1min.set_text(forecast["today"][0]['min'])
            self.fcToday1max.set_text(forecast["today"][0]['max'])
            self.fcToday1wind.set_text(forecast["today"][0]['winds'])
            self.fcToday1clouds.set_text(forecast["today"][0]['clouds'])
            self.fcToday1snow.set_text(forecast["today"][0]['snow'])
            self.fcToday1rain.set_text(forecast["today"][0]['rain'])
            self.fcToday1humidity.set_text(forecast["today"][0]['humidity'])
            self.fcToday1details.set_text(forecast["today"][0]['details'])
            if self.fcToday1time:
                self.fcToday1time.set_text(forecast["today"][0]['hour']+"H")
                
            
            if forecast["today"][1]["ico"] != self.weatherUrlFC2 :
                imageData=self.getImageResize(forecast["today"][1]["ico"],self.forecastResize,self.forecastResize)
                self.weatherUrlFC2 = forecast["today"][1]["ico"]
                self.fcToday2ico.set_from_pixbuf(Pixbuf.new_from_file(imageData))
            self.fcToday2temp.set_text(forecast["today"][1]['temp'])
            self.fcToday2feel.set_text(forecast["today"][1]['feel'])
            self.fcToday2min.set_text(forecast["today"][1]['min'])
            self.fcToday2max.set_text(forecast["today"][1]['max'])
            self.fcToday2wind.set_text(forecast["today"][1]['winds'])
            self.fcToday2clouds.set_text(forecast["today"][1]['clouds'])
            self.fcToday2snow.set_text(forecast["today"][1]['snow'])
            self.fcToday2rain.set_text(forecast["today"][1]['rain'])
            self.fcToday2humidity.set_text(forecast["today"][1]['humidity'])
            self.fcToday2details.set_text(forecast["today"][1]['details'])
            if self.fcToday2time:
                self.fcToday2time.set_text(forecast["today"][1]['hour']+"H")
            
            
            if forecast["today"][2]["ico"] != self.weatherUrlFC3 :
                imageData=self.getImageResize(forecast["today"][2]["ico"],self.forecastResize,self.forecastResize)
                self.weatherUrlFC3 = forecast["today"][2]["ico"]
                self.fcToday3ico.set_from_pixbuf(Pixbuf.new_from_file(imageData))
            self.fcToday3temp.set_text(forecast["today"][2]['temp'])
            self.fcToday3feel.set_text(forecast["today"][2]['feel'])
            self.fcToday3min.set_text(forecast["today"][2]['min'])
            self.fcToday3max.set_text(forecast["today"][2]['max'])
            self.fcToday3wind.set_text(forecast["today"][2]['winds'])
            self.fcToday3clouds.set_text(forecast["today"][2]['clouds'])
            self.fcToday3snow.set_text(forecast["today"][2]['snow'])
            self.fcToday3rain.set_text(forecast["today"][2]['rain'])
            self.fcToday3humidity.set_text(forecast["today"][2]['humidity'])
            self.fcToday3details.set_text(forecast["today"][2]['details'])
            if self.fcToday3time:
                self.fcToday3time.set_text(forecast["today"][2]['hour']+"H")
            
            
            if forecast["today"][3]["ico"] != self.weatherUrlFC4 :
                imageData=self.getImageResize(forecast["today"][3]["ico"],self.forecastResize,self.forecastResize)
                self.weatherUrlFC4 = forecast["today"][3]["ico"]
                self.fcToday4ico.set_from_pixbuf(Pixbuf.new_from_file(imageData))
            self.fcToday4temp.set_text(forecast["today"][3]['temp'])
            self.fcToday4feel.set_text(forecast["today"][3]['feel'])
            self.fcToday4min.set_text(forecast["today"][3]['min'])
            self.fcToday4max.set_text(forecast["today"][3]['max'])
            self.fcToday4wind.set_text(forecast["today"][3]['winds'])
            self.fcToday4clouds.set_text(forecast["today"][3]['clouds'])
            self.fcToday4snow.set_text(forecast["today"][3]['snow'])
            self.fcToday4rain.set_text(forecast["today"][3]['rain'])
            self.fcToday4humidity.set_text(forecast["today"][3]['humidity'])
            self.fcToday4details.set_text(forecast["today"][3]['details'])
            if self.fcToday4time:
                self.fcToday4time.set_text(forecast["today"][3]['hour']+"H")
            
            
            if forecast["today"][4]["ico"] != self.weatherUrlFC5 :
                imageData=self.getImageResize(forecast["today"][4]["ico"],self.forecastResize,self.forecastResize)
                self.weatherUrlFC5 = forecast["today"][4]["ico"]
                self.fcToday5ico.set_from_pixbuf(Pixbuf.new_from_file(imageData))
            self.fcToday5temp.set_text(forecast["today"][4]['temp'])
            self.fcToday5feel.set_text(forecast["today"][4]['feel'])
            self.fcToday5min.set_text(forecast["today"][4]['min'])
            self.fcToday5max.set_text(forecast["today"][4]['max'])
            self.fcToday5wind.set_text(forecast["today"][4]['winds'])
            self.fcToday5clouds.set_text(forecast["today"][4]['clouds'])
            self.fcToday5snow.set_text(forecast["today"][4]['snow'])
            self.fcToday5rain.set_text(forecast["today"][4]['rain'])
            self.fcToday5humidity.set_text(forecast["today"][4]['humidity'])
            self.fcToday5details.set_text(forecast["today"][4]['details'])
            if self.fcToday5time:
                self.fcToday5time.set_text(forecast["today"][4]['hour']+"H")
            
            self.fcNext1day.set_text(forecast["next"][0]['day'])
            self.fcNext1min.set_text(forecast["next"][0]['min'])
            self.fcNext1max.set_text(forecast["next"][0]['max'])
            self.fcNext1snow.set_text(forecast["next"][0]['snow'])
            self.fcNext1rain.set_text(forecast["next"][0]['rain'])
            if self.fcNext1week:
                self.fcNext1week.set_text(forecast["next"][0]['text_day'])
                self.fcNext1month.set_text(forecast["next"][0]['text_month'])         
            self.fcNext2day.set_text(forecast["next"][1]['day'])
            self.fcNext2min.set_text(forecast["next"][1]['min'])
            self.fcNext2max.set_text(forecast["next"][1]['max'])
            self.fcNext2snow.set_text(forecast["next"][1]['snow'])
            self.fcNext2rain.set_text(forecast["next"][1]['rain']) 
            if self.fcNext2week:
                self.fcNext2week.set_text(forecast["next"][1]['text_day'])
                self.fcNext2month.set_text(forecast["next"][1]['text_month'])        
            self.fcNext3day.set_text(forecast["next"][2]['day'])
            self.fcNext3min.set_text(forecast["next"][2]['min'])
            self.fcNext3max.set_text(forecast["next"][2]['max'])
            self.fcNext3snow.set_text(forecast["next"][2]['snow'])
            self.fcNext3rain.set_text(forecast["next"][2]['rain'])
            if self.fcNext3week:
                self.fcNext3week.set_text(forecast["next"][2]['text_day'])
                self.fcNext3month.set_text(forecast["next"][2]['text_month'])         
            self.fcNext4day.set_text(forecast["next"][3]['day'])
            self.fcNext4min.set_text(forecast["next"][3]['min'])
            self.fcNext4max.set_text(forecast["next"][3]['max'])
            self.fcNext4snow.set_text(forecast["next"][3]['snow'])
            self.fcNext4rain.set_text(forecast["next"][3]['rain'])
            if self.fcNext4week:
                self.fcNext4week.set_text(forecast["next"][3]['text_day'])
                self.fcNext4month.set_text(forecast["next"][3]['text_month']) 
        except:
            print(dt.now().strftime("%m-%d-%y %H:%M > ") + "Cant't read forecast datas")
            
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
        self.statePlayer = False
        self.vlcInstance = vlc.Instance("--no-xlib --quiet")
        self.player = self.vlcInstance.media_player_new()        
        self.player.set_mrl(self.radioStreamUrl)
        self.player.audio_set_volume(100)
        
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