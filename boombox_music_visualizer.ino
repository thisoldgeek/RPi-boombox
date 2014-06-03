/***********************************************************************
 * HT1624.pde - Arduino demo program for Holtek HT1632 LED driver chip,
 *            As implemented on the Sure Electronics DE-DP016 display board
 *            (16*24 dot matrix LED module.)
 * Nov, 2008 by Bill Westfield ("WestfW")
 *   Copyrighted and distributed under the terms of the Berkely license
 *   (copy freely, but include this notice of original author.)
 *
 * Adapted for 8x32 display by FlorinC.
 ***********************************************************************/

// comment out this line for the 8x32 display;
//#define _16x24_

#include <wprogram.h>
#include <avr\pgmspace.h>
#include <HT1632_LedMatrix.h>

#include <Adafruit_NeoPixel.h>
#define NEOPIXELPIN1 8
#define NEOPIXELPIN2 9

Adafruit_NeoPixel strip1 = Adafruit_NeoPixel(12, NEOPIXELPIN1, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel strip2 = Adafruit_NeoPixel(12, NEOPIXELPIN2, NEO_GRB + NEO_KHZ800);



// create object to control the LED Matrix
HT1632_LedMatrix led = HT1632_LedMatrix();

// HT1632 PINOUTS:
/*
SURE PIN        ARDUINO PIN
CS1   (#3)        2
WR    (#5)        7
DATA  (#7)        6
+5V   (#12)       5v
GND   (#11)       GND
*/


// variables used for MSGEQ7
int strobe = 4; // strobe pins on digital 4
int res = 5; // reset pins on digital 5
int left[7]; // store band values in these arrays
int right[7];
int band;

// variables for Neopixels
const int num_pixels = 12;
const int pi_input = 10;
int led_toggle = 1;   // takes input from Rpi to turn lights on/off

int incr_vol = 900;
int avg1 = 0;  // left band
int avg2 = 0;  // right band

#define DISPDELAY 60
  
/***********************************************************************
 * traditional Arduino sketch functions: setup and loop.
 ***********************************************************************/

void setup ()
{
  // initialize Neopixels
  strip1.begin();
  strip1.setBrightness(128);
  strip1.show(); // Initialize all pixels to 'off'
  
  strip2.begin();
  strip2.setBrightness(128);
  strip2.show(); // Initialize all pixels to 'off'
  
  
  // Initialize Sure LED Matrix
  led.init(1,1);
  Serial.begin(115200);
  led.clear();
  
  led.setBrightness(2);
  
  // for MSGEQ7
pinMode(res, OUTPUT); // reset
pinMode(strobe, OUTPUT); // strobe
digitalWrite(res,LOW); // reset low
digitalWrite(strobe,HIGH); //pin 5 is RESET on the shield


  
pinMode(pi_input, INPUT);
digitalWrite(pi_input, LOW);
}
void readMSGEQ7()
// Function to read 7 band equalizers
{
avg1 = 0;
avg2 = 0;
digitalWrite(res, HIGH);
digitalWrite(res, LOW);
for( band = 0; band < 7; band++ )
{
digitalWrite(strobe,LOW); // strobe pin on the shield - kicks the IC up to the next band
delayMicroseconds(30); //
left[band] = analogRead(0); // store left band reading
avg1 += left[band];    // for Neopixel VU meter 
right[band] = analogRead(1); // ... and the right
avg2 += right[band];    // for Neopixel VU meter 
digitalWrite(strobe,HIGH);
}

} 
  
 
  

void loop ()
{ // boombox pi script telling us to turn lights on or off
  
  led_toggle = digitalRead(pi_input);
  
  //  Neopixels Cleared
  for(int i = 0; i < num_pixels; i++){
    strip1.setPixelColor(i, strip1.Color(0, 0, 0));
  }
  //Clear out the NeoPixel String
  for(int i = 0; i < num_pixels; i++){
    strip2.setPixelColor(i, strip2.Color(0, 0, 0));
  }
  
  strip1.show();
  strip2.show();
  
  led.clear();
  
  while (led_toggle)

  {music_visualizer();
  
  led_toggle = digitalRead(pi_input);
  }  
  
}
 
void music_visualizer()
{
  int xpos;
readMSGEQ7();
led.clear();

//avg = avg/7;
  avg1 = avg1 + incr_vol;
  avg1 = avg1/7;
  avg2 = avg2 + incr_vol;
  avg2 = avg2/7;
  //Serial.println(avg1);
  //Serial.println(avg2);
  //Clear out the NeoPixel String
  for(int i = 0; i < num_pixels; i++){
    strip1.setPixelColor(i, strip1.Color(0, 0, 0));
  }
  //Clear out the NeoPixel String
  for(int i = 0; i < num_pixels; i++){
    strip2.setPixelColor(i, strip2.Color(0, 0, 0));
  }
  
  
 
  
  for(int i = 0; i < map(avg1, 0, 1023, 0, num_pixels); i++){
    strip1.setPixelColor(i, strip1.Color(i*4, num_pixels + i, map(left[i], 0, 1023, 0, num_pixels+60))); //Added blue flash for bass hit
    //strip.setPixelColor(i, strip.Color(i*4, num_pixels - i, 0)); //Without blue flash
  }
  
 
  for(int i = 0; i < map(avg2, 0, 1023, 0, num_pixels); i++){
    strip2.setPixelColor(num_pixels - i, strip2.Color(i*4, num_pixels + i, map(right[i], 0, 1023, 0, num_pixels+60))); //Added blue flash for bass hit
    //strip1.setPixelColor(i, strip1.Color(i*4, num_pixels - i, 0)); //Without blue flash
  }
  
 /*
  for(int i = 0; i < map(avg2, 0, 1023, 0, num_pixels); i++){
    strip2.setPixelColor(num_pixels - i, strip2.Color(i*4, num_pixels - i, map(right[band], 0, 1023, 0, num_pixels))); //Added blue flash for bass hit
    //strip1.setPixelColor(i, strip1.Color(i*4, num_pixels - i, 0)); //Without blue flash
  }
  */
  
  
  
  
  
  //strip1.setBrightness(125);
  strip1.show();  
  strip2.show();  
  
// display values of left channel on DMD
for( band = 0; band < 7; band++ )
{
xpos = (band*2)+1;
if (left[band]>=895) { led.drawFilledRectangle( xpos, 0, xpos+1, 7, PIXEL_ON ); } else
if (left[band]>=767) { led.drawFilledRectangle( xpos, 1, xpos+1, 7, PIXEL_ON ); } else
if (left[band]>=639) { led.drawFilledRectangle( xpos, 2, xpos+1, 7, PIXEL_ON ); } else
if (left[band]>=511) { led.drawFilledRectangle( xpos, 3, xpos+1, 7, PIXEL_ON ); } else
if (left[band]>=383) { led.drawFilledRectangle( xpos, 4, xpos+1, 7, PIXEL_ON ); } else
if (left[band]>=255) { led.drawFilledRectangle( xpos, 5, xpos+1, 7, PIXEL_ON ); } else
if (left[band]>=127) { led.drawFilledRectangle( xpos, 6, xpos+1, 7, PIXEL_ON ); } else
if (left[band]>=0) { led.drawFilledRectangle( xpos, 7, xpos+1, 7, PIXEL_ON ); }
}
 
for( band = 0; band < 7; band++ )
{
xpos = (band*2)+17;
if (right[band]>=895) { led.drawFilledRectangle( xpos, 0, xpos+1, 7, PIXEL_ON ); } else
if (right[band]>=767) { led.drawFilledRectangle( xpos, 1, xpos+1, 7, PIXEL_ON ); } else
if (right[band]>=639) { led.drawFilledRectangle( xpos, 2, xpos+1, 7, PIXEL_ON ); } else
if (right[band]>=511) { led.drawFilledRectangle( xpos, 3, xpos+1, 7, PIXEL_ON ); } else
if (right[band]>=383) { led.drawFilledRectangle( xpos, 4, xpos+1, 7, PIXEL_ON ); } else
if (right[band]>=255) { led.drawFilledRectangle( xpos, 5, xpos+1, 7, PIXEL_ON ); } else
if (right[band]>=127) { led.drawFilledRectangle( xpos, 6, xpos+1, 7, PIXEL_ON ); } else
if (right[band]>=0) { led.drawFilledRectangle( xpos, 7, xpos+1, 7, PIXEL_ON ); }
}
  
 
  led.putShadowRam();
  delay(DISPDELAY); 
  
}

