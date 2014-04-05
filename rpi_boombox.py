#!/usr/bin/python

#import logging
import pylirc
import mpd
import os
import time
import re

import feedparser

from time import sleep, clock
import spidev
import VFD

from mpd import MPDClient, MPDError, CommandError

#logging.basicConfig(filename='vfd.log',level=logging.INFO)

keep_running = 1


starttime=clock() # used to refresh display

# General Menu processing class
class Menu():
    def __init__(self):
        self.load_playlist = 0

        self.current_col = 0
        self.current_row = 0

        # current_display: m=mpd, t=time, w=weather
        self.running_pgm = "m"

        # dictionary of menu choices, by level of how deep into the menu
        self.menutext = {"1.":"mpd time weather"}   

        self.lvl = "1."  # menu level 
        # three choices at cursor column 0, 4 and 9
        self.lvl1_cursors={0:1, 4:2, 9:3}

        self.current_cursors = self.lvl1_cursors
        self.this_cursor = self.current_cursors[self.current_col]
        self.vol = 0

    def show_menu(self):
        #print ("in show_menu")
        thistext=self.menutext[self.lvl]
        vfd.blank_lines()
        vfd.setCursor(0,0)
        vfd.text(thistext)
        vfd.setCursor(0,0)
        vfd.blink_on()
        self.current_col=0
        self.current_row=0
        if self.lvl == "1.":
           self.current_cursors=self.lvl1_cursors
        elif self.lvl == "1.1":
             self.current_cursors=self.lvl1_1_cursors

    def nav(self, direction):
        #get the current level cursor assignments for menu choices
        self.this_cursor = self.current_cursors[self.current_col] 
        
        if direction == "R":  
           self.this_cursor = self.this_cursor + 1
        elif direction == "L":
           self.this_cursor = self.this_cursor - 1  
        if self.this_cursor < 1:
           self.this_cursor = 1
        if self.this_cursor > len(self.current_cursors):
           self.this_cursor = len(self.current_cursors)
        
        for col, nbr in self.current_cursors.items():
            if nbr == self.this_cursor:
               self.current_col = col
        vfd.setCursor(self.current_col,0) 

class PollerError(Exception):
    """Fatal error in poller."""

class MPDPoller(object):
    def __init__(self, host="localhost", port="6600", password=None):
        self._host = host
        self._port = port
        self._password = password
        self._client = MPDClient()
        self.song = "song"

    def connect(self):
        try:
            self._client.connect(self._host, self._port)

        # Catch socket errors
        except IOError as (errno, strerror):
            raise PollerError("Could not connect to '%s': %s" %
                              (self._host, strerror))

        # Catch all other possible errors
        # ConnectionError and ProtocolError are always fatal.  Others may not
        # be, but we don't know how to handle them here, so treat them as if
        # they are instead of ignoring them.
        except MPDError as e:
            raise PollerError("Could not connect to '%s': %s" %
                              (self._host, e))

        if self._password:
            try:
                self._client.password(self._password)

            # Catch errors with the password command (e.g., wrong password)
            except CommandError as e:
                raise PollerError("Could not connect to '%s': "
                                  "password commmand failed: %s" %
                                  (self._host, e))

            # Catch all other possible errors
            except (MPDError, IOError) as e:
                raise PollerError("Could not connect to '%s': "
                                  "error with password command: %s" %
                                  (self._host, e))

    def disconnect(self):
        # Try to tell MPD we're closing the connection first
        try:
            self._client.close()

        # If that fails, don't worry, just ignore it and disconnect
        except (MPDError, IOError):
            pass

        try:
            self._client.disconnect()

        # Disconnecting failed, so use a new client object instead
        # This should never happen.  If it does, something is seriously broken,
        # and the client object shouldn't be trusted to be re-used.
        except (MPDError, IOError):
            self._client = MPDClient()

    def poll(self):
        try:
            self.song = self._client.currentsong()

        # Couldn't get the current song, so try reconnecting and retrying
        except (MPDError, IOError):
            # No error handling required here
            # Our disconnect function catches all exceptions, and therefore
            # should never raise any.
            self.disconnect()

            try:
                self.connect()

            # Reconnecting failed
            except PollerError as e:
                raise PollerError("Reconnecting failed: %s" % e)

            try:
                self.song = self._client.currentsong()

            # Failed again, just give up
            except (MPDError, IOError) as e:
                raise PollerError("Couldn't retrieve current song: %s" % e)

        # Hurray!  We got the current song without any errors!
        #print self.song
        




blocking = 0;   #set to 1 for blocking = on
conf = "/home/pi/scripts/lirc.config"

pylirc.init("pylirc", conf, blocking)

# initialize mpc client
mpc = mpd.MPDClient()

# initalize SPI
vfd=VFD.SPI()

vfd.init_VFD()

#initialize Menu processing
menu=Menu()
#menu.init_Menu()

#initialize Poller
poller = MPDPoller()
poller.connect()

def mpd_info():
        menu.running_pgm = "m"
	#song=mpc.currentsong()
        poller.poll()
        song = poller.song
	#print song
        #status=mpc.status()
        #vol=status['volume']
        #print vol
 # Display the song title and author on the VFD
        vfd.blank_lines()
        sleep (0.1)
                
        if 'title' in song:
            SongTitle = song['title']
        elif 'file' in song:
            SongTitle = song['file']
        else:
            SongTitle = 'Song Title Unknown'

        if 'name' in song:
            Station = song['name']
        else:
            Station = 'Station Unknown'

        a = re.split(": | - ",SongTitle)
     
        #print(a[0])
        vfd.setCursor(0,0)
        vfd.text(a[0])
        
        if len(a)>1:
           #print(a[1])
           vfd.setCursor(0,1)
           # Send SongTitle to VFD
           vfd.text(a[1])

        

