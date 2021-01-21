import io
import time
import picamera
from base_camera import BaseCamera

from events import door_event
from email_sender import send_email


class Camera(BaseCamera):
    @staticmethod
    def frames():
        with picamera.PiCamera() as camera:
            # let camera warm up
            time.sleep(2)

            stream = io.BytesIO()
            camera.resolution = (640,480)
            
            newEvent = True
            frame_cnt = 0
        
        
            for _ in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # return current frame
                stream.seek(0)
                
                if door_event.isSet() == True:
                    frame_cnt += 1
                    if newEvent == True:
                        newEvent = False
                        dateTimeStr = time.strftime("%Y-%m-%d-%H_%M_%S")
                        fname = dateTimeStr+'.avi'
                        q_fname = dateTimeStr+'_q.avi'
                        camera.start_recording( q_fname )
                        
                        
                else:
                    frame_cnt = 0
                    if newEvent == False: # just finish recording
                        camera.stop_recording()
                        #send email
                        print("sending email")
                        send_email(q_fname)
                        
                    newEvent = True
                
                
                yield stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()
