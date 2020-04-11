/*     Arduino Rotary Encoder Tutorial
 *      
 *  by Dejan Nedelkovski, www.HowToMechatronics.com
 *  
 */
 
 #define outputA 7
 #define outputB 6

 int counter = 0; 
 int aState = 1;
 int aLastState;  

 int sensorPin = A0;    // select the input pin for the potentiometer
 int ledPin = 13;      // select the pin for the LED
 int sensorValue = 0;  // variable to store the value coming from the sensor

 void setup() { 
  // declare the ledPin as an OUTPUT:
   pinMode(ledPin, OUTPUT);
 
   pinMode (outputA,INPUT);
   digitalWrite(outputA, HIGH);
   pinMode (outputB,INPUT);
   digitalWrite(outputB, HIGH);
   
   Serial.begin (9600);
   // Reads the initial state of the outputA
   aLastState = digitalRead(outputA);   
 } 

 void loop() { 

  // read the value from the sensor:
  sensorValue = analogRead(sensorPin);

  Serial.println(sensorValue);

  // stop the program for <sensorValue> milliseconds:
  delay(2000);

 
   aState = digitalRead(outputA); // Reads the "current" state of the outputA
   // If the previous and the current state of the outputA are different, that means a Pulse has occured
   if (aState != aLastState){     
     // If the outputB state is different to the outputA state, that means the encoder is rotating clockwise
     if (digitalRead(outputB) != aState) { 
       Serial.println("knob up");
     } else {
       Serial.println("knob down");
     }
   } 
   aLastState = aState; // Updates the previous state of the outputA with the current state
 }
