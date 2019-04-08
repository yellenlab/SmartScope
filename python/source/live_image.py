from pyvcam import pvc
from pyvcam.camera import Camera
# import pylab as pl
from matplotlib import pyplot as plt
import time
import cv2
import numpy as np
import math
import getch

def py_lab():
    pvc.init_pvcam()
    cam = next(Camera.detect_camera())
    cam.open()

    cam.clear_mode = "Never"
    cam.exp_mode = "Ext Trig Trig First"
    cam.readout_port = 0
    cam.speed_table_index = 0
    print(cam.speed_table)
    cam.gain = 1

    # cam.start_live(exp_time=1)
    # cam.start_live_cb(exp_time=1)




    img = None
    # need to make this a while loop, and find a way to escape 
    count = 0
    try:
        while True:

            t1 = time.time()
            # frame = cam.get_live_frame().reshape(cam.sensor_size[::-1])
            # frame = cam.get_live_frame_cb()
            t2 = time.time()
            frame = cam.get_frame(exp_time=1).reshape(cam.sensor_size[::-1])
            print (frame.shape)
            # plt.figure(1)
            # plt.clf()
            plt.imshow(frame, cmap="gray")
            t3 = time.time()
            # print (cam.readout_time)
            #frame = cam.get_frame(exp_time=1).reshape(cam.sensor_size[::-1])
            # Plot the crosshairs 
            # plt.axhline(math.floor(cam.sensor_size[1]/2))
            # plt.axvline(math.floor(cam.sensor_size[0]/2))
            plt.imshow(frame, cmap="gray")
            plt.pause(.1)
            # print ("Saving Frame")
            # plt.savefig('img_'+str(count)+'.png')
            plt.cla()
            t4 = time.time()
            print('time to get: '+ str(t2-t1))
            print('time to imshow: '+ str(t3-t2))
            print('time to save: '+ str(t4-t3)+'\n\n')
            
            count = count +1

    except KeyboardInterrupt:
        cam.close()
        pvc.uninit_pvcam()


# This method of displaying the live image is prone to crashing 
def opencv():
    pvc.init_pvcam()
    cam = next(Camera.detect_camera())
    cam.open()
    cam.clear_mode = "Never"
    cam.exp_mode = "Ext Trig Trig First"
    cam.readout_port = 0
    cam.speed_table_index = 0
    cam.gain = 1

    cam.start_live(exp_time=1)


    cnt = 0
    tot = 0
    t1 = time.time()
    start = time.time()
    width = 800
    height = int(cam.sensor_size[1] * width / cam.sensor_size[0])
    dim = (width, height)
    fps = 0

    # frame = cam.get_frame(exp_time=1).reshape(cam.sensor_size[::-1])    
    # pl.imshow(frame, cmap="gray")
    # pl.pause(5)
    # pl.draw()

    # while True:
    #     time.sleep(2)
    #     frame = cam.get_live_frame().reshape(cam.sensor_size[::-1])
    #     #frame = cam.get_frame(exp_time=1).reshape(cam.sensor_size[::-1])
    #     #cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #     frame = cv2.resize(frame,dim, interpolation = cv2.INTER_AREA)
    #     #cv2.line(frame, (int(width/2), 0), (int(width/2), height), (255,255,255), 1)
    #     #cv2.line(frame, (0, int(height/2)), (width, int(height/2)), (255,255,255), 1)
        


    #     # low = np.amin(frame)
    #     # high = np.amax(frame)
    #     # average = np.average(frame)

    #     # if cnt == 10:
    #     #         t1 = time.time() - t1
    #     #         fps = 10/t1
    #     #         t1 = time.time()
    #     #         cnt = 0
    #     # if cv2.waitKey(10) == 27:
    #     #     break
    #     # print('Min:{}\tMax:{}\tAverage:{:.0f}\tFrame Rate: {:.1f}\n'.format(low, high, average, fps))
    #     # cnt += 1
    #     # tot += 1
    

    try:
        print ("Camera started")
        while True:
            frame = cam.get_live_frame().reshape(cam.sensor_size[::-1])
            frame = cv2.resize(frame,dim, interpolation = cv2.INTER_AREA)
            cv2.imshow('Live Mode', frame)
    except KeyboardInterrupt:
        cam.close()
        pvc.uninit_pvcam()

    # print('Total frames: {}\nAverage fps: {}\n'.format(tot, (tot/(time.time()-start))))

def main():
    py_lab()
    #opencv()


if __name__=="__main__":
    main()