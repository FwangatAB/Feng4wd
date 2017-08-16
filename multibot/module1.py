# Python 2/3 compatibility
from __future__ import print_function
import sys
PY3 = sys.version_info[0] == 3

if PY3:
    xrange = range

import numpy as np
import cv2
from math import atan2, degrees, pi 
import random
import math 

# local module
import video

#Tests module
def printo():
    print "Feng's MultBot module 1.0"
    print "Feng Wang"
    print "08/08/2017"

#/////////////////// Multibot Module Settings //////////////////////
def dVariables():
    #For converting the compass heading into an integer
    global intDegree
    intDegree = 0

    #Holds the frame index
    global iFrame
    iFrame = 0

    #How many frames before we consider the object being tracked.
    global trackConfirmFrame
    trackConformFrame = 60

    #How many frames to wait before moving.
    global waitedFrames
    waitedFrames = 50

    #Proximity to target threshold.
    global targetProximity
    targetProximity = 5
 
    #Helps control the gui placement.
    global guiX
    global guiY
    guiX = 0
    guiY = 0
    
    #headingDegrees holds the compass heading. Lets make it an integer.
    global headingDegrees    
    headingDegrees = 0
    
    #Used to determine whether the first compass reading has arrived.
    global compassInitFlag
    compassInitFlag = False

    global initCompass
    initCompass = 0    

    #///////////////// End Main Control Variables //////////////////////////

    #///////////////// Color Selector Variables //////////////////////////
    global selection, drag_start, tracking_state, show_backproj, down_x, down_y
    global mouseX, mouseY, trackBoxShow

    selection = None
    drag_start = None
    tracking_state = 0
    show_backproj = False

    trackBoxShow = False
    mouseX = 0
    mouseY = 0
    
    down_x = 0
    down_y = 0    
    
    #Flag to assuring we have something to say serially.
    global tranx_ready
    global moveComm
    tranx_ready = False
    #Carries what we have to say.
    moveComm = 5

    #///////////////// Motor Control Variables /////////////////////////////

    global right, left, forward, stop, back
    right = 4
    left = 2
    forward = 3
    stop = 5
    back = 1

#//////////////// WIP //////////////////////////////////
def onmouse(event, x, y, flags, param):
    global selection, drag_start, tracking_state, show_backproj, down_x, down_y, selcFrame
    global mouseX, mouseY, trackBoxShow
    x, y = np.int16([x, y]) #[sic] BUG
    mouseX = x
    mouseY = y
    if event == cv2.EVENT_LBUTTONDOWN:
        down_x = x
        down_y = y
        drag_start = (x, y)
        tracking_state = 0
        trackBoxShow = True
    if event == cv2.EVENT_LBUTTONUP:
        trackBoxShow = False
    if drag_start:
        if flags & cv2.EVENT_FLAG_LBUTTON:
            h, w = selcFrame.shape[:2]
            xo, yo = drag_start
            x0, y0 = np.maximum(0, np.minimum([xo, yo], [x, y]))
            x1, y1 = np.minimum([w, h], np.maximum([xo, yo], [x, y]))
            selection = None
            if x1-x0 > 0 and y1-y0 > 0:
                selection = (x0, y0, x1, y1)
        else:
            drag_start = None
            if selection is not None:
                tracking_state = 1
                
def mapper(x, in_min, in_max, out_min, out_max):
    #This will map numbers onto others.
    return ((x-in_min)*(out_max -out_min)/(in_max - in_min) + out_min)

def compass(headingDegrees):
    global compassInitFlag
    global initCompass
    global intDegree
    
    
    #This sets the first compass reading to our 0*.
    if compassInitFlag == False:
       initCompass = headingDegrees
       compassInitFlag = True
       print "this is initial heading degree %s" % initCompass
       exit 

    #This is the function that actually maps offsets the compass reading.
    
    if headingDegrees >= initCompass:
        adjHeading = mapper(headingDegrees, initCompass, 360, 0, (360-initCompass))
    elif headingDegrees <= initCompass:
        adjHeading = mapper(headingDegrees, 0, (initCompass-1),(360-initCompass), 360)
    
    #Here, our compass reading is loaded into intDegree
    
    intDegree = adjHeading
    
    print "adjHeading from compass function %s" % adjHeading
    
