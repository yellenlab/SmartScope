from matplotlib import pyplot as plt
import time
import cv2
import utils

def py_lab():
    cam = utils.start_cam()
    try:
        while True:
            t1 = time.time()
            t2 = time.time()
            frame = cam.get_frame(exp_time=1).reshape(cam.sensor_size[::-1])
            print (frame.shape)
            plt.imshow(frame, cmap="gray")
            t3 = time.time()
            plt.imshow(frame, cmap="gray")
            plt.pause(.1)
            plt.cla()
            t4 = time.time()
            print('time to get: '+ str(t2-t1))
            print('time to imshow: '+ str(t3-t2))
            print('time to save: '+ str(t4-t3)+'\n\n')

    except KeyboardInterrupt:
        utils.close_cam(cam)


# This method of displaying the live image is prone to crashing 
def opencv():
    cam = utils.start_cam()
    try:
        print ("Camera started")
        while True:
            frame = cam.get_live_frame().reshape(cam.sensor_size[::-1])
            frame = cv2.resize(frame,dim, interpolation = cv2.INTER_AREA)
            cv2.imshow('Live Mode', frame)
    except KeyboardInterrupt:
        utils.close_cam(cam)

if __name__=="__main__":
    py_lab()
    #opencv()