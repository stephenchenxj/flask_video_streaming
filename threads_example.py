#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 14:44:27 2021

@author: xujianchen
"""


from random import random
import threading
import time


    
import email, smtplib, ssl

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

door_open = threading.Event()
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
            time.sleep(1)
            cnt += 1
            if cnt >= 3:
                cnt = 0
                door_open.set()
                print('door_open is set')
            else:
                door_open.clear()
                
    def run(self):
        self.thread = threading.Thread(target = self.threaded_program, args=())
        self.thread.start()
    def stop(self):
        self.started = False
        self.thread.join()



    

def main():
    GPIOmonitor = GPIOThreading()
    
    GPIOmonitor.run()
    
    cnt = 0
    


    # wait here for the result to be available before continuing
    while door_open.wait():
        cnt += 1
        print('main thread acknoledges door open. Email sent at ', time.time())
        send_email(filename)
        time.sleep(1)
            
        if cnt >= 2:
            break
    print("main thread starts to sleep 8 secs")
        
    time.sleep(8)
    GPIOmonitor.stop()
        
    
        
    


if __name__ == '__main__':
    main()