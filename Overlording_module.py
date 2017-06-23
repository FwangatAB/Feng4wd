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

    
def Compasscallback(data):
    overlord.compass(data.data) 
    
    
def overlordnode():

    pub = rospy.Publisher('cmd_4wd', Int32, queue_size=10)
       
    rospy.init_node('overlordnode', anonymous=True)

    rospy.Subscriber('HeadingDegree', Int32, Compasscallback)
    
    rate = rospy.Rate(10)

    while not rospy.is_shutdown():
        val = overlord.tranx
        pub.publish(Int32(val))
        rate.sleep()
       
def motorTimer():
        
   while(1):
       
        
        #This is for threading out the motor timer.  Allowing for control
        #over the motor burst duration.  There has to be both, something to write and
        #the motors can't be busy.
       
        if overlord.tranx_ready == True and overlord.motorBusy == False:
            print "motor parameters %s %s %s" % (overlord.tranx, overlord.tranx_ready, overlord.motorBusy)
            overlord.motorBusy = True
            overlord.tranx_ready = False
        if overlord.motorBusy == True:
            sleep(.2) #Sets the motor burst duration.
            print val
            sleep(.3) #Sets time inbetween motor bursts.
            overlord.motorBusy = False


#Threads the serial functions.
#Compasslistener = threading.Thread(target=Compasslistener)
#Compasslistener.start()

#Threads OpenCV stuff.        
OpenCV = threading.Thread(target=OpenCV)
OpenCV.start()

#Threads the motor functions.
#motorTimer = threading.Thread(target=motorTimer)
#motorTimer.start()

overlordnode()
