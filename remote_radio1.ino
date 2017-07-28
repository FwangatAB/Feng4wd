#include "Arduino.h"
//JULY 25 2017 SETUP COMPASS OFFSET VALUES. COMMENT OUT MAP() FUNCTION.
// Reference the I2C Library
#include <Wire.h>

// Reference the HMC5883L Compass Library
#include <HMC5883L.h>

//Reference the Rnf24L01 radio library
#include <SPI.h>
#include "RF24.h"

// Store our compass as a variable.
HMC5883L compass;

/****************** Radio Config ***************************/
/* Nrf24L01 radio module with base module 5V
 * VCC --> separate 5v power supply red wire, GND --> black wire of 5v power supply and connect to GND pin of arduino board
 * CE --> pin 2, CSN -->3, SCK --> 13, MO --> 11, MI -->12, IRO -->? (none).
 */

/***      Set this radio as radio number 0 or 1         ***/
bool radioNumber = 1;   //set robot_radio as 1, and raspi_radio as 0

/* Hardware configuration: Set up nRF24L01 radio on SPI bus plus pins 2 & 3 */
RF24 radio(2,3);

/**********************************************************/

byte addresses[][6] = {"1Node","2Node"};

/********************************DC motor Config Start (L298P)**********************************/

//the original pins for L298P dc motor shield are 10, 11, 12, 13. But pins 11, 12, 13 is used by Nrf24L01 radio module.
//We short these pns 10, 11, 12, 13 on the L298P dc motor shield and connect these pins to 6, 7, 8, 9 on the arduino uno board.

int pwm_a = 6;  //PWM control for motor1
int pwm_b = 7;  //PWM control for motor2
int dir_a = 8;  //dir control for motor1
int dir_b = 9;  //dir control for motor2

int lowspeed = 140;
int highspeed = 255;

//Distance away
int distance;

//Sets the duration each keystroke captures the motors.
int keyDuration = 10;

int iComp;

int val = 5;
char d = 's';

void setup(){

 /*****************************Setup for Nrf24L01 radio module********************/

  Serial.begin(9600);    //Nrf24L radio on 115200, and HMC5886L on 9600?
  Serial.println(F("Radio Start"));
  radio.begin();

  // Set the PA Level low to prevent power supply related issues at first, and the likelihood of close proximity of the devices. RF24_PA_MAX is default.
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

/*********************************Setup for HMC5886L compass module***************************/

      Serial.println("Initialize HMC5883L");
          
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
       compass.setOffset(229, -427);


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
    float declinationAngle = (14.0 + (25.0 / 60.0)) / (180 / M_PI);
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
    int adjHeading = 0;
    //The "floor" part makes the float into an integer, rounds it up.
    adjHeading = floor(headingDegrees);
   /* headingDegrees = floor(headingDegrees);
    if (headingDegrees >= 280){
        adjHeading = map(headingDegrees, 280, 360, 0, 79);
    }
    else if (headingDegrees <= 279) {
        adjHeading = map(headingDegrees, 0, 279, 80, 360);
    }
    delay(20);
       
    /****************** Send adjHeading value to radio 0 ***************************/

        radio.stopListening();                                    // First, stop listening so we can talk.


         if (!radio.write(&adjHeading, sizeof(int) )){
                   }

        radio.startListening();                                    // Now, continue listening

      delay(20); //For serial stability.

 
   /****************** receive motor move command from radio 0 ***************************/


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

      digitalWrite(dir_a, LOW);  
      digitalWrite(dir_b, LOW);  
      
delay(keyDuration);
}

void Left(){
      //Left
      analogWrite(pwm_a, highspeed);
      analogWrite(pwm_b, highspeed);

      digitalWrite(dir_a, HIGH);  //Reverse motor direction, 1 high, 2 low
      digitalWrite(dir_b, LOW);  //Reverse motor direction, 3 low, 4 high

delay(keyDuration);
}

void Right(){
      //Right
      analogWrite(pwm_a, highspeed);
      analogWrite(pwm_b, highspeed);

      digitalWrite(dir_a, LOW);  //Reverse motor direction, 1 high, 2 low
      digitalWrite(dir_b, HIGH);  //Reverse motor direction, 3 low, 4 high

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
