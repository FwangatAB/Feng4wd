#include "Arduino.h"

// Reference the I2C Library
#include <Wire.h>

// Reference the HMC5883L Compass Library
#include <HMC5883L.h>

//Reference the Rnf24L01 radio library
#include <SPI.h>
#include "RF24.h"

// Store our compass as a variable.
HMC5883L compass;

/****************** Radio User Config ***************************/
/* Nrf24L01 radio module with base module
 * VCC --> separate 5v power supply red wire, GND --> black wire of 5v power supply and connect to GND pin of arduino board
 * CE --> pin 2, CSN -->3, SCK --> 13, MO --> 11, MI -->12, IRO -->? (none).
 */

/***      Set this radio as radio number 0 or 1         ***/
bool radioNumber = 1;   //set robot_radio as 1, and raspi_radio as 0

/* Hardware configuration: Set up nRF24L01 radio on SPI bus plus pins 2 & 3 */
RF24 radio(2,3);

/**********************************************************/

byte addresses[][6] = {"1Node","2Node"};

// Used to control whether this node is sending or receiving
bool role = 0;


/********************************DC motor Config Start (L298P)**********************************/

//the original pins for L298P dc motor shield are 10, 11, 12, 13. But pins 11, 12, 13 is used by Nrf24L01 radio module.
//We short these pns 10, 11, 12, 13 on the L298P dc motor shield and connect these pins to 6, 7, 8, 9 on the arduino uno board.

int pwm_a = 6;  //PWM control for motor1
int pwm_b = 7;  //PWM control for motor2
int dir_a = 8;  //dir control for motor1
int dir_b = 9;  //dir control for motor2

int lowspeed = 100;
int highspeed = 140;

//Distance away
int distance;

//Sets the duration each keystroke captures the motors.
int keyDuration = 10;


int iComp;

void setup() {

/*****************************Setup for Nrf24L01 radio module********************/

  Serial.begin(115200);    //Nrf24L radio on 115200, and HMC5886L on 9600?
  Serial.println(F("Radio Start"));
  radio.begin();

  // Set the PA Level low to prevent power supply related issues at first, and the likelihood of close proximity of the devices. RF24_PA_MAX is default.
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

/*********************************Setup for HMC5886L compass module***************************/

    Serial.begin(115200);

   //  Wire.begin(); // Start the I2C interface.need it or not?

      Serial.println("Initialize HMC5883L");
    //  compass = HMC5883L(); // Construct a new HMC5883 compass.

      while (!compass.begin())
       {
         Serial.println("Could not find a valid HMC5883L sensor, check wiring!");
         delay(500);
       }

       // Set measurement range
       compass.setRange(HMC5883L_RANGE_1_3GA);

       // Set measurement mode
       compass.setMeasurementMode(HMC5883L_CONTINOUS);

       // Set data rate
       compass.setDataRate(HMC5883L_DATARATE_30HZ);

       // Set number of samples averaged
       compass.setSamples(HMC5883L_SAMPLES_8);

       // Set calibration offset. See HMC5883L_calibration.ino
       compass.setOffset(0, 0);


      pinMode(pwm_a, OUTPUT);  //Set control pins to be outputs
      pinMode(pwm_b, OUTPUT);
      pinMode(dir_a, OUTPUT);
      pinMode(dir_b, OUTPUT);

      analogWrite(pwm_a, 0);
      analogWrite(pwm_b, 0);


}

