import spidev
from time import sleep

spi=spidev.SpiDev()


class SPI():
    

    def __init__(self,COLS=20,ROWS=2):

        # instantiate spidev module
        self.setspi()

        # VFD Display Values
        self.COLS = COLS
        self.ROWS = ROWS

        # constants for controlling 
        # display commands
        self.VFD_CLEARDISPLAY = 0x01
        self.VFD_RETURNHOME = 0x02
        self.VFD_ENTRYMODESET = 0x04
        self.VFD_DISPLAYCONTROL = 0x08
        self.VFD_CURSORSHIFT = 0x10
        self.VFD_FUNCTIONSET = 0x20
        self.VFD_SETCGRAMADDR = 0x40
        self.VFD_SETDDRAMADDR = 0x80

        # flags for display entry mode
        self.VFD_ENTRYRIGHT = 0x00
        self.VFD_ENTRYLEFT = 0x02
        self.VFD_ENTRYSHIFTINCREMENT = 0x01
        self.VFD_ENTRYSHIFTDECREMENT = 0x00

        # flags for display on/off control
        self.VFD_DISPLAYON = 0x04
        #    self.VFD_DISPLAYOFF = 0x00
        self.VFD_CURSORON = 0x02
        self.VFD_CURSOROFF = 0x00
        self.VFD_BLINKON = 0x01
        self.VFD_BLINKOFF = 0x00

        # flags for display/cursor shift
        self.VFD_DISPLAYMOVE = 0x08
        self.VFD_CURSORMOVE = 0x00
        self.VFD_MOVERIGHT = 0x04
        self.VFD_MOVELEFT = 0x00

        # flags for function set
        self.VFD_8BITMODE = 0x10
        self.VFD_4BITMODE = 0x00
        self.VFD_2LINE = 0x08
        self.VFD_1LINE = 0x00
        self.VFD_BRIGHTNESS25 = 0x03
        self.VFD_BRIGHTNESS50 = 0x02
        self.VFD_BRIGHTNESS75 = 0x01
        self.VFD_BRIGHTNESS100 = 0x00

        self.VFD_5x10DOTS = 0x04
        self.VFD_5x8DOTS = 0x00

        self.VFD_SPICOMMAND = 0xF8
        self.VFD_SPIDATA = 0xFA

        self.VFD_SPICOMMAND = 0xf8

        # brightness values are "reversed" - higher 0x0n values are less bright
        self.brightness_cmds={0:0x03, 1:0x02, 2:0x01, 3:0x00}        
        self.brightness_lvl = 0

       

        
    def setspi(self):
        spi.open(0,0)
        spi.max_speed_hz=5000000
        # set spi mode to 3WIRE
        spi.mode = 3

    def init_VFD(self):
        _displayfunction = self.VFD_8BITMODE
        self.begin(self.COLS, self.ROWS,_displayfunction, self.VFD_BRIGHTNESS25)

    def begin(self, cols, lines, _displayfunction, brightness):
        if lines > 1:
           _displayfunction |= self.VFD_2LINE

        self.setBrightness(_displayfunction, brightness)

        _numlines = lines
        _currline = 0
    
        # Initialize to default text direction (for romance languages
        self._displaymode = self.VFD_ENTRYLEFT | self.VFD_ENTRYSHIFTDECREMENT 
        # set the entry mode
        self.command( self.VFD_ENTRYMODESET | self._displaymode) 

        # go to address 0
        self.command(self.VFD_SETDDRAMADDR)  
    
        # turn the display on with no cursor or blinking default
        self.command(self.VFD_DISPLAYCONTROL | self.VFD_DISPLAYON)
    
    
        self.clear()
        self.home()
    
    def display(self, _displaycontrol): 
        _displaycontrol |=  self.VFD_DISPLAYON 
        self.command(self.VFD_DISPLAYCONTROL | _displaycontrol) 

    def blink_on(self):
        _displaycontrol =  self.VFD_DISPLAYON | self.VFD_CURSORON | self.VFD_BLINKON
        self.display(_displaycontrol)

    def blink_off(self):
        _displaycontrol = self.VFD_DISPLAYON | self.VFD_CURSOROFF | self.VFD_BLINKOFF
        self.display(_displaycontrol)

    def clear(self):
        self.command(self.VFD_CLEARDISPLAY)
        sleep(2)

    def home(self):
        self.command(self.VFD_RETURNHOME)
        sleep(2)

    def setBrightness(self,_displayfunction, brightness):
        #set the brightness (only if a valid value is passed
        if brightness <= self.VFD_BRIGHTNESS25: 
            _displayfunction &= ~self.VFD_BRIGHTNESS25
            _displayfunction |= brightness

        self.command(self.VFD_FUNCTIONSET | _displayfunction)

    def brightnessAdjust(self):
        # will set brightness in round-robin fashion, low-to-high,
        # then back to low on the next key press
        self.setBrightness(self.VFD_2LINE, self.brightness_cmds[self.brightness_lvl])
        self.brightness_lvl+=1
        if self.brightness_lvl >=4:
           self.brightness_lvl = 0

    def setCursor(self, cols, row):
        _numlines = self.ROWS
        row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row > _numlines:
           row = _numlines-1        # count rows starting with 0
        self.command(self.VFD_SETDDRAMADDR | (cols + row_offsets[row]) )

    def noDisplay(self, vfdoff):
        self.command(self,self.VFD_DISPLAYCONTROL | vfdoff)
    
    
    #These commands scroll the display without changing the RAM
    def scrollDisplayLeft(self):
        self.command(self.VFD_CURSORSHIFT | self.VFD_DISPLAYMOVE | self.VFD_MOVELEFT)

    def scrollDisplayRight(self):
        self.command(self.VFD_CURSORSHIFT | self.VFD_DISPLAYMOVE | self.VFD_MOVERIGHT)

    #This will 'right justify' text from the cursor
    def autoscroll(self):
       self._displaymode |= self.VFD_ENTRYSHIFTINCREMENT
       self.command(self.VFD_ENTRYMODESET | self._displaymode)

    #This will 'left justify' text from the cursor
    def noAutoscroll(self):
      self._displaymode &= ~self.VFD_ENTRYSHIFTINCREMENT
      self.command(self.VFD_ENTRYMODESET | self._displaymode)

    def volume(self,mpd_volume, delta):    # pass actual mpd volume and vol +/- 
        # bounds checking
        mpd_volume = mpd_volume + delta
        #print mpd_volume
        if mpd_volume > 100:          # mpd_volume + delta > 100
           mpd_volume = 100
        elif mpd_volume < 5:          # mpd_volume + delta < 5
           mpd_volume = 0

        self.blank_lines() 
        self.setCursor(0,0)
        _string="      Volume: "
        _string=_string+str(mpd_volume)+"%"

        # display volume %
        l = [self.VFD_SPIDATA]
        for char in _string:
           l.append(ord(char))
        spi.writebytes(list(l))

        # display volume level bar
        self.setCursor(0,1)  
        disp_volume = mpd_volume/5  # one block displayed for each 5% volume (to fit 20 characters at 100%)

        l = [self.VFD_SPIDATA]
        for d in range(disp_volume):
            l.append(20)            # the '20' translates to a full-block character in CG-ROM
        spi.writebytes(list(l))          


    def text(self,string):
        l = [self.VFD_SPIDATA]
        for char in string:
           l.append(ord(char))
        spi.writebytes(list(l))
    
    def blank_lines(self):
        thistext = "                    "
        self.setCursor(0,0)
        self.text(thistext)
        self.setCursor(0,1)
        self.text(thistext)     

    def command(self,_setting):
        spi.xfer2([self.VFD_SPICOMMAND, _setting])


