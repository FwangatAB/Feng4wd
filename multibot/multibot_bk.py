#!/usr/bin/env python

'''
This is the multibot 1.0 modified by Feng Wang on 08/11/2017

    To initialize tracking, select the object with mouse

Keys:
-----
    ESC   - exit
    b     - toggle back-projected probability visualization
'''

# Python 2/3 compatibility
from __future__ import print_function
import sys
PY3 = sys.version_info[0] == 3

if PY3:
    xrange = range

import numpy as np
import cv2
import math
from math import atan2, degrees, pi

# local module
import video
import ros_module


def settings():
	
    #How many frames before we consider the object being tracked.
    trackConformFrame = 60

    #How many frames to wait before moving.
    waitedFrame = 50
    iFrame = 0
    initPositionFlag = False
	
    #Proximity to target threshold.
    targetProximity = 0
 
    #Helps control the gui placement.
    guiX = 0
    guiY = 0
    
    #global values from compass(), need to define as global here, or only once in the ros_module?
    global headingDegrees    
    headingDegrees = 0
    derivateDegree = 30
       
    global compassInitFlag
    compassInitFlag = False
    
    calibFlag = False

    global initCompass
    initCompass = 0    
	
    #///////////////// Motor Control Variables /////////////////////////////

    right = 4
    left = 2
    forward = 3
    stop = 5
    back = 1


def draw_str():
	 
	#Background for text.
    cv2.rectangle(vis, (guiX+18,guiY+2), (guiX+170,guiY+160), (255,255,255), -1)
    cv2.putText(vis,"MultiBot:"+str(botPosition.X)+" , "+str(botPosition.Y),(guiX+20,guiY+20),cv2.FONT_HERSHEY_COMPLEX_SMALL,.7,(0,0,0))
    cv2.putText(vis,"Target:"+str(targetPoint.X)+" , "+str(targetPoint.Y),(guiX+20,guiY+40),cv2.FONT_HERSHEY_COMPLEX_SMALL,.7,(0,0,0))
    cv2.putText(vis,"Compass initReading: "+str(calibrDegree)+" Deg",(guiX+20,guiY+60),cv2.FONT_HERSHEY_COMPLEX_SMALL,.7,(0,0,0))
    cv2.putText(vis,"Target deg: "+str(adjustDegree)+" Deg",(guiX+20,guiY+100),cv2.FONT_HERSHEY_COMPLEX_SMALL,.7,(0,0,0))
    cv2.putText(vis,"Bot turningdeg: "+str(delatDegree)+" Deg",(guiX+20,guiY+80),cv2.FONT_HERSHEY_COMPLEX_SMALL,.7,(0,0,0))
    cv2.putText(vis,"Voltage: "+str(voltage_value)+" volt",(guiX+20,guiY+120),cv2.FONT_HERSHEY_COMPLEX_SMALL,.7,(0,0,0))
    cv2.putText(vis,"Current: "+str(current_value)+" amp",(guiX+20,guiY+140),cv2.FONT_HERSHEY_COMPLEX_SMALL,.7,(0,0,0))



def calibrate_base():
	
	#Calibration process
	if initPositionFlag is False:
		initPosition = botPostion
		initPositionFlag is true
			
	while iFrame < waitedFrame:
		motorComm = 3
		iFrame = iFrame + 1 
				
	motorComm = 5
	
	rads = atan2((botPosition.y - initPosition.y),(botPostion.x - initPosition.x))
	Initdegs = degrees(rads)
	#offset -180 -> 0 degrees to 180 -> 360 degrees			
	if Initdegs < 0 & Initdegs >= -180:
		Initdegs = 360 + Initdegs
	CalibrDegree = ros_module.initCompass - Initdegs  # the compass degree when multibot is heading parale with x axis.
'''

degrees(atan2(y,x))  
					90
					|
					y
					|
    180(-180)-------|----x---0
					|
					|
					|
			       -90
			   
'''

def base_comm(targetPoint):
	while (sqrt((botposition.y ** 2 - targetPoint.y ** 2)+(botposition.x ** 2 -targetPoint.y ** 2)) > targetProximity):
		rads = atan2((botPosition.y - targetPoint.y),(botPosition.x - targetPoint.y))
		degs = degrees(rads)
		if degs < 0 & degs >= -180:
			degs +360 + degs
		adjustDegree = ros_module.compassDegree - calibrDegree
		deltaDegs = degs - adjustDegree
		if deltaDegs >= derivateDegree and deltaDegs < 180:
			motorComm = 4
		if deltaDegs <= (- derivateDegree) and deltagDegs > -180:
			motorComm = 2
		else:
			motorComm = 3
	
	motorComm = 5

