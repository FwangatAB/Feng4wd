
#include <SPI.h>
#include "RF24.h"

/****************** Radio Config ***************************/
/***      Set this local radio (-->raspberry pi) as 0, remote robot radio as 1 ***/
bool radioNumber = 0;

/* Hardware configuration: Set up nRF24L01 radio on SPI bus plus pins 2 & 3 */
RF24 radio(2,3);
/**********************************************************/

byte addresses[][6] = {"1Node","2Node"};
int adjHeading = 0;
int val = 5; 
char c = 's';

void setup() {
  Serial.begin(115200);
  Serial.println(F("Radio transmition getting started"));
    
  radio.begin();

  // Set the PA Level low to prevent power supply related issues since this is a
 // getting_started sketch, and the likelihood of close proximity of the devices. RF24_PA_MAX is default.
  radio.setPALevel(RF24_PA_MAX);
  
  // Open a writing and reading pipe on each radio, with opposite addresses
  if(radioNumber){
    radio.openWritingPipe(addresses[1]);
    radio.openReadingPipe(1,addresses[0]);
  }else{
    radio.openWritingPipe(addresses[0]);
    radio.openReadingPipe(1,addresses[1]);
  }
  
  // Start the radio listening for data
  radio.startListening();
}

void loop() {
  
   if ( Serial.available() )
      {
        char c = Serial.read();
        if ( c == 'w'){
          Serial.println(F("*** robot moving forward********"));
          val = 3;

       }else if ( c == 'x'){
          Serial.println(F("*** robot moving backward*********"));
          val = 1;

        }else if ( c == 'a'){
            Serial.println(F("*** robot moving left**********"));
            val = 4;

          }else if ( c == 'd'){
            Serial.println(F("*** robot moving right************"));
             val = 2;

         }else if ( c =='s'){
          Serial.println(F("*** robot moving right************"));
             val = 5;
          }
      }

    /******************Received adjHeading value from remote_radio1 ***************************/

          
      if( radio.available()){
                                                                      // Variable for the received timestamp
        while (radio.available()) {                                   // While there is data ready
          radio.read( &adjHeading, sizeof(int) );                   // Get the payload
          Serial.println(adjHeading);
        }
       
        radio.stopListening();                          // First, stop listening so we can talk   
        radio.write( &val, sizeof(int) );              // Send the final one back.      
        radio.startListening();                                       // Now, resume listening so we catch the next packets.     
        Serial.print(F("Sent Motor Move Command "));
        Serial.println(val);  
     }
} // Loop


