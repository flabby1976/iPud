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

boolean conn = false;

// Define the bit patters for each of our custom chars. These
// are 5 bits wide and 8 dots deep
uint8_t custChar[8][8] = {
  {31, 31, 31, 0, 0, 0, 0, 0},      // Small top line - 0
  {0, 0, 0, 0, 0, 31, 31, 31},      // Small bottom line - 1
  { B11111,
    B00000,
    B00000,
    B00000,                         // This shows an alternative
    B00000,                         // way of defining a custome character,
    B00000,                         // a bit more 'visually' perhaps?
    B00000,
    B11111,
  },
  //{31, 0, 0, 0, 0, 0, 0, 31},     // Small lines top and bottom -2
  {0, 0, 0, 0, 0, 0,  0, 31},       // Thin bottom line - 3
  {31, 31, 31, 31, 31, 31, 15, 7},  // Left bottom chamfer full - 4
  {28, 30, 31, 31, 31, 31, 31, 31}, // Right top chamfer full -5
  {31, 31, 31, 31, 31, 31, 30, 28}, // Right bottom chamfer full -6
  {7, 15, 31, 31, 31, 31, 31, 31},  // Left top chamfer full -7
};

// Define our numbers 0 thru 9
// 254 is blank and 255 is the "Full Block"
uint8_t bigNums[10][6] = {
  {7, 0, 5, 4, 1, 6},         //0
  {0, 5, 254, 1, 255, 1},     //1
  {0, 2, 5, 7, 3, 1},         //2
  {0, 2, 5, 1, 3, 6},         //3
  {7, 3, 255, 254, 254, 255}, //4
  {7, 2, 0, 1, 3, 6},         //5
  {7, 2, 0, 4, 3, 6},         //6
  {0, 0, 5, 254, 7, 254},     //7
  {7, 2, 5, 4, 3, 6},         //8
  {7, 2, 5, 1, 3, 6},         //9
};

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

  // set up the vfd's number of columns and rows: 
  vfd.begin(20, 2);

  vfd.clear();
  vfd.setCursor(0,0);
  vfd.print(F("Arduino restarting ..."));

  delay(1000);
  
  vfd.setCursor(0,0);  
  vfd.print(F("hello, world!         "));

    // Create custom character map (8 characters only!)
  for (int cnt = 0; cnt < sizeof(custChar) / 8; cnt++) {
    vfd.createChar(cnt, custChar[cnt]);
  }

vfd.clear();
vfd.setCursor(0, 0);
vfd.print("Restarting");
vfd.setCursor(0, 1);
vfd.print("Please wait!");

////  Dummy clock splash screen!
//  vfd.clear();
//  vfd.setCursor(8, 0);
//  vfd.print((char)161);
//  vfd.setCursor(8, 1);
//  vfd.print((char)161);
//
//  vfd.setCursor(17, 0);
//  vfd.print("PM");
//
//  vfd.setCursor(17, 1);
//  vfd.print("55");
//
//  printBigNum(2, 0, 0);
//  printBigNum(3, 4, 0);
//  printBigNum(5, 9, 0);
//  printBigNum(3, 13, 0);
//

  rencoder.enableInternalRotaryPullups(); 
  rencoder.setRotaryLimits(-(rotaryMaximum - 1), rotaryMaximum, rotaryWrapMode);
  
  // One interrupt is required for the rotary
  attachInterrupt(digitalPinToInterrupt(pinSCK), ISRrotary, CHANGE);
  
  // setup the serial port for comms with Pi
  Serial.begin (9600);

  while(conn = false) {
    recvWithStartEndMarkers();
    if (newData == true){
      handleVFDcmd(receivedChars);
      newData = false;
    }
  }
  

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
    Serial.print("<b ");
    Serial.print(*label);
    if (t<1000)
       Serial.print(" s>");
    else
       Serial.print(" l>");    
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
      case 'h':{ // home
        vfd.home();
        break;
      }
      case 'c':{ // clear
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
        Serial.print("<!>");
        conn = true ;
        break;
      }
      default:
        Serial.print("<");Serial.print(receivedChars);Serial.print(" ? >");
        break;
    }
  }
}

// -----------------------------------------------------------------
// Print big number over 2 lines, 3 colums per half digit
// -----------------------------------------------------------------
void printBigNum(int number, int startCol, int startRow) {

  // Position cursor to requested position (each char takes 3 cols plus a space col)
  vfd.setCursor(startCol, startRow);

  // Each number split over two lines, 3 chars per line. Retrieve character
  // from the main array to make working with it here a bit easier.
  uint8_t thisNumber[6];
  for (int cnt = 0; cnt < 6; cnt++) {
    thisNumber[cnt] = bigNums[number][cnt];
  }

  // First line (top half) of digit
  for (int cnt = 0; cnt < 3; cnt++) {
    vfd.print((char)thisNumber[cnt]);
  }

  // Now position cursor to next line at same start column for digit
  vfd.setCursor(startCol, startRow + 1);

  // 2nd line (bottom half)
  for (int cnt = 3; cnt < 6; cnt++) {
    vfd.print((char)thisNumber[cnt]);
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
    Serial.print("<k 1 ");Serial.print(currentPosition);Serial.print(">");
  }

  recvWithStartEndMarkers();
  if (newData == true){
    handleVFDcmd(receivedChars);
    newData = false;
  }
 
}
 
