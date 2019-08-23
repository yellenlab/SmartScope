"""
SmartScope 
Position related functions and classes.

Duke University - 2019
Licensed under the MIT License (see LICENSE for details)
Written by Caleb Sanford
"""


from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
import json
from collections import defaultdict
from collections import OrderedDict
import time
import tifffile as tif
import os
import skimage.io 
import scipy.misc
import cv2

from smartscope.source import chip
from smartscope.source import sc_utils


class PositionList:

    def __init__(self, sp=None, positions=None):
        if positions is not None:
            self.positions = positions
        else:
            self.positions = []
        if sp is not None and isinstance(sp, StagePosition):
            self.append(sp)
    
    def __len__(self):
        return len(self.positions)
    
    def __add__(self, other):
        posits = self.positions + other.positions
        return PositionList(positions=posits)
    
    def __iter__(self):
        return iter(self.positions)

    def __getitem__(self, key):
        return self.positions[key]
    
    def __setitem__(self, key, val):
        self.positions[key] = val
    
    def __delitem__(self, key):
        del self.positions[key]
    
    def __str__(self):
        string = ''
        for p in self.positions:
            string = string + str(p) + '\n'
        return string
    
    def append(self, item):
        self.positions.append(item)
    
    def insert(self, item, idx):
        self.positions.insert(idx, item)

    def visualize(self, xy=False):
        ''' Plots a 3D PositionList 
        arg:
            xy: bool - if True plot x vs y in 2D
        '''
        if xy is False:
            fig = plt.figure()
            plot = fig.add_subplot(111,projection='3d')

            xpos = [i.x for i in self.positions]
            ypos = [i.y for i in self.positions]
            zpos = [i.z for i in self.positions]

            plot.scatter(xpos,ypos,zpos)
            plot.set_xlabel('X')
            plot.set_ylabel('Y')
            plot.set_zlabel('Z')
        else:
            x = [p.x for p in self.positions]
            y = [p.y for p in self.positions]

            plt.scatter(x,y)
            plt.title('Position List')
            plt.xlabel('X')
            plt.ylabel('Y')
    
    def image(self, mmc, save_dir, naming_scheme, save_jpg=False, rotation=0, exposure=1, output_pixels=[2688,2200]):
        ''' Images the positions in the PositionList

        args: 
            mmc: Micro-manager instance
            save_dir: Directory to save tiff files 
        '''
        # Make the directory to save to and change into it
        orig_dir = os.getcwd()
        dir_name = save_dir+'\\'+naming_scheme
        os.makedirs(dir_name)
        os.chdir(dir_name)

        cam = sc_utils.start_cam()

        for ctr, pos in enumerate(self.positions):
            # set position and wait
            set_pos(mmc, pos.x, pos.y, z=pos.z)
            sc_utils.before_every_image()
            
            # Get image and save 
            frame = sc_utils.get_live_frame(cam, exposure)

            sc_utils.after_every_image()
            frame = np.flipud(frame)
            if rotation >= 90:
                frame = np.rot90(frame)
            if rotation >= 180:
                frame = np.rot90(frame)
            if rotation >= 270:
                frame = np.rot90(frame)
            
            convert_and_save(frame, save_jpg, pos, naming_scheme, output_pixels, convert_to_16bit=True)
            time.sleep(0.01)
        
        sc_utils.close_cam(cam)
        os.chdir(orig_dir)
    
    def save(self, filename, path):
        ''' Save PositionList() as a json file
        '''
        # Convert to dict form 
        data = defaultdict(dict)
        for i, val in enumerate(self.positions):
            data[i]['x'] = val.x
            data[i]['y'] = val.y
            data[i]['z'] = val.z
            data[i]['theta'] = val.theta
            data[i]['numAxes'] = val.numAxes
            
        # Write to file
        with open(path + '/' + filename + '.json', 'w') as outfile:
            json.dump(data, outfile)

def convert_and_save(frame, save_jpg, pos, naming_scheme, output_pixels, convert_to_16bit=True):
    if convert_to_16bit:
        frame = sc_utils.bytescale(frame)
    if output_pixels != [2688, 2200]:
        frame = cv2.resize(frame, tuple(output_pixels), interpolation = cv2.INTER_AREA)
    tif.imwrite(naming_scheme + pos.name + time.strftime("%Y%m%d%H%M") + '.tif', frame)
    if save_jpg:
        os.makedirs('jpg', exist_ok=True)
        scipy.misc.imsave('jpg/'+naming_scheme + pos.name + time.strftime("%Y%m%d%H%M") + '.jpg', frame)