def voltage(VoltageInfo):
	global voltage_value
	
	voltage_value = round(VoltageInfo/100,2)

def current(CurrentInfo):
	global current_value
	
	current_value = round(CurrentInfo/100,2)
	
def otracker():
    #Create video capture
    cap = cv2.VideoCapture(0)

    #Globalizing variables
    global moveComm 
    global intDegree
    global iFrame 
    global shortestAngle
    global tranx_ready
    global trackConformFrame
    global left, right, forward
    global guiX, guiY

    global selection, drag_start, tracking_state, show_backproj
    global selcFrame
        
    #These are the centroid of the camShift.
    global cscX
    global cscY
    cscX, cscY = 0, 0
    moveComm = 5 
    #Variable to find target angle. (Used in turning the bot toward target.)
    shortestAngle = 0
    global startFlag 
    
    #Flag for getting a new target.
    newTarget = True
    startFlag = True
    #Dot counter. He's a hungry hippo...
    dots = 0
      
          
    while(1):
        #Read the frames
        _,frame = cap.read()
    
        #Smooth it
        frame = cv2.blur(frame,(3,3))

        #frame for color selector.
        ret, selcFrame = cap.read()
        vis = frame.copy()
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array((0., 60., 32.)), np.array((180., 255., 255.)))
        
        #Code stolen from the camShift example.
        if selection:
            x0, y0, x1, y1 = selection
            track_window = (x0, y0, x1-x0, y1-y0)
            hsv_roi = hsv[y0:y1, x0:x1]
            mask_roi = mask[y0:y1, x0:x1]
            hist = cv2.calcHist( [hsv_roi], [0], mask_roi, [16], [0, 180] )
            cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX);
            hist = hist.reshape(-1)

        if tracking_state == 1:
            selection = None
            prob = cv2.calcBackProject([hsv], [0], hist, [0, 180], 1)
            prob &= mask
            term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1)
            track_box, track_window = cv2.CamShift(prob, track_window, term_crit)
            #Take the centroid of the CamShift.
            tupX, tupY = track_box[0][0], track_box[0][1]
            #Convert these numbers from floats in a tuple to an integer.
            cscX = int(tupX)
            cscY = int(tupY)
            if show_backproj:
                vis[:] = prob[..., np.newaxis]
        
        #"printDegree" is separate in case I want to parse out other sensor data
        #from the bot
        intHeadingDeg = intDegree
        headingDeg = str(intDegree)
        
        #Strings to hold the "Target Lock" status.     
        stringXOk = " "
        stringYOk = " "
        
        #Incrementing frame index
        iFrame = iFrame + 1
        print "iFrame is %s" % iFrame
        #Convert to hsv and find range of colors
        thresh = mask
        thresh2 = thresh.copy()

        #Randomizing target.
       
        if newTarget == True:
			if startFlag == True:
				tX = 1
				tY = 1 