// The loop function is called in an endless loop
void loop()
{


  /**********************calculate adjHeading*******************/

  Vector norm = compass.readNormalize();

    // Calculate heading
    float heading = atan2(norm.YAxis, norm.XAxis);

    // Set declination angle on your location and fix heading
    // You can find your declination on: http://magnetic-declination.com/
    // (+) Positive or (-) for negative
    // For Bytom / Poland declination angle is 4'26E (positive)
    // Formula: (deg + (min / 60.0)) / (180 / M_PI);
    float declinationAngle = (14.0 + (27.0 / 60.0)) / (180 / M_PI);
    heading += declinationAngle;

    // Correct for heading < 0deg and heading > 360deg
    if (heading < 0)
    {
      heading += 2 * PI;
    }

    if (heading > 2 * PI)
    {
      heading -= 2 * PI;
    }

    // Convert to degrees
    float headingDegrees = heading * 180/M_PI;

  // Normally we would delay the application by 66ms to allow the loop
  // to run at 15Hz (default bandwidth for the HMC5883L).
  // However since we have a long serial out (104ms at 9600) we will let
  // it run at its natural speed.
  // delay(66);

  //This throttles how much data is sent to Python code.
  //Basically, it updates every second (10 microsecond delay X 100 iComps)
  if (iComp >= 30){

    int adjHeading = 0;
    //The "floor" part makes the float into an integer, rounds it up.
    headingDegrees = floor(headingDegrees);
    if (headingDegrees >= 280){
        adjHeading = map(headingDegrees, 280, 360, 0, 79);
    }
    else if (headingDegrees <= 279) {
        adjHeading = map(headingDegrees, 0, 279, 80, 360);
    }

    Serial.println(adjHeading);
    /****************** Send adjHeading value to radio 0 ***************************/
   // if (role == 1)  {

        radio.stopListening();                                    // First, stop listening so we can talk.


        Serial.println(F("Now sending adjHeading"));

          if (!radio.write( &adjHeading, sizeof(int) )){
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
                }
      /*  else{
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
        }  */

        // Try again 1s later
        delay(1000);
  //    }
    iComp=0;
  }
  iComp++;

  delay(10); //For serial stability.

  /****************** receive motor move command from radio 0 ***************************/


      int val;

      if( radio.available()){
                                                                      // Variable for the received timestamp
        while (radio.available()) {                                   // While there is data ready
          radio.read( &val, sizeof(int) );             // Get the payload
        }

      //  radio.stopListening();                                        // First, stop listening so we can talk
      //  radio.write( &got_time, sizeof(unsigned long) );              // Send the final one back.
     //   radio.startListening();                                       // Now, resume listening so we catch the next packets.
        Serial.print(F("received motor moving command "));
        Serial.println(val);
     }
  // }


   /****************** receive morot move command from remote arduino serial monitor ***************************/

 /*   if ( Serial.available() )
    {
      char c = toupper(Serial.read());
      if ( c == 'w'){
        Serial.println(F("*** robot moving forward"));
        val = 3;

     }else
      if ( c == 'x'){
        Serial.println(F("*** robot moving backward"));
        val = 1;

      }else
        if ( c == 'a'){
          Serial.println(F("*** robot moving left"));
          val = 4;

        }else
          if ( c == 'd'){
          Serial.println(F("*** robot moving right"));
           val = 2;

       }else
           if ( c == 's'){
           Serial.println(F("*** robot stop moving"));
            val = 5;

        }
    } 
   /*************************************************/

  if (val == 1)
  {
    Back();
  }

  else if (val == 2)
  {
    Right();
  }

  else if (val == 3)
  {
    Forward();
  }

  else if (val == 4)
  {
    Left();
  }

  else if (val == 5)
  {
    Stop();
  }

}


void Back(){
//Straight back
      analogWrite(pwm_a, highspeed);
      analogWrite(pwm_b, highspeed);

      digitalWrite(dir_a, LOW);  //Reverse motor direction, 1 high, 2 low
      digitalWrite(dir_b, LOW);  //Reverse motor direction, 3 low, 4 high

delay(keyDuration);
}

void Left(){
      //Left
      analogWrite(pwm_a, lowspeed);
      analogWrite(pwm_b, lowspeed);

      digitalWrite(dir_a, LOW);  //Reverse motor direction, 1 high, 2 low
      digitalWrite(dir_b, HIGH);  //Reverse motor direction, 3 low, 4 high

delay(keyDuration);
}

void Right(){
      //Right
      analogWrite(pwm_a, lowspeed);
      analogWrite(pwm_b, lowspeed);

      digitalWrite(dir_a, HIGH);  //Reverse motor direction, 1 high, 2 low
      digitalWrite(dir_b, LOW);  //Reverse motor direction, 3 low, 4 high

delay(keyDuration);
}

void Forward(){
  //set both motors to run at 100% duty cycle (fast)
  analogWrite(pwm_a, highspeed);
  analogWrite(pwm_b, highspeed);

  //Straight forward
  digitalWrite(dir_a, HIGH);  //Set motor direction, 1 low, 2 high
  digitalWrite(dir_b, HIGH);  //Set motor direction, 3 high, 4 low

  delay(keyDuration);
}

void Stop(){
  //set both motors to run at 100% duty cycle (fast)
  analogWrite(pwm_a, 0);
  analogWrite(pwm_b, 0);

  //Straight forward
  digitalWrite(dir_a, HIGH);  //Set motor direction, 1 low, 2 high
  digitalWrite(dir_b, HIGH);  //Set motor direction, 3 high, 4 low

  delay(keyDuration);
}

