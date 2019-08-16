"""
SmartScope 
Common utility functions and classes.

Duke University - 2019
Licensed under the MIT License (see LICENSE for details)
Written by Caleb Sanford
"""


####################################################
# Change these lines to import different camera package
####################################################
from pyvcam import pvc
from pyvcam.camera import Camera

def start_cam():
    ''' Initializes the PVCAM

    returns: cam instance
    '''
    try:
        pvc.init_pvcam()
        cam = next(Camera.detect_camera())
        cam.open()
        cam.clear_mode = 'Never'
        cam.exp_mode = "Ext Trig Trig First"
        cam.readout_port = 0
        cam.speed_table_index = 0
        cam.gain = 1
    except:
        raise RuntimeError('Could not start Camera')
    return cam

def get_frame_size(cam):
    return cam.shape

def close_cam(cam):
    ''' Closes the PVCAM instance
    args:
        - camera instance 
    '''
    try:
        cam.close()
        pvc.uninit_pvcam()
    except:
        print_error('Could not close Camera')

def get_frame(exposure):
    ''' Gets a frame from the camera '''
    cam = start_cam()
    frame = cam.get_frame(exp_time=exposure)
    close_cam(cam)
    return frame

def get_live_frame(cam, exposure):
    ''' Gets a frame from the passed camera instance. This is a faster 
    way to get consecutive frames from a camera, used for focus and 
    imaging.

    args:
        - cam: camera instance 
        - exposure: exposure time

    '''
    return cam.get_frame(exp_time=exposure)
####################################################

####################################################
# To use an XYZ controller other than micro-manager,
# change the following lines to fit your stages
####################################################
import MMCorePy

def get_stage_controller(cfg="../../config/scope_stage.cfg"):
    ''' Gets an instance of the stage controller (micro-manager).
    This function can be changed to return other python controllers.
    '''
    mmc = MMCorePy.CMMCore()
    mmc.loadSystemConfiguration(cfg)
    mmc.setFocusDevice('FocusDrive')
    return mmc

def get_x_pos(stage_controller):
    return stage_controller.getXPosition()

def get_y_pos(stage_controller):
    return stage_controller.getYPosition()

def get_z_pos(stage_controller):
    return stage_controller.getPosition()

def set_xy_pos(stage_controller, x, y):
    return stage_controller.setXYPosition(x, y)

def set_z_pos(stage_controller, z):
    return stage_controller.setPosition(z)

def wait_for_system(stage_controller):
    return stage_controller.waitForSystem()
####################################################
 

####################################################
# Image manipulation 
####################################################
from numba import autojit
import numpy as np

@autojit
def convert_frame_to_mrcnn_format(frame):
    ''' Converts the output from the PVCAM frame 
    into the format that the mrcnn model was trained on

    args:
        frame: frame output from PVCAM
    returns:
        frame in mrcnn fromat
    '''
    new_im = np.zeros((frame.shape[0], frame.shape[1], 3))
    frame = bytescale(frame, high=255)
    for ix, iy in np.ndindex(frame.shape):
        val = frame[ix,iy]
        new_im[ix,iy] = [val,val,val]
    new_im = new_im.astype('uint8')
    return new_im

@autojit
def bytescale(data, current_min=0, current_max=None, high=65535, low=0):
    ''' Scales 2D pixel values from a camera to the specified high and 
        low values
    args: 
        data: frame array from camera (grayscale values)
        current_min: the min value of the raw pixel values 
        current_max: the max value of the raw pixel values. This 
                will usually be 255 (8-bit) or 16383 (14-bit)
        high: the high value to scale to (65535 for 16-bit)
        low: the low value to scale to
    
    returns:
        2D 16-bit depth array
    '''
    if current_min is None:
        current_min = data.min()
    if current_max is None:
        current_max = data.max()

    cscale = current_max - current_min
    if cscale < 0:
        raise ValueError("`current_max` should be larger than `current_min`.")
    elif cscale == 0:
        cscale = 1

    scale = float(high - low) / cscale
    bytedata = (data - current_min) * scale + low

    if high == 65535:
        return (bytedata.clip(low, high) + 0.5).astype('uint16')
    elif high == 255:
        return (bytedata.clip(low, high) + 0.5).astype('uint8')
    else:
        return (bytedata.clip(low, high) + 0.5)

####################################################
# Scope Calibration 
####################################################

def get_stage_to_pixel_ratio(stage_point_1, stage_point_2, 
                             pixel_val_1, pixel_val_2):
    ''' Calculates how many microns are in one pixel
    args:
        stage_point_1: xy StagePosition instance
        stage_point_2: xy StagePosition instance
        pixel_val_1: camera pixel value (x,y)
        pixel_val_2: camera pixel value (x,y)
    returns:
        float
    '''
    stage_distance_x = np.abs(stage_point_1.x - stage_point_2.x)
    stage_distance_y = np.abs(stage_point_1.y - stage_point_2.y)
    pixel_distance_x = np.abs(pixel_val_1[0] - pixel_val_2[0])
    pixel_distance_y = np.abs(pixel_val_1[1] - pixel_val_2[1])

    stage_pixel_ratio_x = float(stage_distance_x) / float(pixel_distance_x)
    stage_pixel_ratio_y = float(stage_distance_y) / float(pixel_distance_y)

    return (stage_pixel_ratio_x + stage_pixel_ratio_y) / 2
    
####################################################
# Printing
####################################################

def print_info(message):
    print ('[SS INFO]:'+ message)

def print_error(message):
    print('------------------------------------------------------')
    print ('[SS ERROR]:'+ message)
    print('------------------------------------------------------')