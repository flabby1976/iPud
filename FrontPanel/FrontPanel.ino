#include <Pushbutton.h>

/*  Arduino code for iPud front panel buttons and switches    
 *  by Andrew Robinson
 *  
 *  Uses Pushbutton library from https://github.com/pololu/pushbutton-arduino
 *  Uses rotary encoder reading/debouncing from http://www.technoblogy.com/show?1YHJ
 *  
 */

#define rotPushPin 4

#define push1Pin 8
#define push2Pin 9
#define push3Pin 10
#define push4Pin 11

#define volumePin A0


const int EncoderA = 3;           // PD4
const int EncoderAInt = PCINT19;  // Pin change interrupt on PD4
const int EncoderB = 2;           // PD5

// Rotary encoder **********************************************
volatile int a0;
volatile int c0;
volatile int Count = 0;

// Push buttons
Pushbutton push1(push1Pin);
Pushbutton push2(push2Pin);
Pushbutton push3(push3Pin);
Pushbutton push4(push4Pin);

Pushbutton rotPush(rotPushPin);


int ledPin = 13;      // select the pin for the LED
//int sensorValue = 0;  // variable to store the value coming from the sensor

// Called when encoder value changes
void ChangeValue (bool Up) {
  digitalWrite(ledPin, Up);
  Count = max(min((Count + (Up ? 1 : -1)), 1000), 0);
  Serial.println(Count);
}

// Pin change interrupt service routine
ISR (PCINT2_vect) {
  int a = PIND>>EncoderA & 1;     // Change these if
  int b = PIND>>EncoderB & 1;     // using different pins
  if (a != a0) {                  // A changed
    a0 = a;
    if (b != c0) {
      c0 = b;
      ChangeValue(a == b);
    }
  }
}


 void setup() { 
  // declare the ledPin as an OUTPUT:
   pinMode(ledPin, OUTPUT);

   // rotary switch pins
   pinMode(EncoderA, INPUT_PULLUP);
   pinMode(EncoderB, INPUT_PULLUP);

   // rotary switch push pin
   pinMode (rotPushPin,INPUT);
   digitalWrite(rotPushPin, HIGH);
 
   // setup theserial port for comms with Pi
   Serial.begin (9600);

   PCMSK2 = 1<<PCINT19;            // Configure pin change interrupt on A
   PCICR = 1<<PCIE2;               // Enable interrupt
   PCIFR = 1<<PCIF2;               // Clear interrupt flag
   
   Serial.println("Ready");
 } 

void loop() {

   if (push1.getSingleDebouncedPress()){
    Serial.println("Button 1 pressed");
   }
   if (push2.getSingleDebouncedPress()){
    Serial.println("Button 2 pressed");
   }
   if (push3.getSingleDebouncedPress()){
    Serial.println("Button 3 pressed");
   }
   if (push4.getSingleDebouncedPress()){
    Serial.println("Button 4 pressed");
   }

   if (rotPush.getSingleDebouncedPress()){
    Serial.println("Rotary button pressed");
   }
   
 }