def mpd_playlist(pl):
    mpc.clear()
    mpc.load(pl)
    mpc.play(0)
    mpd_info()

def select_menu():
    #print ("this_cursor")
    #print (menu.this_cursor)
    next_lvl=menu.lvl+str(menu.this_cursor)
    ret_val = menu.menutext.get(next_lvl, None)
    
    if ret_val == None:
        this_rtn = run_rtn.get(next_lvl, None)
    
    # need to call the routine by reference
        menu.lvl = "1."
        menu.this_cursor = menu.current_cursors[0]
        vfd.blink_off()
        this_rtn()
    else:
       # descend into the menu tree
       menu.lvl = next_lvl
       #print ("next lvl")
       #print menu.lvl
       
       menu.show_menu()
    
def prev():
    mpc.previous()
    mpd_info()  

def next():
    mpc.next()
    mpd_info()

def incr_vol():
    status=mpc.status()
    vol=status['volume']
    if int(vol) >= 95:
        vol=95
    vfd.volume(int(vol),5)
    mpc.setvol(int(vol)+5)

def decr_vol():
    status=mpc.status()
    vol=status['volume']
    if int(vol) <= 5:
        vol = 5
    vfd.volume(int(vol),-5)
    mpc.setvol(int(vol)-5)

def time_info():
    #print ("in time info")
    vfd.blank_lines()
    vfd.setCursor(0,0)
    vfd.text(time.strftime(" %B %d %I:%M %p", time.localtime()))
    menu.running_pgm = "t"

def weather_info():
    d = feedparser.parse('http://www.wunderground.com/auto/rss_full/CA/Pleasant_Hill.xml')
    line =  str(d.entries[0].summary)
    line = line.replace(":","|")
    a = line.split("|")
    #print "Printing a"	
    #print a
	
    #print "Printing mytemp:"
    mytemp = str(a[1])
    mytemp = mytemp.replace("&#176;", " ")
    mytemp = mytemp.replace("&deg;", " ")
    mytemp = mytemp.replace(" ", "")
    mytemp = mytemp.split("/")
		
    b = a[11].split("/")
    #print a[1]	# Temperature Example: 51.7&#176;F / 10.9&#176;C
    #print mytemp[0]
    #print a[7]	# Conditions
    #print a[5]	# Barometer
    #print a[3]	# Humidity
    #print b[0]	# Wind Speed - also contains image source, removed by split into array b
    #print a[9]	# Wind Direction

    remove_spcs = mytemp[0]+a[7]+a[3]+b[0]+a[9]  # without Barometer
    to_VFD = remove_spcs.replace("  ","|")
    #print to_VFD
    vfd.blank_lines()
    vfd.setCursor(0,0)
    vfd.text("Now: Pleasant Hill")
    vfd.setCursor(0,1)
    vfd.text(to_VFD)
    
    # set weather to show on the display
    menu.running_pgm = "w"
  

def current_display():
    #tstamp = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())
    #logging.info(tstamp)
    
    #print menu.running_pgm
    
    if menu.running_pgm == "m":      # we are displaying mpd info now
       mpd_info()

    if menu.running_pgm == "t":      #get the time and display it
       time_info()

    if menu.running_pgm == "w":      # now we are showing the weather
       weather_info()


def quit():
    vfd.blank_lines()
    vfd.setCursor(0,0)
    vfd.text("<= Shutting Down! =>")
    vfd.setCursor(0,1)
    vfd.text("Off at red light out")
    mpc.setvol(5)
    global keep_running
    keep_running=0
    

commands={
	"play":		lambda: mpc.play(),
	"pause":	lambda: mpc.pause(),
	"prev":		lambda: prev(),
	"next":		lambda: next(),
	"random":	lambda: random(),
	"quit":		lambda: quit(),
	"voldown":	lambda: decr_vol(),
	"volup":	lambda: incr_vol(),
        "left":         lambda: menu.nav("L"),
        "right":        lambda: menu.nav("R"),
        "enter":        lambda: select_menu(),
	"bright":	lambda: vfd.brightnessAdjust(),
	"playlist1":	lambda: mpd_playlist("webstream"),
	"playlist2":	lambda: mpd_playlist("classical_sd"),
	"playlist3":	lambda: mpd_playlist("newage"),
	"playlist4":	lambda: mpd_playlist("rock"),
	"5":		lambda: search(5),
	"6":		lambda: search(6),
	"7":		lambda: search(7),
	"8":		lambda: search(8),
	"9":		lambda: search(9),
	"back":		lambda: mpd_info(),
        "setup":        lambda: menu.show_menu()

}

# dictionary of methods to run when menu choice is made                
run_rtn = {"1.1":mpd_info,
           "1.2":time_info,
           "1.3":weather_info
          }

#print("<==== Mainline Starts ====>")

while keep_running:  
        sleep(.25)      # keep the loop from eating up CPU time!
        if  (time.time() - starttime) >= 15:        # refresh the screen every 15 seconds
            starttime=time.time()
            current_display()
            
            
	presses=pylirc.nextcode(1)
	if presses == None:
           continue    
        
	for press in presses:
		try:
			cmd=commands[press["config"]]
		except KeyError:
                        print "getting KeyError"
			continue
		try:
			mpc.connect("localhost", 6600)
			cmd()
			mpc.disconnect()
		except mpd.ConnectionError:
			pass

pylirc.exit()
os.system("sudo shutdown -h now")


