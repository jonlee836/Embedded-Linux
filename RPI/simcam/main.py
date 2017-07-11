#!/home/pi/.virtualenvs/cv/bin/python

import os
import time
import datetime

from threading import Thread

from usbCam import webcamFeed
from usePicam import PiCamfeed

from comms import get_msg
from comms import send_msg

def main():

    while True:

        #check every 5 seconds for commands
        foo = datetime.datetime.now()
    
        time.sleep(5)
        status = get_msg()
        
        if status == "ON":
            print "ON"
            send_msg("SYSTEM ONLINE")
            webcamFeed()
            #PiCamfeed()

        #I'm not sure how to safetly shut off the camera from the main function
        #Right now the camfeed function listens on its own for an OFF command
        #from the user's phone.

        elif status == "OFF":
            send_msg("SYSTEM OFFLINE")
            break
        
        print foo

if __name__ == '__main__':
    main()
