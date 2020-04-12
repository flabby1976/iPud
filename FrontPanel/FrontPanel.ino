#include <SPI_VFD.h>
#include <FR_RotaryEncoder.h>
#include <Pushbutton.h>

/*  Arduino code for iPud front panel buttons and switches    
 *  by Andrew Robinson
 *  
 *  Uses Pushbutton library from https://github.com/pololu/pushbutton-arduino
 *  Uses rotary encoder library from https://github.com/fryktoria/FR_RotaryEncoder
 *          which is based on reading/debouncing from http://www.technoblogy.com/show?1YHJ
 *  
 */


#define push1Pin 8
#define push2Pin 9
#define push3Pin 10
#define push4Pin 11

#define volumePin A0

int pinSCK = 3; // Interrupt pin for rotary encoder. Can be 2 or 3      
int pinDT = 4; // Better select a pin from 4 to 7
int pinSW = 2; // Interrupt pin for switch. Can be 2 or 3
int rotaryMaximum = 100;
int rotaryMinimum = -(rotaryMaximum - 1);
bool rotaryWrapMode = false;

int mSIO = 5;
int mSTB = 6;
int mSCK = 7;

unsigned long button_time = 0;

const byte numChars = 64;
char receivedChars[numChars];

boolean newData = false;

//-----------------------------------------------------------------------------------

// Push buttons
Pushbutton push1(push1Pin);
Pushbutton push2(push2Pin);
Pushbutton push3(push3Pin);
Pushbutton push4(push4Pin);

// Rotary encoder
RotaryEncoder rencoder(pinSCK, pinDT, pinSW);

// Interrupt handling routine for the rotary
void ISRrotary() {
    rencoder.rotaryUpdate();
}

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

//        Serial.write(rc);

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}


Pushbutton pushk(pinSW);

// initialize the VFD with the numbers of the interface pins
// (data, clk, strobe)
SPI_VFD vfd(mSIO, mSCK, mSTB);

int ledPin = 13;      // select the pin for the LED

void setup() { 
  // declare the ledPin as an OUTPUT:
  pinMode(ledPin, OUTPUT);

  // set up the LCD's number of columns and rows: 
  vfd.begin(20, 2);
  // Print a message to the LCD.
  vfd.print("hello, world!");
  
  rencoder.enableInternalRotaryPullups(); 
  rencoder.setRotaryLimits(rotaryMinimum, rotaryMaximum, rotaryWrapMode);
  
  // One interrupt is required for the rotary
  attachInterrupt(digitalPinToInterrupt(pinSCK), ISRrotary, CHANGE);
  
  // setup the serial port for comms with Pi
  Serial.begin (9600);

  Serial.println("<Arduino is ready>");
} 

int t;
int lastPosition;

void loop() {

   if (pushk.getSingleDebouncedPress()){
    button_time = millis();
    t = 0;
    // Note: this holds the whole loop up while button is pressed
    while ( ( t < 1000) && pushk.isPressed() ) {
      t = millis()-button_time;
      }
    if (t<1000)
       Serial.println("knob button press");
    else
       Serial.println("knob button longpress");    
   }

 
   if (push1.getSingleDebouncedPress()){
    button_time = millis();
    t = 0;
    while ( ( t < 1000) && push1.isPressed() ) {
      t = millis()-button_time;
      }
    if (t<1000)
       Serial.println("button 1 press");
    else
       Serial.println("button 1 longpress");    
   }
   
   if (push2.getSingleDebouncedPress()){
    Serial.println("button 2 press");
   }
   if (push3.getSingleDebouncedPress()){
    Serial.println("button 3 press");
   }
   if (push4.getSingleDebouncedPress()){
    Serial.println("button 4 press");
   }

  // Rotary 
  int currentPosition = rencoder.getPosition();
  if (lastPosition != currentPosition) {
    lastPosition = currentPosition;
    Serial.print("knob position ");Serial.println(currentPosition); 
  }

  recvWithStartEndMarkers();
  if (newData == true){
    vfd.setCursor(0, 1);
    vfd.print(receivedChars);
    newData = false;
  }
  else {
//    Serial.println("0");
  }
 
 }
 
