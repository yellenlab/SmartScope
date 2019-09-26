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

def get_inference_model(model_dir):
    ''' Loads weights and returns an inference model '''

    inference_config = mark_dataset.InferenceConfig()
    model = modellib.MaskRCNN(mode="inference", 
                              config=inference_config,
                              model_dir=os.path.join(os.path.dirname(model_dir),'logs'))
    sc_utils.print_info("Loading weights from "+ model_dir)
    model.load_weights(model_dir, by_name=True)
    return model

def get_mark_center(rois):
    centroids = np.stack([
        rois[1] + ((rois[3] - rois[1]) / 2.0),
        rois[0] + ((rois[2] - rois[0]) / 2.0),
    ], -1)
    return centroids

def find_alignment_mark(stage_controller, 
                    estimate_pos, 
                    alignment_model,
                    exposure,
                    frame_to_pixel_ratio,
                    camera_pixel_width=2688, 
                    camera_pixel_height=2200):
    # go to the estimate position
    estimate_pos.goto(stage_controller)
    orig_frame = sc_utils.get_frame(exposure)
    frame = sc_utils.convert_frame_to_mrcnn_format(orig_frame)
    
    results = alignment_model.detect([frame], verbose=1)
    r = results[0]
    if len(r['rois']) > 0:
        centroids = get_mark_center(r['rois'][0])
        return centroids, orig_frame, frame, r
    else:
        # TODO
        pass

def get_center(mmc, center, frame_to_pixel_ratio, 
                camera_pixel_width, camera_pixel_height):
    cur_position = pos.current(mmc)
    x_change = (center[0]-(float(camera_pixel_width)/2))*frame_to_pixel_ratio
    y_change = (center[1]-(float(camera_pixel_height)/2))*frame_to_pixel_ratio
    new_x = cur_position.x-x_change
    new_y = cur_position.y-y_change
    return pos.StagePosition(x=new_x, y=new_y)

def search_and_find_center(stage_controller, 
                    estimate_pos, 
                    alignment_model,
                    exposure,
                    frame_to_pixel_ratio,
                    camera_pixel_width=2688, 
                    camera_pixel_height=2200):
    center, img, frame, r = find_alignment_mark(stage_controller, alignment_model, exposure)
    pos = get_center(stage_controller, center, frame_to_pixel_ratio, camera_pixel_width, camera_pixel_height)
    pos.z = estimate_pos.z
    return pos

def extended_search(stage_controller):
    center = pos.current(stage_controller)
    keep_searching = True
    while keep_searching:
        pos.set_pos()

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