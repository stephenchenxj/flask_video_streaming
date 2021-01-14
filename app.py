#!/usr/bin/env python
from importlib import import_module
import os
from flask import Flask, render_template, Response

import time
import threading

from random import random

RECORD = False
open_time_stamp = 0


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
        r_pre = 0
        while True:
            print("check GPIO")
            ran = random()
            threshold = 0.95
            if ran >= threshold and r_pre < threshold:
                RECORD = True
                print("Record")
            else:
                RECORD = False
            if RECORD == False:
                time.sleep(2)
            else:
                time.sleep(10)








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
    """Video streaming home page."""
    return render_template('index.html')


def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    print("Response client")
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    
    gpio_thread = GPIO_Monitor()
    
    app.run(host='0.0.0.0', port =9090,threaded=True)
    
        
