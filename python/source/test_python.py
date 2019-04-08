from pyvcam import pvc
from pyvcam.camera import Camera
from matplotlib import pyplot as plt
import MMCorePy
import _thread
import time
import os

# Define a function for the thread
def print_time( folder, cam):
        ctr = 0
        while True:
            frame = cam.get_live_frame().reshape(cam.sensor_size[::-1])
            # frame = cam.get_frame(exp_time=1).reshape(cam.sensor_size[::-1])
            plt.imshow(frame, cmap="gray")
            plt.savefig(folder+'_'+str(ctr)+'.png')
            plt.cla()
            ctr = ctr + 1
            time.sleep(2)


# Create two threads as follows
pvc.init_pvcam()
cam1 = next(Camera.detect_camera())
cam1.open()
cam1.exp_mode = "Ext Trig Trig First"
cam1.readout_port = 0
cam1.speed_table_index = 0
cam1.start_live(exp_time=1)

dir_name = './ThreadTest'
os.chdir(dir_name)

try:
   _thread.start_new_thread( print_time, ("Thread-1", cam1, ) )
   time.sleep(1)
   _thread.start_new_thread( print_time, ("Thread-2", cam1, ) )
except:
   print ("Error: unable to start thread")

while 1:
   pass
