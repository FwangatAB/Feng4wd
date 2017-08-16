import ros_module
import threading
import module1


module1.printo()

module1.dVariables()

def OpenCV():
    module1.otracker()

      
OpenCV = threading.Thread(target=OpenCV)
OpenCV.start()

ros_module.RosNodes()
