import os
import cv2
import time
from base_camera import BaseCamera

from events import door_event

from email_sender import send_email



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
        frame_cnt = 0

        while True:
            # read current frame
            _, img = camera.read()
            
            
            if door_event.isSet() == True:
                frame_cnt += 1
                if newEvent == True:
                    newEvent = False
                    dateTimeStr = time.strftime("%Y-%m-%d-%H_%M_%S")
                    fname = dateTimeStr+'.avi'
                    q_fname = dateTimeStr+'_q.avi'
                    out = cv2.VideoWriter(fname,cv2.VideoWriter_fourcc('M','J','P','G'), 24, size,True)
                    q_out = cv2.VideoWriter(q_fname,cv2.VideoWriter_fourcc('M','J','P','G'), 8, q_size,True)
                
                out.write(img)
                img = cv2.resize(img, q_size)
                if frame_cnt % 3 == 0:
                    q_out.write(img)
            else:
                frame_cnt = 0
                if newEvent == False: # just finish recording
                    #send email
                    out.release()
                    q_out.release()
                    print("sending email")
                    send_email(q_fname)
                    
                newEvent = True
                

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()
            
    
        
