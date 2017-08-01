/*
 * local_radio0
 * the sketch for raspberry pi connected arduino uno board, and communicate with remote_radio1 (multibot end) 
 * 
 * July 28, 2017 replace adjHeading with myData for receiving dataStructure (adjHeading, voltage, current) from remote_radio1
 * 
 * To do list:
 * customized ros messager
 */


//reference for ros library
#include <ros.h>
#include <std_msgs/Int16.h>
#include <std_msgs/Float32.h>

//referece for Nrf24l01 radio library
#include <SPI.h>
#include "RF24.h"

/****************** Radio Config ***************************/
/***      Set this local radio (-->raspberry pi) as 0, remote robot radio as 1 ***/
bool radioNumber = 0;

/* Hardware configuration: Set up nRF24L01 radio on SPI bus plus pins 2 & 3 */
RF24 radio(2,3);

byte addresses[][6] = {"1Node","2Node"};

/**********************************************************/

struct dataStruct{
  int adjHeading;
  float voltage;
  float current;
}myData;

char c = 's';   //initialize robot motors as "stop" 
int val = 5;    

void commandCallback(const std_msgs::Int16& cmd_msg){
  val = cmd_msg.data;
}

ros::NodeHandle  nh;

std_msgs::Int16 adjDegree;
std_msgs::Float32 voltage;
std_msgs::Float32 current;
ros::Publisher HeadingDegree("HeadingDegree", &adjDegree);
ros::Publisher VoltageInfo("VoltageInfo", &voltage);
ros::Publisher CurrentInfo("CurrentInfo", &current);
ros::Subscriber<std_msgs::Int16>Motor_Cmd("cmd_4wd",commandCallback);

void setup() {
  Serial.begin(57600);
//  Serial.println(F("Radio transmition getting started")); 

  /***************Setup radio read/write pipes***************/
    
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
  
  /*******************config ROS node*************/
  
  nh.initNode();
  nh.advertise(HeadingDegree);
  nh.advertise(VoltageInfo);
  nh.advertise(CurrentInfo);
  nh.subscribe(Motor_Cmd);
  
  
}

void loop() {

  /*******send commands to robot motors from local serial monitor********/
   

          
      if( radio.available()){
                                                                      // Variable for the received timestamp
        while (radio.available()) {                                   // While there is data ready
          radio.read( &myData, sizeof(myData) );                   // Get the payload
       //   Serial.println(adjHeading);
        }
       radio.stopListening();                          // First, stop listening so we can talk   
       
       adjDegree.data = myData.adjHeading; 
       voltage.data = myData.voltage;
       current.data = myData.current;
       HeadingDegree.publish( &adjDegree);
       VoltageInfo.publish(&voltage);
       CurrentInfo.publish(&current);
       nh.spinOnce();
       delay(50); 
    
    /******************send commands to remote robot radio1****************/
        radio.write( &val, sizeof(int) );              // Send the final one back.      
        radio.startListening();                                       // Now, resume listening so we catch the next packets.     
    //    Serial.print(F("Sent Motor Move Command "));
     //   Serial.println(val);  
     }
} // Loop
