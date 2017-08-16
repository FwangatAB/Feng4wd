import rospy
from std_msgs.msg import Int16

def Compasscallback(data):
    compass(data.data) 

def compass(compassReading):
    global compassInitFlag
    global initCompass
    global compassDegree
        
    #The first compass reading --> initCompass
    if compassInitFlag == False:
       initCompass = compassReading
       compassInitFlag = True
       exit 
    
    compassDegree = compassReading
    
def Voltagecallback(data):
    
    global voltage_value
	
    voltage_value = round(VoltageInfo.data/1000,2)
    
def Currentcallback(data):
	
    global current_value
	
    current_value = round(CurrentInfo.data/1000,2)
	    
def RosNodes(motorComm):

    pub = rospy.Publisher('cmd_4wd', Int16, queue_size=10)
       
    rospy.init_node('overlordnode', anonymous=True)

    rospy.Subscriber('HeadingDegree', Int16, ros_module.Compasscallback)
    
    rospy.Subscriber('VoltageInfo', Int16, ros_module.Voltagecallback)
    
    rospy.Subscriber('CurrentInfo', Int16, ros_module.Currentcallback)
    
    rate = rospy.Rate(10)

    while not rospy.is_shutdown():
        pub.publish(Int16(motorComm))
        rate.sleep()

 
