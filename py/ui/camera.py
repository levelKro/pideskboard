import json, requests, gi, re, datetime, io, time
gi.require_version("Gtk", "3.0")
gi.require_version('Gst', '1.0')
from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Gst
from gi.repository import GdkPixbuf
from gi.repository.GdkPixbuf import Pixbuf
import cv2
import numpy as np

class App():
    def __init__(self):
        self.stream = 'http://192.168.0.100:8090/camera3'
        capture_video = cv2.VideoCapture(self.stream)
        while(True):
            ret, img = capture_video.read()
            imgResize = cv2.resize(img, (320, 240))
            cv2.imshow("MonitorStream", imgResize) # Monitor
            
            imageWorked = np.array(imgResize).ravel()
            print(imageWorked.size)
            imagePixbuf = GdkPixbuf.Pixbuf.new_from_data(imageWorked,GdkPixbuf.Colorspace.RGB, False, 8, 320, 240, 3*320)
    #           self.imageMJpegStream.set_from_pixbuf(imagePixbuf)

            
            if cv2.waitKey(10) == ord('q'):
                #exit(0)
                break
            
app=App()            