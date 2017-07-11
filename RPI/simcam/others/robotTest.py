from picamera.array import PiRGBArray
from picamera import PiCamera

from matplotlib import pyplot as plt
import imutils
import time
import numpy as np
import cv2
from fractions import Fraction

def nothing(x):
    pass

InputImg = 'image'
guiImg   = 'gui'

cv2.namedWindow(InputImg)
cv2.namedWindow(guiImg)

setCon = 100
setBright = 50
setSharp = 0
setSat = 50
setExpcomp = 17
setMeter = 4
ImgWidth = 640
ImgHeight = 480

RedGain1 = 1
RedGain2 = 35

BlueGain1 = 1
BlueGain2 = 10

setSleepTime = 0.5
setISO = 0
recordImages = 0

expSpeed = 500
shutSpeed = 15000

cv2.createTrackbar('ISO',       guiImg,  setISO, 8,  nothing)

cv2.createTrackbar('RedGain1' , guiImg, RedGain1, 8,  nothing)
cv2.createTrackbar('RedGain2' , guiImg, RedGain2, 100,  nothing)

cv2.createTrackbar('BlueGain1', guiImg, BlueGain1, 8, nothing)
cv2.createTrackbar('BlueGain2', guiImg, BlueGain2, 100, nothing)

cv2.createTrackbar('recordImages', guiImg, recordImages, 1, nothing)
cv2.createTrackbar('shutSpeed', guiImg, shutSpeed, 50000, nothing)
cv2.createTrackbar('setSat', guiImg, setSat, 100, nothing)

cv2.createTrackbar('setCon', guiImg, setCon, 200 ,nothing)
cv2.createTrackbar('setBright', guiImg, setBright, 100, nothing)
cv2.createTrackbar('setSharp', guiImg, setSharp, 100 ,nothing)
cv2.createTrackbar('setSat', guiImg, setSat, 100,nothing)
cv2.createTrackbar('setExpcomp', guiImg, setExpcomp, 50,nothing)
cv2.createTrackbar('setMeter', guiImg, setMeter, 4,nothing)

camera = PiCamera(resolution=(ImgWidth, ImgHeight), framerate=30)

rawCapture = PiRGBArray(camera, size=(ImgWidth, ImgHeight))

time.sleep(setSleepTime)

#camera.shutter_speed = shutSpeed
#camera.shutter_speed = camera.exposure_speed
#camera.exposure_mode = 'off'
camera.awb_mode = 'off'

i=1

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    
    RedGain2  = RedGain2  * 0.01
    BlueGain2 = BlueGain2 * 0.01

    if RedGain1 >= 8:
        RedGain1 = 8

    if BlueGain1 >= 8:
        BlueGain1 = 8
    
    RedGain  = RedGain1 + RedGain2
    BlueGain = BlueGain1 + BlueGain2
    
    setAwb  = (RedGain, BlueGain)

    recordImages = cv2.getTrackbarPos('recordImages', guiImg)    

    RedGain1 = cv2.getTrackbarPos('RedGain1', guiImg)
    RedGain2 = cv2.getTrackbarPos('RedGain2', guiImg)

    BlueGain1 = cv2.getTrackbarPos('BlueGain1', guiImg)
    BlueGain2 = cv2.getTrackbarPos('BlueGain2', guiImg)

    setISO = cv2.getTrackbarPos('ISO', guiImg)
    setISO = setISO * 100

    # I don't think you can adjust shutspeed once it has been set
    expSpeed     = cv2.getTrackbarPos('exposure speed', guiImg)
    
    setSat       = cv2.getTrackbarPos('setSat', guiImg)
    setCon       = cv2.getTrackbarPos('setCon', guiImg) - 100
    setBright    = cv2.getTrackbarPos('setBright', guiImg)
    setSharp     = cv2.getTrackbarPos('setSharp', guiImg)
    setExpcomp   = cv2.getTrackbarPos('setExpcomp', guiImg) - 25
    setMeter     = cv2.getTrackbarPos('setMeter', guiImg)

    mm = 'average'
    
    if setMeter == 0:
        setMeter = 1

    if setMeter == 1:
        mm = 'average'
    elif setMeter == 2:
        mm = 'spot'
    elif setMeter == 3:
        mm = 'backlit'
    elif setMeter == 4:
        mm = 'matrix'
    
    camera.iso = setISO
    camera.contrast = setCon
    camera.brightness = setBright
    camera.sharpness = setSharp
    camera.saturation = setSat
    camera.exposure_compensation = setExpcomp
    camera.awb_gains = setAwb
    camera.meter_mode = mm

    setISO = camera.ISO

    analogGain = camera.analog_gain
    digitalGain = camera.digital_gain
    ss = camera.shutter_speed

    g = setAwb
    
    timeStart = time.time()

    image = frame.array
    
    imgname = "Rg_%.2f_Bg_%.2f_ag_%.2f_dg_%.2f_exp_%d_ss_%d_ISO_%d_sleep_%.1f_mm_%s_%05d.jpg"%(
        RedGain, BlueGain, analogGain, digitalGain, camera.exposure_speed, ss, setISO, setSleepTime, mm, i)    

    if recordImages == 1:
        cv2.imwrite(imgname, image)
    
    cv2.imshow(InputImg, image)
    timeEnd = time.time() - timeStart
    print imgname

    # print i, camera.exposure_speed, camera.shutter_speed, tempIso, analogGain, digitalGain, redGain, blueGain
    key = cv2.waitKey(1) & 0xFF

    rawCapture.truncate(0)
    
    if key == ord("q"):
        break

    i+=1
    
#camera.capture_sequence(['image%0004d.jpg' % i for i in range(10)])