def load(filename, path):
    ''' Load PositionList() from json file 
    
    args:
        filename: string 
        path: directory to save file 
    returns:
        PositionList() 
    '''
    with open(path + '/' + filename + '.json') as f:
        data = json.load(f,object_pairs_hook=OrderedDict)
    sp = []
    for key, val in data.items():
        sp.append(StagePosition(x=val['x'], y=val['y'],
                                    z=val['z'], theta=val['theta']))
    return PositionList(positions=sp)

def current(stage_controller, axis='xyz'):
    ''' Gets the current stage position 
    
    arg:
        stage_controller: Micromanager instance
        axis: axis to return
    returns:
        (x_pos, y_pos, z_pos)
    '''
    if axis == 'x':
         return StagePosition(x=sc_utils.get_x_pos(stage_controller))
    if axis == 'y':
         return StagePosition(y=sc_utils.get_y_pos(stage_controller))
    if axis == 'z':
         return StagePosition(z=sc_utils.get_z_pos(stage_controller))
    if axis == 'xy':
         return StagePosition(x=sc_utils.get_x_pos(stage_controller), 
                              y=sc_utils.get_y_pos(stage_controller))  
    return StagePosition(x=sc_utils.get_x_pos(stage_controller), 
                         y=sc_utils.get_y_pos(stage_controller),
                         z=sc_utils.get_z_pos(stage_controller))

def set_pos(stage_controller, x=None, y=None, z=None):
    ''' Sets a microscope position
    args:
        - mmc instance
        - x (float)
        - y (float)
        - z (float) (default is None - keeps previous focus)
    '''
    if z is not None:
        if x is None and y is None:
            sc_utils.set_z_pos(stage_controller, z)
            sc_utils.wait_for_system(stage_controller)
        else:
            sc_utils.set_xy_pos(stage_controller, x, y)
            sc_utils.set_z_pos(stage_controller, z)
            sc_utils.wait_for_system(stage_controller)
    else:
        sc_utils.set_xy_pos(stage_controller, x, y)
        sc_utils.wait_for_system(stage_controller)
    

class StagePosition:
    ''' Stores the data of one instantaneous stage position 
    args:
        x: x position (optional)
        y: y position (optional)
        z: z position (optional)
        theta: theta position (optional)
    '''
    def __init__(self, x=None, y=None, z=None, theta=None, name=None):
        self.x = x
        self.y = y
        self.z = z
        self.theta = theta
        self.numAxes = 0
        self.name = name
        for val in [x, y, z, theta]:
            if val is not None:
                self.numAxes = self.numAxes + 1
    
    def __eq__(self, other):
        ''' Allows use of == operator on two StagePositions
        '''
        return (self.x == other.x and
                self.y == other.y and
                self.z == other.z and
                self.theta == other.theta and
                self.numAxes == other.numAxes)
    
    def __str__(self):
        ''' Allows for print(StagePosition()) to see values
        '''
        if self.numAxes == 0:
            return 'No vals'
        if self.numAxes == 1:
            return "(" + str(self.x) + ")"
        elif self.numAxes == 2:
            return "(" + str(self.x) + "," + str(self.y) + ")"
        elif self.numAxes ==3:
            return ("(" + str(self.x) + "," + str(self.y) + 
                    "," + str(self.z) + ")")
        else:
            return ("(" + str(self.x) + "," + str(self.y) + 
                    "," + str(self.z) + "," + str(self.theta) + ")")
    
    def dist(self, other):
        ''' l2 distance between two stage postions. eg stage1.dist(stage2)
        args: 
            other: StagePosition()
        returns:
            distance between points 
        '''
        if self.numAxes == 0:
            raise ValueError('StagePosition does not have any values')
        if self.numAxes == 1:
            return np.sqrt(np.square(self.x - other.x))
        elif self.numAxes == 2:
            return np.sqrt(np.square(self.x - other.x) + 
                       np.square(self.y - other.y))
        elif self.numAxes ==3:
            return np.sqrt(np.square(self.x - other.x) + 
                       np.square(self.y - other.y) + 
                       np.square(self.z - other.z))
    
    def goto(self, mmc, xy_only=False):
        ''' Goes to the stage position
        args:
            mmc: Micro-Manager instance
            xy_only: ignore the z axis
        '''
        if xy_only:
            mmc.setXYPosition(self.x,self.y)
            mmc.waitForSystem()
        else:
            mmc.setXYPosition(self.x,self.y)
            mmc.setPosition(self.z)
            mmc.waitForSystem()

   
