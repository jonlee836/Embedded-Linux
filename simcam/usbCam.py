#!/home/pi/.virtualenvs/cv/bin/python

from imutils.video import WebcamVideoStream
from comms import send_msg, get_msg

import subprocess
import numpy as np
import datetime
import imutils
import json
import time
import cv2

def webcamFeed():

    with open('camfeed.json') as data_file:
        conf = json.load(data_file)

    ImgPath = "/home/pi/gitstorage/simcam/images/"

    vs = WebcamVideoStream(src=0).start()
    
    time.sleep(conf["camera_warmup_time"])

    lastUploaded_time = datetime.datetime.now()
    lastmsgCheck = datetime.datetime.now()

    secondsSinceUpload = 0
    motionCounter = 0
    avg = None

    while True:

        timestamp = datetime.datetime.now()        
        largest_area = 0

        image = vs.read()
        image = imutils.resize(image, width=640, height=480)
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)

        ts = timestamp.strftime("%A %d %B %Y %I : %M : %S")

        #on start
        if avg is None:
            avg = gray.copy().astype("float")
            #rawCapture.truncate(0)
            continue

        cv2.accumulateWeighted(gray, avg, 0.5)
        frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))

        thresh = cv2.threshold(frameDelta, conf["delta_thresh"], 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=7)

        (cnts, _) = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]
        
        cv2.putText(image, ts, (10, image.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 0, 0), 2) # time date bottom left
        cv2.putText(image, ts, (10, image.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 0), 1)

        motionCounter = context(cnts, image, timestamp, lastUploaded_time, motionCounter)
        
        key = cv2.waitKey(1) & 0xFF

        #trouble shooting
        cv2.imshow("image", image)

        if key == ord("q"):
            #cv2.destroyAllWindows()
            break

        #clear stream for next frame       
        #rawCapture.truncate(0)

        if (timestamp - lastmsgCheck).seconds >= conf["reCheck_Time"]:
            lastmsgCheck = timestamp
            
            if get_msg() == "OFF":
                send_msg("SYSTEM OFFLINE")
                #cv2.destroyAllWindows()
                #vs.stop()
                print "OFF"
                return    

def context(cnts, image, timestamp, lastUploaded_time, motionCounter):

    with open('camfeed.json') as data_file:
        conf = json.load(data_file)

    ts = timestamp.strftime("%A %d %B %Y %I : %M : %S")
    img_name = "images/" + ts + ".jpg"
        
    for c in cnts:

        if motionCounter < 0:
            motionCounter = 0

        if cv2.contourArea(c) >= conf["min_area"]:
            if (timestamp - lastUploaded_time).seconds >= conf["min_upload_seconds"]:
                motionCounter += 1

                if motionCounter >= conf["min_motion_frames"]:

                    largest_area = cv2.contourArea(c)
                    lastUploaded_time = timestamp

                    motionCounter = 0

                    if conf["AlarmStatus"]:
                        #camera.capture(img_name)
                        cv2.imwrite(img_name, image)
                        send_msg("alarm triggered!", img_name)

                        print "MSG SENT"

                        break
        else:
            motionCounter -= 1

    return motionCounter