def base_run():
	if clibFlag is False & tracking_state == 1:
		calibrate_base
		base_comm(5,5)
		clibFlag is True
	if clibFlag is True & tracking_state == 1:
		mapServer
		base_comm(targetPoint)
			
def mapServer():
	if botPosition.y <=355:
		if botPosition.x = 5:
			targetPoint.y = botPosition.y + 20
			targetPoint.x = 475
		if botPosition.x = 475:
			targetPoint.y = botPosition.y + 20
			targetPoint.x = 5
		else: 
			motorComm = 3
				
	else:
		base_comm(5,5)
	
class App(object):
    def __init__(self, video_src):
        self.cam = video.create_capture(video_src)
        ret, self.frame = self.cam.read()
        cv2.namedWindow('Multibot monitor')
        cv2.setMouseCallback('Multibot monitor', self.onmouse)

        self.selection = None
        self.drag_start = None
        self.tracking_state = 0
        self.show_backproj = False

    def onmouse(self, event, x, y, flags, param):
        x, y = np.int16([x, y]) # BUG
        if event == cv2.EVENT_LBUTTONDOWN:
            self.drag_start = (x, y)
            self.tracking_state = 0
            return
        if self.drag_start:
            if flags & cv2.EVENT_FLAG_LBUTTON:
                h, w = self.frame.shape[:2]
                xo, yo = self.drag_start
                x0, y0 = np.maximum(0, np.minimum([xo, yo], [x, y]))
                x1, y1 = np.minimum([w, h], np.maximum([xo, yo], [x, y]))
                self.selection = None
                if x1-x0 > 0 and y1-y0 > 0:
                    self.selection = (x0, y0, x1, y1)
            else:
                self.drag_start = None
                if self.selection is not None:
                    self.tracking_state = 1

    def show_hist(self):
        bin_count = self.hist.shape[0]
        bin_w = 24
        img = np.zeros((256, bin_count*bin_w, 3), np.uint8)
        for i in xrange(bin_count):
            h = int(self.hist[i])
            cv2.rectangle(img, (i*bin_w+2, 255), ((i+1)*bin_w-2, 255-h), (int(180.0*i/bin_count), 255, 255), -1)
        img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
        cv2.imshow('hist', img)

    def run(self):
        while True:
            ret, self.frame = self.cam.read()
            vis = self.frame.copy()
            hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, np.array((0., 60., 32.)), np.array((180., 255., 255.)))

            if self.selection:
                x0, y0, x1, y1 = self.selection
                self.track_window = (x0, y0, x1-x0, y1-y0)
                hsv_roi = hsv[y0:y1, x0:x1]
                mask_roi = mask[y0:y1, x0:x1]
                hist = cv2.calcHist( [hsv_roi], [0], mask_roi, [16], [0, 180] )
                cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
                self.hist = hist.reshape(-1)
                self.show_hist()

                vis_roi = vis[y0:y1, x0:x1]
                cv2.bitwise_not(vis_roi, vis_roi)
                vis[mask == 0] = 0

            if self.tracking_state == 1:
                self.selection = None
                prob = cv2.calcBackProject([hsv], [0], self.hist, [0, 180], 1)
                prob &= mask
                term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )
                track_box, self.track_window = cv2.CamShift(prob, self.track_window, term_crit)

				#Take the centroid of the CamShift.
                tupX, tupY = track_box[0][0], track_box[0][1]    #track_box.center.y and track_box.center.x ?
				#Convert bot coordinations from floats in a tuple to an integer.
                botPosition = (Int(tupX),Int(tupY))
            
                if self.show_backproj:
                    vis[:] = prob[...,np.newaxis]
                try:
                    cv2.circle(vis, botPosition, 10, (0, 0, 255), -1)
                    cv2.circle(vis, targetPoint, 10, (0, 255,0), -1)
                    cv2.line(vis, botPosition, targetPoint, (255, 0,0), 1)
                except:
                    print(track_box)
            draw_str()
            cv2.imshow('Multibot Monitor', vis)

            ch = 0xFF & cv2.waitKey(5)
            if ch == 27:
                break
            if ch == ord('b'):
                self.show_backproj = not self.show_backproj
        motorComm = 5
        cv2.destroyAllWindows()


if __name__ == '__main__':
    import sys
    try:
		video_src = 0
    except:
        video_src = sys.argv[1]
    print(__doc__)
    
    OpenCV = threading.thread(target = App(video_src).run)
    OpenCV.start()
    
    MotorMove = threading.thread(target = base_run)
    MotorMove.start()
    
    ros_module.RosNodes
    
    
  
