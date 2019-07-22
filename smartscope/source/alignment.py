"""
SmartScope 
Alignment related functions and classes.

Duke University - 2019
Licensed under the MIT License (see LICENSE for details)
Written by Caleb Sanford
"""

import os
import random
import math
import numpy as np
import skimage.io
import matplotlib
import matplotlib.pyplot as plt
import time

from smartscope.source.maskrcnn import utils
from smartscope.source.maskrcnn import model as modellib
from smartscope.source.maskrcnn import visualize
from smartscope.source.maskrcnn import config

from smartscope.source.dataset import mark_dataset
from smartscope.source import sc_utils
from smartscope.source import position as pos

classnames = ['BG', 'mark']

def get_inference_model(model_dir=".",
                        model_name="alignment_30.h5"):
    ''' Loads weights and returns an inference model '''

    model_path = os.path.join(model_dir, model_name)
    inference_config = mark_dataset.InferenceConfig()
    model = modellib.MaskRCNN(mode="inference", 
                              config=inference_config,
                              model_dir=model_dir+'/logs')
    print("Loading weights from ", model_path)
    model.load_weights(model_path, by_name=True)
    return model

def get_mark_center(rois):
    centroids = np.stack([
        rois[1] + ((rois[3] - rois[1]) / 2.0),
        rois[0] + ((rois[2] - rois[0]) / 2.0),
    ], -1)
    return centroids

def find_alignment_mark(model, exposure):
    orig_frame = sc_utils.get_frame(exposure)
    frame = sc_utils.convert_frame_to_mrcnn_format(orig_frame)
    
    results = model.detect([frame], verbose=1)
    r = results[0]
    if len(r['rois']) > 0:
        centroids = get_mark_center(r['rois'][0])
        return centroids, orig_frame, frame, r
    raise NoMarkError("No Alignment Mark in Frame")

def move_to_center(mmc, center, camera_pixel_width=2688, camera_pixel_height=2200, 
                   frame_width=1210, frame_height=990):
    currx = mmc.getXPosition()
    curry = mmc.getYPosition()

    frame_to_pixel_ratio = float(frame_width) / float(camera_pixel_width)
    x_change = (center[0]-(float(camera_pixel_width)/2))*frame_to_pixel_ratio
    y_change = (center[1]-(float(camera_pixel_height)/2))*frame_to_pixel_ratio
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