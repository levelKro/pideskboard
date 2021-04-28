#PiDeskboard by Mathieu Légaré <levelkro@yahoo.ca> https://levelkro.com
#
import json, requests, gi, re, datetime, time, configparser
gi.require_version("Gtk", "3.0")
gi.require_version('Gst', '1.0')
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gdk
#from gi.repository import GObject
from gi.repository import Gst
from gi.repository import GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf, InterpType
import cv2
import numpy as np
import threading
import cairo

#Main Class
class Deskboard():
    def __init__(self):
        #pre-init
        Gst.init(None)
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

#def getDatas():
#    jsonUrl = "http://localhost/api.php?a=datas"
#    url = requests.get(jsonUrl)
#    return json.loads(url.text)

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
    
    def imageText(self,pixbuf, text, x, y):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, pixbuf.get_width(), pixbuf.get_height())
        context = cairo.Context(surface)
        Gdk.cairo_set_source_pixbuf(context, pixbuf, 0, 0)
        context.paint()
        fontsize= 10
        context.move_to(x, y+fontsize)
        context.set_font_size(fontsize)
        context.set_source_rgba(255,255,255,1)
        context.show_text(text)
        surface= context.get_target()
        pixbuf= Gdk.pixbuf_get_from_surface(surface, 0, 0, surface.get_width(), surface.get_height())
        return pixbuf

    # Marquee effect
    def marquee(self, text):
        if self.a < len(text):
            self.a = self.a + 1
            self.z = self.z + 1
            if self.a >= len(text):
                self.a = 0
                self.z = 20
        return str(text[self.a:self.z])

    def displayMarquee(self):
        self.dataPlayerDetails.set_label(self.marquee(self.gibberish))
        return True

    def startMarquee(self):
        GLib.timeout_add(500, self.displayMarquee)

    def loadConfig(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.weatherUrl = ""
        self.count = 0        
        self.statePlayer = False
        self.stateCamera = False
        self.radioStreamUrl = "http://radio.levelkro.net:8000/1"; #default value, refreshed with API
        self.defaultPath = self.config['system']['path']
        self.gibberish = "Loading . . ."
        self.gibberishShadow = "Loading . . ."
        if self.config['system']['api'] is not None:
            self.apiUrl = self.config['system']['api']
        else:
            self.apiUrl = "http://localhost/api.php?a="
        self.a = 0
        self.z = 20
        
    def saveConfig(self):
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
            
    def loadUI(self):
        self.root = Gtk.Builder()
        self.root.add_from_file(self.defaultPath + "deskboard.glade")
        self.window = self.root.get_object("window")
        self.window.set_default_size(480, 320)        
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
        # add config file for this
        i=1
        self.buttonIPCam = []
        while i <= 5:
            if 'cam' + str(i) in self.config['cameras']:
                thisTmp = Gtk.Button()
                thisTmp.add(Gtk.Image.new_from_file(self.defaultPath + "cam" + str(i) + ".png"))
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

    #Cameras MJPEG
    def triggerMJpegOpen(self,w):
        self.imageMJpegStream.set_from_file(self.defaultPath + "nocamera.jpg")
        self.windowMJpeg.show_all()
        self.stream = ''
    
    def triggerMJpegCameraPreview(self,w,id):
        self.windowMJpeg.show_all()
        self.textMJpegStream.set_text("Camera " + str(id))
        self.id=id
        self.stream = self.config['cameras']['camImage' + str(id)]
        self.thread = threading.Thread(target=self.startCameraPreview)
        self.stateCamera = True
        self.thread.daemon=True 
        self.thread.start()          
    
    def startCameraPreview(self):
        #Mode Preview
        id=self.id
        error = 0
        while(True):
            if id != self.id or self.stateCamera == False:
                GLib.idle_add(self.imageMJpegStream.set_from_file,self.defaultPath + "nocamera.jpg")
                break
            thisFrame = self.getImage(self.stream)
            thisFrameFile = Pixbuf.new_from_file(thisFrame)
            if thisFrameFile is None and error >= 3:
                GLib.idle_add(self.imageMJpegStream.set_from_file,self.defaultPath + "nocamera.jpg")
                break
            elif thisFrameFile is None:
                error += 1
            else:
                error = 0
                thisFrameFileResize = thisFrameFile.scale_simple(320, 240, InterpType.BILINEAR)
                dateTimeObj = datetime.datetime.now()
                dateString = dateTimeObj.strftime("%H:%M:%S")
                thisFrameFileTimestamp = self.imageText(thisFrameFileResize,dateString,260,10)
                GLib.idle_add(self.imageMJpegStream.set_from_pixbuf,thisFrameFileTimestamp)
            time.sleep(5)
   
    def triggerMJpegCamera(self,w,id):
        self.windowMJpeg.show_all()
        self.textMJpegStream.set_text("Camera " + str(id))
        self.id=id
        self.stream = self.config['cameras']['cam' + str(id)]
        self.thread = threading.Thread(target=self.startCamera)
        self.stateCamera = True
        self.thread.daemon=True 
        self.thread.start()        
    
    def startCamera(self):
        #Mode Live
        id=self.id
        jump = 0
        self.capture_video = cv2.VideoCapture(self.stream)
        while(True):
            if id != self.id or self.stateCamera == False:
                GLib.idle_add(self.imageMJpegStream.set_from_file,self.defaultPath + "nocamera.jpg")
                break
            ret, img = self.capture_video.read()
            if img is None:
                GLib.idle_add(self.imageMJpegStream.set_from_file,self.defaultPath + "nocamera.jpg")
                break
            if jump == 0:
                jump = 1
                img=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                imgResize = cv2.resize(img, (320, 240))
                imageWorked = np.array(imgResize).ravel()
                imagePixbuf = GdkPixbuf.Pixbuf.new_from_data(imageWorked,GdkPixbuf.Colorspace.RGB, False, 8, 320, 240, 3*320)
                dateTimeObj = datetime.datetime.now()
                dateString = dateTimeObj.strftime("%H:%M:%S")
                imagePixbufTimestamp = self.imageText(imagePixbuf,dateString,260,10)                
                GLib.idle_add(self.imageMJpegStream.set_from_pixbuf,imagePixbufTimestam)
            elif jump >= 5:
                jump = 0
            else:
                jump += 1
            #time.sleep(0.2) 
        
    def triggerMJpegClose(self,w):
        self.stateCamera=False
        self.id = 0
        self.windowMJpeg.hide()
        
    #Controls
    def triggerCtrl(self,w):
        self.windowCtrl.show_all()
    def triggerPoweroff(self,w):
        self.tmp = self.getApi("poweroff")
    def triggerReboot(self,w):
        self.tmp = self.getApi("reboot")
    def triggerRestart(self,w):
        self.tmp = self.getApi("restart")
    def triggerBluetooth(self,w):
        self.tmp = self.getApi("bluetooth")
    def triggerCtrlClose(self,w):
        self.windowCtrl.hide()      

    #Updates
    def setUpdates(self):
        jsonDatas = json.loads(self.getApi("datas"))
        attText = self.templateTextA.get_attributes()
        self.textToday.set_text(jsonDatas["text_today"])
        self.radioStreamUrl=jsonDatas["radio"]["url"]
        self.gibberish=jsonDatas["radio"]["title"] + " - " + jsonDatas["radio"]["songTitle"]
        self.dataDate.set_text(jsonDatas["date"])
        self.dataTime.set_text(jsonDatas["time"])
        self.dataMailboxUnread.set_text(str(jsonDatas["mailbox"]["unread"]))
        self.dataMailboxRead.set_text(str(jsonDatas["mailbox"]["read"]))
        self.dataWeatherTemp.set_text(jsonDatas["weather"]["temp"])
        self.dataWeatherFeel.set_text(jsonDatas["weather"]["feel"])
        self.dataWeatherTempMin.set_text(jsonDatas["weather"]["min"])
        self.dataWeatherTempMax.set_text(jsonDatas["weather"]["max"])
        self.dataWeatherClouds.set_text(str(jsonDatas["weather"]["clouds"]) + "%")
        self.dataWeatherDetails.set_text(jsonDatas["weather"]["name"])        
        rain = "rain" in jsonDatas["weather"]
        snow = "snow" in jsonDatas["weather"]
        if rain:
            self.dataWeatherRain.set_text(jsonDatas["weather"]["rain"])
        else:
            self.dataWeatherRain.set_text("-")
        if snow:    
            self.dataWeatherSnow.set_text(jsonDatas["weather"]["snow"])
        else:
            self.dataWeatherSnow.set_text("-")
        if jsonDatas["weather"]["ico"] != self.weatherUrl :
            imageData=self.getImage(jsonDatas["weather"]["ico"])
            self.weatherUrl = jsonDatas["weather"]["ico"]
            self.dataWeatherIcon.set_from_pixbuf(Pixbuf.new_from_file(imageData))            
        for row in self.listToday:
            self.listToday.remove(row)
        row = Gtk.Box()
        for todoItem in jsonDatas["todo"]:
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            toAdd = Gtk.Label()
            toAdd.set_text("- " + self.cleanhtml(todoItem))
            toAdd.set_attributes(attText)
            box.pack_start(toAdd, True, True, 0)
            row.add(box)
            self.listToday.add(row)
        self.listToday.show_all()
        return True

    # Music Player
    def loadPlayer(self):
        self.imagePlayerAction.set_from_file(self.defaultPath + "play.png")
        self.buttonPlayerAction.connect("clicked", self.triggerPlayer)
        self.buttonPlayerAction.show()
        # MP: Init Player
        Gst.init_check(None)
        self.IS_GST010 = Gst.version()[0] == 0
        self.player = Gst.ElementFactory.make("playbin", "player")
        self.player.set_property("uri", self.radioStreamUrl)
        self.player.props.buffer_duration = 5 * Gst.SECOND
        self.bus = self.player.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_message)
        self.player.connect("about-to-finish",  self.on_finished)
        
    def triggerPlayer(self, w):
        if self.statePlayer == False:
            self.statePlayer = True;
            self.buttonPlayerAction.get_child().set_from_file(self.defaultPath + "stop.png")
            self.player.set_property("uri", self.radioStreamUrl)
            self.player.set_state(Gst.State.PLAYING)
            GLib.timeout_add_seconds(1, self.setPlayerUpdates)
        else:
            self.player.set_state(Gst.State.NULL)
            self.statePlayer = False;
            self.buttonPlayerAction.get_child().set_from_file(self.defaultPath + "play.png")
        
    def setPlayerUpdates(self):
        if(self.statePlayer == False):
            return False
        posTimeNano = self.player.query_position(Gst.Format.TIME)[1];
        posTimeSec = float(posTimeNano / Gst.SECOND)
        self.dataPlayerTime.set_text(str(datetime.timedelta(seconds=round(posTimeSec))))
        return True
    
    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.statePlayer = False;
            self.buttonPlayerAction.get_child().set_from_file(self.defaultPath + "play.png")
        elif t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print("Error: %s" % err, debug)
            self.statePlayer = False;
            self.buttonPlayerAction.get_child().set_from_file(self.defaultPath + "play.png")
            
    def on_finished(self, player):
        self.statePlayer = False;
        self.buttonPlayerAction.get_child().set_from_file(self.defaultPath + "play.png")
        self.dataPlayerTime.set_text("0:00:00")
 
# End of Class
# Run the main app
app=Deskboard()        