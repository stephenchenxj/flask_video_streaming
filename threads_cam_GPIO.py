#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 14:44:27 2021

@author: xujianchen
"""
import os
import cv2

import threading
import time


    
import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from base_camera import BaseCamera


event_door_open = threading.Event()
filename = "/Users/xujianchen/github/video_streaming/small.avi"  # In same directory as script


def send_email(file_name):
    subject = "An email with attachment from Python"
    body = "This is an email with attachment sent from Python"
    sender_email = "hs.diy.sf@gmail.com"
    receiver_email = "stephenchenKL@gmail.com"
    # password = input("Type your password and press enter:")
    password = "specialforce"
    
    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails
    
    # Add body to email
    message.attach(MIMEText(body, "plain"))
    
    filename =file_name  # In same directory as script
    
    # Open PDF file in binary mode
    with open(filename, "rb") as attachment:
        # Add file as application/octet-stream
        # Email client can usually download this automatically as attachment
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    
    # Encode file in ASCII characters to send by email    
    encoders.encode_base64(part)
    
    # Add header as key/value pair to attachment part
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {filename}",
    )
    
    # Add attachment to message and convert message to string
    message.attach(part)
    text = message.as_string()
    
    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    
    # creates SMTP session 
    s = smtplib.SMTP('smtp.gmail.com', 587) 
      
    # start TLS for security 
    s.starttls() 
      
    # Authentication 
    s.login(sender_email, password) 
      
    # Converts the Multipart msg into a string 
    text = message.as_string()
      
    # sending the mail 
    s.sendmail(sender_email, receiver_email, text) 
      
    # terminating the session 
    s.quit() 
    
    
    '''
    #with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    with smtplib.SMTP("smtp.gmail.com", 587, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)
    '''
    
    
    





class GPIOThreading:
    def __init__(self):
        self.thread = None
        self.started = True
        
    def threaded_program(self):
        cnt = 0
        while self.started:
            print('GPIO thread is running')
            
            cnt += 1
            if cnt >= 2:
                cnt = 0
                event_door_open.set()
                print('event_door_open is set')
                time.sleep(10) # keep this event for 10 sec, save 10 sec of video
            else:
                event_door_open.clear()
                time.sleep(60)
        print('Left GPIO thread')
                
    def run(self):
        self.thread = threading.Thread(target = self.threaded_program, args=())
        self.thread.start()
    def stop(self):
        self.started = False
        self.thread.join()




class Camera(BaseCamera):
    video_source = 0

    def __init__(self):
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(Camera, self).__init__()

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        
        size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)),
                int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        q_size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)/4),
                  int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)/4))
    
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')
            
        newEvent = True
        
        

        while True:
            # read current frame
            _, img = camera.read()
            
            if event_door_open.isSet() == True:
                if newEvent == True:
                    newEvent = False
                    dateTimeStr = time.strftime("%Y-%m-%d-%H_%M_%S")
                    fname = dateTimeStr+'.avi'
                    q_fname = dateTimeStr+'_q.avi'
                    out = cv2.VideoWriter(fname,cv2.VideoWriter_fourcc('M','J','P','G'), 24, size,True)
                    q_out = cv2.VideoWriter(q_fname,cv2.VideoWriter_fourcc('M','J','P','G'), 24, q_size,True)
                
                out.write(img)
                img = cv2.resize(img, q_size)
                q_out.write(img)
                cv2.waitKey(1)
            else:
                if newEvent == False: # just finish recording
                    out.release()
                    q_out.release()
                    #send email
                    print("sending email")
                    time.sleep(1)
                    send_email(q_fname)
                    time.sleep(1)
                    send_email(filename)
                    
                newEvent = True
                

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()
            

    

def main():
    GPIOmonitor = GPIOThreading()
    
    GPIOmonitor.run()
    
    camera = Camera()
    
    while True:
        frame = camera.get_frame()
        #cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
          break
    
    



    '''
    cnt = 0

    # wait here for the result to be available before continuing
    while event_door_open.wait():
        cnt += 1
        print('main thread acknoledges door open. Email sent at ', time.time())
        send_email(filename)
        time.sleep(1)
            
        if cnt >= 2:
            break
            
    '''
    print("main thread starts to sleep 8 secs")
        
    time.sleep(8)
    GPIOmonitor.stop()
        

        
    


if __name__ == '__main__':
    main()