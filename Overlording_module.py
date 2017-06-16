
import rospy
from std_msgs.msg import Int32
import serial
from time import sleep
import threading
import overlord

#To test module.
overlord.printo()

#Initialize Overlord variables.
overlord.dVariables()

#Open COM port to tether the bot.
#ser = serial.Serial('/dev/ttyUSB0', 57600)

#/////////////////// Overlord Module Settings //////////////////////

#Frames passed before object is considered tracked.
#overlord.trackingFidelityLim = 150

#Frames to wait before moving.
#Defaults to 160
#overlord.waitedFrames = 160

#How close to does the robot need to be? Greater is less accurate.
#Defaults to 5.
#overlord.targetProximity = 5

#GUI X, Y 
#Defaults to 0, 0
#overlord.guiX = 440
#overlord.guiY = 320

#Random target constraint; so target doesn't get placed too far from center.
#Defaults to 1, 640, 1, 480
#overlord.targetLeftLimit = 20
#overlord.targetRightLimit = 400
#overlord.targetBottomLimit = 320
#overlord.targetTopLimit = 20

#/////////////////// Overlord Module Settings //////////////////////

def OpenCV():
    #Execute the Overlord.
    overlord.otracker()

#def rx():
  #  while(True):
        # Read the newest output from the Arduino
   #     if ser.readline() != "":
    #        rx = ser.readline()
            #This is supposed to take only the first three digits.
     #       rx = rx[:3]
                
            #This removes any EOL characters
      #      rx = rx.strip()
                
            #If the number is less than 3 digits, then it will be included
            #we get rid of it so we can have a clean str to int conversion.
       #     rx = rx.replace(".", "")
        
            #Here, you pass Overlord your raw compass data.  The very first reading it gets
            #it stores and uses to offset every other reading.  The off set amount depends on
            #which direction you have the bot facing when it's initialized.  In short, the
            #direction the robot is facing at the beginning is what it will call "North."
        #    overlord.compass(int(rx))

    
def Compasscallback(data):
    rospy.loginfo(rospy.get_caller_id() + 'Compass Heading Degree %s', data.data)
    overlord.compass(data.data) 
    
def Compasslistener():

    # In ROS, nodes are uniquely named. If two nodes with the same
    # name are launched, the previous one is kicked off. The
    # anonymous=True flag means that rospy will choose a unique
    # name for our 'listener' node so that multiple listeners can
    # run simultaneously.
    rospy.init_node('Compasslistener', anonymous=True)

    rospy.Subscriber('HeadingDegree', Int32, Compasscallback)

    # spin() simply keeps python from exiting until this node is stopped
        
    
    
def motorTimer():
        
    while(1):
        #This is for threading out the motor timer.  Allowing for control
        #over the motor burst duration.  There has to be both, something to write and
        #the motors can't be busy.
        if overlord.tranx_ready == True and overlord.motorBusy == False:
         #   ser.write(overlord.tranx)
         #   ser.flushOutput() #Clear the buffer?
            overlord.motorBusy = True
            overlord.tranx_ready = False
        if overlord.motorBusy == True:
            sleep(.2) #Sets the motor burst duration.
         #   ser.write(overlord.stop)
            sleep(.3) #Sets time inbetween motor bursts.
            overlord.motorBusy = False


#Threads the serial functions.
#Compasslistener = threading.Thread(target=Compasslistener)
#Compasslistener.start()

#Threads OpenCV stuff.        
OpenCV = threading.Thread(target=OpenCV)
OpenCV.start()


#Threads the motor functions.
motorTimer = threading.Thread(target=motorTimer)
motorTimer.start()

   # if __name__ == '__main__':
Compasslistener()
rospy.spin()