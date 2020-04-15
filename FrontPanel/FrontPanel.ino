#include <SPI_VFD.h>
#include <FR_RotaryEncoder.h>
#include <Pushbutton.h>

/*  Arduino code for iPud front panel display, buttons, dials and switches    
 *  by Andrew Robinson
 *  
 *  Uses Pushbutton library from https://github.com/pololu/pushbutton-arduino
 *  Uses rotary encoder library from https://github.com/fryktoria/FR_RotaryEncoder
 *          which is based on reading/debouncing from http://www.technoblogy.com/show?1YHJ
 *  Uses SPI_VFD library from https://github.com/adafruit/SPI_VFD
 *  
 */

// The 4 pushbuttons
#define push1Pin 8
#define push2Pin 9
#define push3Pin 10
#define push4Pin 11

// The slider from the volume control pot
#define volumePin A0

// Rotary encoder pins
#define pinSCK 3 // Interrupt pin for rotary encoder. Can be 2 or 3      
#define pinDT 4  // Better select a pin from 4 to 7
#define pinSW 2  // Interrupt pin for switch. Can be 2 or 3

// SDI output for the display
#define mSIO 5
#define mSTB 6
#define mSCK 7

unsigned int rotaryMaximum = 1000;
//int rotaryMinimum = -(rotaryMaximum - 1);
bool rotaryWrapMode = false;

const byte numChars = 64;
char receivedChars[numChars];
boolean newData = false;


//-----------------------------------------------------------------------------------

// initialize the Push buttons
Pushbutton push1(push1Pin);
Pushbutton push2(push2Pin);
Pushbutton push3(push3Pin);
Pushbutton push4(push4Pin);

// initialize the Rotary encoder
RotaryEncoder rencoder(pinSCK, pinDT, pinSW);
// Rotary encoder switch is handled better by the Pushbutton library
Pushbutton pushk(pinSW);

// Interrupt handling routine for the rotary encoder
void ISRrotary() {
    rencoder.rotaryUpdate();
}

// initialize the VFD with the numbers of the interface pins
SPI_VFD vfd(mSIO, mSCK, mSTB);

//-----------------------------------------------------------------------------------

void setup() { 

  // set up the LCD's number of columns and rows: 
  vfd.begin(20, 2);
  // Print a message to the LCD.

  vfd.clear();
  vfd.setCursor(0,0);
  vfd.print(F("Arduino restarting ..."));

  delay(1000);
  
  vfd.setCursor(0,0);  
  vfd.print(F("hello, world!         "));

  rencoder.enableInternalRotaryPullups(); 
  rencoder.setRotaryLimits(-(rotaryMaximum - 1), rotaryMaximum, rotaryWrapMode);
  
  // One interrupt is required for the rotary
  attachInterrupt(digitalPinToInterrupt(pinSCK), ISRrotary, CHANGE);
  
  // setup the serial port for comms with Pi
  Serial.begin (9600);

} 


void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

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


void handleSwitch(Pushbutton *button, char *label) {

   unsigned int t;
   unsigned int button_time;

   if ((*button).getSingleDebouncedPress()){
    button_time = millis();
    t = 0;
    // Note: this holds the whole loop up while button is pressed
    while ( ( t < 1000) && (*button).isPressed() ) {
      t = millis()-button_time;
      }
    Serial.print("b ");
    Serial.print(*label);
    if (t<1000)
       Serial.println(" s");
    else
       Serial.println(" l");    
   }
  
}

void handleVFDcmd(char *cmd){

  char *pch;
  int a;
  int b;
  char *s;

  pch = strtok(cmd," ");
  if (pch != NULL) {
    switch(pch[0]){
      case 'h':{ // home and clear
        vfd.home();
        break;
      }
      case 'c':{ // home and clear
        vfd.clear();
        break;
      }
      case 'm': { // move cursor
        a = atoi(strtok(NULL," "));
        b = atoi(strtok(NULL," "));
        vfd.setCursor(a, b);
        break;
      }
      case 'd': { // display on/off
        s = strtok(NULL," ");
        if (s != NULL) {
          if (s[0] == '1') {
            vfd.display();
          }
          else {
            vfd.noDisplay();
          }
         }
        else {
           vfd.display();
        }        
        break;
      }
      case 'p': { // print text
        s = strtok(NULL,"\"");
        vfd.print(s);
        break;
      }
      case 's': { // scroll right or left
        s = strtok(NULL," ");
        if (s != NULL) {
          if (s[0] == 'l') {
            vfd.scrollDisplayLeft();
          }
          else {
            vfd.scrollDisplayRight();
          }
         }
        else {
           vfd.scrollDisplayRight();
        }        
        break;
      }
      case 'k': { // cursor on/off
        s = strtok(NULL," ");
        if (s != NULL) {
          if (s[0] == '1') {
            vfd.cursor();
          }
          else {
            vfd.noCursor();
          }
         }
        else {
           vfd.cursor();
        }        
        break;
      }
      case 'b': { // blink on/off
        s = strtok(NULL," ");
        if (s != NULL) {
          if (s[0] == '1') {
            vfd.blink();
          }
          else {
            vfd.noBlink();
          }
         }
        else {
           vfd.blink();
        }        
        break;
      }
      case 'r': { // direction
        s = strtok(NULL," ");
        if (s != NULL) {
          if (s[0] == '1') {
            vfd.rightToLeft();
          }
          else {
            vfd.leftToRight();
          }
         }
        else {
           vfd.leftToRight();
        }        
        break;
      }
      case '?': { // ping from client to make sure I'm awake
        Serial.println("!");
        break;
      }
      default:
        Serial.println("?");
        Serial.println(receivedChars);
        break;
    }
  }
}
  

int lastPosition;
void loop() {

  handleSwitch(&pushk, "k");
  handleSwitch(&push1, "1");
  handleSwitch(&push2, "2");
  handleSwitch(&push3, "3");
  handleSwitch(&push4, "4");

  // Rotary 
  int currentPosition = rencoder.getPosition();
  if (lastPosition != currentPosition) {
    lastPosition = currentPosition;
    Serial.print("k 1 ");Serial.println(currentPosition); 
  }

  recvWithStartEndMarkers();
  if (newData == true){
    handleVFDcmd(receivedChars);
    newData = false;
  }
 
}
 
