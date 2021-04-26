#PiDeskboard by Mathieu Légaré <levelkro@yahoo.ca> https://levelkro.com
#

import json, requests, gi, re, datetime
gi.require_version("Gtk", "3.0")
gi.require_version('Gst', '1.0')
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gst
from gi.repository.GdkPixbuf import Pixbuf

# Functions
def getApi(action):
    jsonUrl = "http://localhost/api.php?a="+ action
    url = requests.get(jsonUrl)
    return url.text

def getDatas():
    jsonUrl = "http://localhost/api.php?a=datas"
    url = requests.get(jsonUrl)
    return json.loads(url.text)

def getWeatherIcon(url):
    response = requests.get(url)
    fname = url.split("/")[-1]
    f = open(fname, "wb")
    f.write(response.content)
    f.close()
    response.close()
    return fname

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext

#Main Class
class App():
    def __init__(self):
        #pre-init
        Gst.init(None)
        self.weatherUrl = ""
        self.count = 0        
        self.statePlayer = False;
        self.defaultPath = "/home/pi/pideskboard/py/ui/" #fix for autorun
        self.radioStreamUrl = "http://radio.levelkro.net:8000/1"; #default value
        self.imageStop = Gtk.Image.new_from_file(self.defaultPath + "stop.png")
        self.imagePlay = Gtk.Image.new_from_file(self.defaultPath + "play.png")
        self.imagePause = Gtk.Image.new_from_file(self.defaultPath + "pause.png")
        self.imageEject = Gtk.Image.new_from_file(self.defaultPath + "eject.png")
        self.imageIPCam = Gtk.Image.new_from_file(self.defaultPath + "ipcam.png")
        self.imageCtrl = Gtk.Image.new_from_file(self.defaultPath + "ctrl.png")
        self.gibberish = "Loading . . ."
        self.gibberishShadow = "Loading . . ."
        self.a = 0
        self.z = 20
        
        #init-start
        self.root = Gtk.Builder()
        self.root.add_from_file(self.defaultPath + "deskboard.glade")
        self.window = self.root.get_object("window")
        self.window.set_default_size(480, 320)        
        self.window.set_title("PiDeskboard in Python")
        self.window.connect("destroy", Gtk.main_quit, "WM destroy")
        self.window.show_all()
        self.windowMJpeg = self.root.get_object("windowMJpeg")
        self.windowCtrl = self.root.get_object("windowControl")

        # Names to GUI objects
        self.textToday =  self.root.get_object("textToday")
        
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
        
        self.listToday =  self.root.get_object("listToday")
        self.templateTextA = self.root.get_object("templateTextA")
        
        self.playerAction = self.root.get_object("playerAction")
        self.buttonPlayerAction = self.root.get_object("buttonPlayerAction")
        self.dataPlayerTime = self.root.get_object("dataPlayerTime")
        self.dataPlayerDetails = self.root.get_object("dataPlayerDetails")
        
        self.placeButtonCtrl = self.root.get_object("placeButtonCtrl")
        self.ButtonCtrlClose = self.root.get_object("buttonCtrlClose")
        self.ButtonCtrlClose.connect("clicked", self.triggerCtrlClose)
        self.buttonCtrlPoweroff = self.root.get_object("buttonCtrlPoweroff")
        self.buttonCtrlPoweroff.connect("clicked", self.triggerPoweroff)
        self.buttonCtrlReboot = self.root.get_object("buttonCtrlReboot")
        self.buttonCtrlReboot.connect("clicked", self.triggerReboot)
        self.buttonCtrlBluetooth = self.root.get_object("buttonCtrlBluetooth")
        self.buttonCtrlBluetooth.connect("clicked", self.triggerBluetooth)
        
        self.placeButtonCameras = self.root.get_object("placeButtonCameras")
        self.ButtonMJpegClose = self.root.get_object("buttonMJpegClose")
        self.ButtonMJpegClose.connect("clicked", self.triggerMJpegClose)

        #post-init

        # Button for controles options    
        self.buttonCtrl = Gtk.Button()
        self.buttonCtrl.add(self.imageCtrl)
        self.buttonCtrl.connect("clicked", self.triggerCtrl)
        self.buttonCtrl.props.relief = Gtk.ReliefStyle.NONE
        self.placeButtonCtrl.add(self.buttonCtrl)
        self.placeButtonCtrl.show_all()
        
        # Music Player
        # MP: Cleanup
        for row in self.playerAction:
            self.playerAction.remove(row)
            
        # MP: Create Play/Stop button    
        self.buttonPlayerAction = Gtk.Button()
        self.buttonPlayerAction.add(self.imagePlay)
        self.buttonPlayerAction.connect("clicked", self.triggerPlayer)
        self.buttonPlayerAction.props.relief = Gtk.ReliefStyle.NONE
        self.playerAction.add(self.buttonPlayerAction)
        self.playerAction.show_all()
        
        # MP: Init Player and set it to Kore Radio
        Gst.init_check(None)
        self.IS_GST010 = Gst.version()[0] == 0
        self.player = Gst.ElementFactory.make("playbin", "player")
        self.player.set_property("uri", self.radioStreamUrl)
        self.player.props.buffer_duration = 5 * Gst.SECOND
        self.bus = self.player.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect("message", self.on_message)
        self.player.connect("about-to-finish",  self.on_finished) 

        # Updates datas
        self.setUpdates()
        GLib.timeout_add_seconds(5, self.setUpdates)

        #init-end
        self.startMarquee()        
        Gtk.main()

    # Tasks functions
        
    def triggerPoweroff(self,w):
        self.tmp = getApi("poweroff")
        
    def triggerReboot(self,w):
        self.tmp = getApi("reboot")
        
    def triggerBluetooth(self,w):
        self.tmp = getApi("bluetooth")
        
    def triggerCtrlClose(self,w):
        self.windowCtrl.hide() 
    
    def triggerCtrl(self,w):
        self.windowCtrl.show_all()
        
    def triggerMJpegClose(self,w):
        self.windowMJpeg.hide()    
        
    def setUpdates(self):
        # Updates datas
        jsonDatas = getDatas()
        attText = self.templateTextA.get_attributes()
        
        self.textToday.set_text(jsonDatas["text_today"])
        self.radioStreamUrl=self.gibberishShadow=jsonDatas["radio"]["url"]
        #Player Web Radio            
        self.gibberishShadow=jsonDatas["radio"]["title"] + " - " + jsonDatas["radio"]["songTitle"]
        if(self.statePlayer == False):
            self.gibberish=self.gibberishShadow
        #date & time
        self.dataDate.set_text(jsonDatas["date"])
        self.dataTime.set_text(jsonDatas["time"])
        #mailbox
        self.dataMailboxUnread.set_text(str(jsonDatas["mailbox"]["unread"]))
        self.dataMailboxRead.set_text(str(jsonDatas["mailbox"]["read"]))
        #weather
        self.dataWeatherTemp.set_text(jsonDatas["weather"]["temp"])
        self.dataWeatherFeel.set_text(jsonDatas["weather"]["feel"])
        self.dataWeatherTempMin.set_text(jsonDatas["weather"]["min"])
        self.dataWeatherTempMax.set_text(jsonDatas["weather"]["max"])
        self.dataWeatherClouds.set_text(str(jsonDatas["weather"]["clouds"]) + "%")
        self.dataWeatherDetails.set_text(jsonDatas["weather"]["name"])        
        rain = "rain" in jsonDatas["weather"]
        snow = "snow" in jsonDatas["weather"]
        if rain:
            self.dataWeatherRain.set_text(str(jsonDatas["weather"]["rain"]) + "mm")
        else:
            self.dataWeatherRain.set_text("-")
        if snow:    
            self.dataWeatherSnow.set_text(str(jsonDatas["weather"]["snow"]) + "cm")
        else:
            self.dataWeatherSnow.set_text("-")

        if jsonDatas["weather"]["ico"] != self.weatherUrl :
            imageData=getWeatherIcon(jsonDatas["weather"]["ico"])
            self.weatherUrl = jsonDatas["weather"]["ico"]
            self.dataWeatherIcon.set_from_pixbuf(Pixbuf.new_from_file(imageData))            

        #Todo today
        for row in self.listToday:
            self.listToday.remove(row)

        row = Gtk.Box()
        for todoItem in jsonDatas["todo"]:
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            toAdd = Gtk.Label()
            toAdd.set_text("- " + cleanhtml(todoItem))
            toAdd.set_attributes(attText)
            box.pack_start(toAdd, True, True, 0)
            row.add(box)
            self.listToday.add(row)
            
        self.listToday.show_all()
        
        #End
        return True

    # Music Player
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
        elif t == Gst.MessageType.BUFFERING:
            self.a = -1
            self.z = 16
            percent = message.parse_buffering()
            #print("Buffering: %s" % percent)
            self.gibberish="Buffer: " + str(percent) + "%"
            if percent == 100:
                self.buttonPlayerAction.get_child().set_from_file(self.defaultPath + "stop.png")
                GLib.timeout_add(1000, self.playerSongShadow)
            else:
                self.buttonPlayerAction.get_child().set_from_file(self.defaultPath + "pause.png")
        #else:
        #    print("Debug message: %s" % t)
            
    def playerSongShadow(self):
        self.gibberish=self.gibberishShadow
        
    def on_finished(self, player):
        self.statePlayer = False;
        self.buttonPlayerAction.get_child().set_from_file(self.defaultPath + "play.png")
        self.dataPlayerTime.set_text("0:00")
 
    # Marquee effect
    def marquee(self, text):
        if self.a < len(text):
            self.a = self.a + 1
            self.z = self.z + 1
            if self.a >= len(text):
                self.a = 0
                self.z = 17
        return str(text[self.a:self.z])

    def displayMarquee(self):
        self.dataPlayerDetails.set_label(self.marquee(self.gibberish))
        return True

    def startMarquee(self):
        GLib.timeout_add(500, self.displayMarquee)

# End of Class

# Run the main app
app=App()