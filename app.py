#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response

import time
import threading

from random import random
from events import door_event

import RPi.GPIO as GPIO

RECORD = False
open_time_stamp = 0

input_pin_no = 19

GPIO.setmode(GPIO.BOARD)
GPIO.setup(input_pin_no, GPIO.IN)


class GPIO_Monitor(object):
    thread = None  # background thread that reads frames from camera

    def __init__(self):
        """Start the background camera thread if it isn't running yet."""


        # start background frame thread
        GPIO_Monitor.thread = threading.Thread(target=self._thread)
        GPIO_Monitor.thread.start()


    @classmethod
    def _thread(cls):
        """Camera background thread."""
        print('Starting GPIO_Monitor thread.')
        '''
        r_pre = 0
        while True:
            print("check GPIO")
            ran = random()
            threshold = 0.91
            if ran >= threshold and r_pre < threshold:
                RECORD = True
                door_event.set()
                print(door_event.isSet())
                print("Record")
            else:
                RECORD = False
                door_event.clear()
                print(door_event.isSet())
            if RECORD == False:
                time.sleep(2)
            else:
                time.sleep(40)
        '''
        if GPIO.input(input_pin_no)== 1:
            print ('Door is opened!')
            RECORD = True
            door_event.set()
        else:
            RECORD = False
            door_event.clear()
        if RECORD == False:
            time.sleep(2)
        else:
            time.sleep(40)
            
        








# import camera driver
if os.environ.get('CAMERA'):
    Camera = import_module('camera_' + os.environ['CAMERA']).Camera
else:
    from camera import Camera

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)


@app.route('/')
def index():
    print("def index():")
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    print("def gen(camera):")
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    print("def video_feed():")
    """Video streaming route. Put this in the src attribute of an img tag."""
    print("Response client")
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    
    #door_event = threading.Event()
    
    gpio_thread = GPIO_Monitor()
    camera = Camera()
    
    app.run(host='0.0.0.0', port =9090,threaded=True)
    
        
