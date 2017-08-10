import rospy
from std_msgs.msg import Int16
import serial
import threading
import module1


module1.printo()

#Initialize Overlord variables.
module1.dVariables()

def OpenCV():
    #Execute the Overlord.
    module1.otracker()

    
def Compasscallback(data):
    module1.compass(data.data) 

def Voltagecallback(data):
	module1.voltage(data.data)
    
def Currentcallback(data):
	module1.current(data.data)
	    
def overlordnode():

    pub = rospy.Publisher('cmd_4wd', Int16, queue_size=10)
       
    rospy.init_node('overlordnode', anonymous=True)

    rospy.Subscriber('HeadingDegree', Int16, Compasscallback)
    
    rospy.Subscriber('VoltageInfo', Int16, Voltagecallback)
    
    rospy.Subscriber('CurrentInfo', Int16, Currentcallback)
    
    rate = rospy.Rate(10)

    while not rospy.is_shutdown():
        val = module1.tranx
        pub.publish(Int16(val))
        rate.sleep()
       
      
OpenCV = threading.Thread(target=OpenCV)
OpenCV.start()

overlordnode()
