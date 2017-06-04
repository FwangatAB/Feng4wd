
/*
* Getting Started example sketch for nRF24L01+ radios
* This is a very basic example of how to send data from one node to another
* Updated: Dec 2014 by TMRh20
*/

#include <SPI.h>
#include "RF24.h"

/****************** User Config ***************************/
/***      Set this radio as radio number 0 or 1         ***/
bool radioNumber = 0;

/* Hardware configuration: Set up nRF24L01 radio on SPI bus plus pins 7 & 8 */
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
  radio.setPALevel(RF24_PA_LOW);
  
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

       }else
        if ( c == 'x'){
          Serial.println(F("*** robot moving backward*********"));
          val = 1;

        }else
          if ( c == 'a'){
            Serial.println(F("*** robot moving left**********"));
            val = 4;

          }else
            if ( c == 'd'){
            Serial.println(F("*** robot moving right************"));
             val = 2;

         }else {
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
   

/****************** Ping Out Role ***************************/  

    
 /*   radio.stopListening();                                    // First, stop listening so we can talk.
    
    
    Serial.println(F("Now sending"));

    unsigned long start_time = micros();                             // Take the time, and send it.  This will block until complete
     if (!radio.write( &start_time, sizeof(unsigned long) )){
       Serial.println(F("failed"));
     }
        
    radio.startListening();                                    // Now, continue listening
    
    unsigned long started_waiting_at = micros();               // Set up a timeout period, get the current microseconds
    boolean timeout = false;                                   // Set up a variable to indicate if a response was received or not
    
    while ( ! radio.available() ){                             // While nothing is received
      if (micros() - started_waiting_at > 200000 ){            // If waited longer than 200ms, indicate timeout and exit while loop
          timeout = true;
          break;
      }      
    }
        
    if ( timeout ){                                             // Describe the results
        Serial.println(F("Failed, response timed out."));
    }else{
        unsigned long got_time;                                 // Grab the response, compare, and send to debugging spew
        radio.read( &got_time, sizeof(unsigned long) );
        unsigned long end_time = micros();
        
        // Spew it
        Serial.print(F("Sent "));
        Serial.print(start_time);
        Serial.print(F(", Got response "));
        Serial.print(got_time);
        Serial.print(F(", Round-trip delay "));
        Serial.print(end_time-start_time);
        Serial.println(F(" microseconds"));
    }

    // Try again later
    delay(1000);
  


*/

} // Loop