#				startFlag = False
			
			elif tY <= 480:
				if tX == 1:
					tX = 640
					tY = + 20
				else:
					tX = 1
					tY = + 20 
			else:
				tX = 1
				tY = 1
				startFlag = True
                
        newTarget = False

        #Did our robot eat the dot?
        if abs(tX-cscX)<=5 & abs(tY-cscY)<=5:
           newTarget = True
                
        
        #Slope
        dx = cscX - tX
        dy = cscY - tY
        
        #Quad I -- Good
        if tX >= cscX and tY <= cscY:
            rads = atan2(dy,dx)
            degs = degrees(rads)
            degs = degs - 90
        #Quad II -- Good
        elif tX >= cscX and tY >= cscY:
            rads = atan2(dx,dy)
            degs = degrees(rads)
            degs = (degs * -1)
        #Quad III
        elif tX <= cscX and tY >= cscY:
            rads = atan2(dx,-dy)
            degs = degrees(rads)
            degs = degs + 180
        #Quad VI
        elif tX <= cscX and tY <= cscY:
            rads = atan2(dx,-dy)
            degs = degrees(rads) + 180
        
        #Convert float to int
        targetDegs = int(math.floor(degs))
        
        #Variable to print the degrees offset from target angle.
        strTargetDegs = " "
        
        #Put the target angle into a string to printed.
        strTargetDegs = str(math.floor(degs))
        print "TargetDegs from otracker function %s" % targetDegs
        
        #///End Finding Target Angle////////////////////////////////////

        
        #//// Move Bot //////////////////////////////////////
        
        #Don't start moving until things are ready.
        if iFrame >= waitedFrames:
            #This compares the bot's heading with the target angle.  It must
            #be +-30 for the bot to move forward, otherwise it will turn.
            shortestAngle = targetDegs - intHeadingDeg
                        
            if shortestAngle > 180:
                shortestAngle -= 360
            if shortestAngle < -180:
                shortestAngle += 360
            print "shortestAngle=targetDegs-intHeadingDeg %s" % shortestAngle   
            #Do we move left, right, or forward.
            if shortestAngle <= 30 and shortestAngle >= -30:
                #tranx = (forward)
                moveComm = 3
                tranx_ready = True
            elif shortestAngle > 30:
                #tranx = (left)
                moveComm = 4
                tranx_ready = True
            elif shortestAngle < -30:
                #tranx = (left)
                moveComm = 2
                tranx_ready = True
                 
            
        #//// End Move Bot //////////////////////////////////
        
        print ('motor command is %s' % moveComm)
        
        #////////CV Dawing//////////////////////////////
        
        if tracking_state > 0:
            #Robot circle.
            cv2.circle(frame,(cscX,cscY),10,255,-1)
            print "coordination of dot %s" % cscX, cscY
            #Target angle.
            cv2.line(frame, (tX,tY), (cscX, cscY),(0,255,0), 1)

        #Target circle
        cv2.circle(frame, (tX, tY), 10, (0, 0, 255), thickness=-1)
        
        #ser.write(botXY)
        
        #Background for text.
        cv2.rectangle(frame, (guiX+18,guiY+2), (guiX+170,guiY+160), (255,255,255), -1)
        
        if trackBoxShow == True:
            cv2.rectangle(frame, (down_x, down_y), (mouseX,mouseY), (0,255,0), 1)

        
        #Bot's X and Y is written to image
        cv2.putText(frame,"Bot position:"+str(cscX)+" , "+str(cscY),(guiX+20,guiY+20),cv2.FONT_HERSHEY_COMPLEX_SMALL,.7,(0,0,0))
		#Next Target's X and Y is written to image
        cv2.putText(frame,"Next target:"+str(tX)+" , "+str(tY),(guiX+20,guiY+40),cv2.FONT_HERSHEY_COMPLEX_SMALL,.7,(0,0,0))
		#Print the compass to the frame.
        cv2.putText(frame,"Bot inital deg: "+str(initCompass)+" Deg",(guiX+20,guiY+60),cv2.FONT_HERSHEY_COMPLEX_SMALL,.7,(0,0,0))
        cv2.putText(frame,"Bot turning deg: "+str(shortestAngle)+" Deg",(guiX+20,guiY+80),cv2.FONT_HERSHEY_COMPLEX_SMALL,.7,(0,0,0))
        cv2.putText(frame,"Target deg: "+strTargetDegs+" Deg",(guiX+20,guiY+100),cv2.FONT_HERSHEY_COMPLEX_SMALL,.7,(0,0,0))
        cv2.putText(frame,"Voltage: "+str(voltage_value)+" volt",(guiX+20,guiY+120),cv2.FONT_HERSHEY_COMPLEX_SMALL,.7,(0,0,0))
        cv2.putText(frame,"Current: "+str(current_value)+" amp",(guiX+20,guiY+140),cv2.FONT_HERSHEY_COMPLEX_SMALL,.7,(0,0,0))
                
        #After the frame has been modified to hell, show it.
        cv2.imshow('frame',frame) #Color image
        #cv2.imshow('thresh',thresh2) #Black-n-White Threshold image

        cv2.setMouseCallback('frame', onmouse)
        
        #/// End CV Draw //////////////////////////////////////

        
        if cv2.waitKey(33)== 27:
            # Clean up everything before leaving
            cap.release()
            cv2.destroyAllWindows()
            #Tell the robot to stop before quit.
            moveComm = 5
            break
