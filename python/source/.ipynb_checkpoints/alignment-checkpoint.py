import os
import sys
import random
import math
import numpy as np
import skimage.io
import matplotlib
import matplotlib.pyplot as plt
import time
from numba import autojit

sys.path.append('./maskrcnn')
sys.path.append('./dataset')

import maskrcnn.utils as utils
import model as modellib
import visualize
import config

import mark_dataset
import sc_utils
import position as pos

ROOT_DIR = os.path.abspath(".")
MODEL_DIR = os.path.join(ROOT_DIR, "logs")
model_path = os.path.join(ROOT_DIR, "adjusted_frame_alignment_20.h5")
classnames = ['BG', 'mark']

def get_inference_model():
    ''' Loads weights and returns an inference model '''
    inference_config = mark_dataset.InferenceConfig()
    model = modellib.MaskRCNN(mode="inference", 
                              config=inference_config,
                              model_dir=MODEL_DIR)
    print("Loading weights from ", model_path)
    model.load_weights(model_path, by_name=True)
    return model

@autojit
def convert_to_mrcnn_format(image):
    ''' Converts the output from the PVCAM frame 
    into the format that the mrcnn model was trained on

    args:
        image: frame output from PVCAM
    returns:
        image in mrcnn fromat
    '''
    new_im = np.zeros((image.shape[0], image.shape[1], 3))
    for ix, iy in np.ndindex(image.shape):
        val = np.ceil(image[ix,iy] / 255) * 16
        new_im[ix,iy] = [val,val,val]
    new_im = new_im.astype('uint8')
    return new_im

def get_mark_center(rois):
    centroids = np.stack([
        rois[1] + ((rois[3] - rois[1]) / 2.0),
        rois[0] + ((rois[2] - rois[0]) / 2.0),
    ], -1)
    return centroids

def get_frame():
    cam = sc_utils.start_cam()
    frame = cam.get_frame(exp_time=1)
    sc_utils.close_cam(cam)
    print(frame.shape)
    return frame

def find_alignment_mark(model):
    orig_frame = get_frame()
    frame = convert_to_mrcnn_format(orig_frame)
    
    results = model.detect([frame], verbose=1)
    r = results[0]
    if len(r['rois']) > 0:
        centroids = get_mark_center(r['rois'][0])
        return centroids, orig_frame, frame, r
    raise NoMarkError("No Alignment Mark in Frame")

def move_to_center(mmc, center):
    currx = mmc.getXPosition()
    curry = mmc.getYPosition()

    x = center[0]
    y = center[1]
    
    x_change = (x-1344)*0.45
    y_change = (y-1100)*0.45
    
    new_x = currx-x_change
    new_y = curry-y_change
    
    pos.set_pos(mmc, x=new_x, y=new_y)

class Error(Exception):
    """Base class for exceptions in alignment."""
    pass

class NoMarkError(Error):
    """Exception raised for errors in the alignment.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message