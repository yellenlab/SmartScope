'''
TODO: get_focus
'''
 
#import MMCorePy
import position as pos
import chip
from pyvcam import pvc
from pyvcam.camera import Camera
from matplotlib import pyplot as plt
import time
import os
import numpy as np
import scipy.interpolate
import scipy.misc
import tifffile as tif

import sys
sys.path.insert(0, '../miq_p3')
import miq
 
class Goto:
    def __init__(self, mmc, pl, save_dir):
        self.mmc = mmc
        self.pl = pl
        self.save_dir = save_dir
        #self.get_curr_position()
 
    def get_curr_position(self):
        self.curr_x = self.mmc.getXPoistion()
        self.curr_y = self.mmc.getYPoistion()
        self.curr_z = self.mmc.getPoistion()
        return self.curr_x, self.curr_y, self.curr_z
 
    def image_pos_list(self):
        ''' Images the position list that the class was initialized with
        '''
        dir_name = self.save_dir+'/'+time.strftime("%Y-%m-%d_%H:%M")
        os.makedirs(dir_name)
        os.chdir(dir_name)
 
        # Start Camera 
        pvc.init_pvcam()
        cam = next(Camera.detect_camera())
        cam.open()
        cam.clear_mode = 'Never'
        cam.exp_mode = "Ext Trig Trig First"
        cam.readout_port = 0
        cam.speed_table_index = 0
        cam.gain = 1
        # cam.start_live(exp_time=1)
        
 
        print("Length: ", len(self.pl.positions))
 
        for posit in self.pl.positions:
            print ('Going to: ', posit.get(index=0).x, ',', posit.get(index=0).y, ',', posit.get(index=1).z)
            self.mmc.setXYPosition(-posit.get(index=0).x, -posit.get(index=0).y)
            self.mmc.setPosition(posit.get(index=1).z)
            self.mmc.waitForSystem()
 
            # Snap and save pvcam image
            # frame = cam.get_live_frame().reshape(cam.sensor_size[::-1])
            frame = cam.get_frame(exp_time=1).reshape(cam.sensor_size[::-1])
            plt.imshow(frame, cmap="gray")
            plt.savefig('img_'+str(posit.get(index=0).x)+'_'+str(posit.get(index=0).y)+'.png', bbox_inches='tight', pad_inches=0)
            plt.cla()
            time.sleep(0.05)
 
        print ('Done')
        cam.close()
        pvc.uninit_pvcam()
 
    def image_z_stack_pos_list(self, zstep, znum=11):
        '''Images a position list at different focuses. Used to train a focus 
        classifier. 
         
        args:
        - zstep: step size between different focuses in (um)
        - znum: the number of focuses to image
        '''
        current_dir = self.save_dir+'/zstack_'+time.strftime("%Y-%m-%d_%H:%M")
        os.makedirs(current_dir)
        os.chdir(current_dir)
 
        # Start Camera
        pvc.init_pvcam()
        cam = next(Camera.detect_camera())
        cam.open()
        cam.clear_mode = 'Never'
        cam.exp_mode = "Ext Trig Trig First"
        cam.readout_port = 0
        cam.speed_table_index = 0
        cam.gain = 1
        # cam.start_live(exp_time=1)
        img_ctr = 0
         
        for i in range(znum):
            # Change the Save dir each time through 
            os.makedirs(current_dir+'/'+str(i))
            os.chdir(current_dir+'/'+str(i))
             
            for posit in self.pl.positions:
                print ('Going to: ', posit.get(index=0).x, ',', posit.get(index=0).y, ',', posit.get(index=1).z)
                self.mmc.setXYPosition(-posit.get(index=0).x, -posit.get(index=0).y)
                self.mmc.setPosition(posit.get(index=1).z + (zstep*i)) # set the z pos based on i
                self.mmc.waitForSystem()

                # Snap and save pvcam image
                # frame = cam.get_live_frame().reshape(cam.sensor_size[::-1])
                frame = cam.get_frame(exp_time=1).reshape(cam.sensor_size[::-1])
                # plt.imshow(frame, cmap="gray")
                # plt.savefig('img_focus'+str(i)+'_'+str(img_ctr)+'.tif', bbox_inches='tight', pad_inches=0)
                # plt.cla()

                ## NEED TO TEST THIS!!
                # scipy.misc.imsave('img_focus'+str(i)+'_'+str(img_ctr)+'.tif', frame)
                tif.imwrite('img_focus'+str(i)+'_'+str(img_ctr)+'.tif', frame)
                time.sleep(0.05)
                img_ctr = img_ctr +1
            img_ctr = 0
 
        print ('Done')
        cam.close()
        pvc.uninit_pvcam()
         
