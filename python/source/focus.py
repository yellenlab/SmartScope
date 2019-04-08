'''TODO 
    - train model 

'''
import sys
sys.path.insert(0, '../miq_p3')

import goto
import miq
import MMCorePy
from pyvcam import pvc
from pyvcam.camera import Camera
import imageio
import numpy as np
from skimage import exposure
from skimage import color
from skimage import io as sk_io
import utils
import position as pos
import numpy as np
import scipy.interpolate

def get_focus(xy_points, mmc, z_step=3, pred_thresh=2.25):
    '''Finds the best focus at each interior chip location
 
    args:
    xy_points: a StagePosition[] of the points to find 
    focus. Intended to be the output from Chip().get_focus_xy_points()
    mmc: Micro-Manager instance
    z_step: step size between focus heights (decided when training focus model)
 
    returns: PositionList() of xy_points locations plus best z height
    '''
 
    focused_points = pos.PositionList()
    starting_z_value = mmc.getPosition()

    # Get focus model
    focus_model = miq.get_classifier()

    # Start Camera
    cam = utils.start_cam()
    
    # Loop through all of the focus locations
    for location in xy_points:
        # If we have more that 3 focused points, we
        # can interpolate the z height based on the
        # plane that all of the known points create
        if focused_points.getNumberOfPositions() > 4:
            predicted_z = predict_z_height(focused_points, (location.x, location.y))
            utils.set_pos(mmc, location.x, location.y, predicted_z)
        # We do not have enough points to interpolate,
        # keep the previous z height
        else:
            utils.set_pos(mmc, location.x, location.y)
         
        last_predit = -1
        direction = 1
        iters = 0
        bounce = False
        hist = []

        while True:
            # Read from camera frame
            frame = cam.get_frame(exp_time=1).reshape(cam.sensor_size[::-1])
            prediction = focus_model.score(frame)
            print (prediction)
             
            if prediction < pred_thresh or bounce == True:
                ''' Prediction is good, add to focused_points and move 
                    to next location 
                '''
                print ('Done')
                zPos = pos.StagePosition()
                zPos.stageName = 'zStage'
                zPos.numAxes = 1
                zPos.z = mmc.getPosition()
                msp = pos.MultiStagePosition()
                msp.add(location)
                msp.add(zPos)
                focused_points.addPosition(msp)
                break
            elif (not (last_predit == -1)) and prediction < last_predit:
                ''' Focus is getting better, keep going in same direction '''
                
                new_z = starting_z_value + direction*z_step
                print ('1', new_z)
                mmc.setPosition(new_z)
                mmc.waitForSystem()
                hist.append(1)
            elif (not (last_predit == -1)) and prediction > last_predit:
                ''' Focus is getting worse, move in opposite direction '''
                
                direction = -direction
                new_z = starting_z_value + direction*z_step
                print('2', new_z)
                mmc.setPosition(new_z)
                mmc.waitForSystem()
                hist.append(-1)
            else:
                ''' We do not have a previous direction - move one step in 
                    the +z direction 
                '''
                
                new_z = starting_z_value + z_step
                print('3', new_z)
                mmc.setPosition(new_z)
                mmc.waitForSystem()
                hist.append(1)

            starting_z_value = new_z
            last_predit = prediction
            iters = iters +1

            # We were moving in the right direction, but have moved too far.
            if len(hist) > 3:
                if hist[::-1][1] == hist[::-1][2] and (not hist[::-1][0] == hist[::-1][1]):
                    bounce = True
            if iters == 20:
                # Could not find the focus for some reason, ignore this point
                print ('Could not find focus')
                break
    
    utils.close_cam(cam)
    return focused_points

def predict_z_height(pos_list, xy_location=None):
    '''Interpolate the z value at xy_location
 
    args:
    pos_list: a Position List containing at least 4 points
    xy_location: a tuple (x,y) containg the point in question
 
    returns: interpolated z height (float), interpolation function
    '''
    if pos_list.getNumberOfPositions() < 4:
        raise ValueError("Position List must have at least 4 values")
 
    x_vals = []
    y_vals = []
    z_vals = []
 
    for position in pos_list.positions:
        x_vals.append(position.get(stageName='xyStage').x)
        y_vals.append(position.get(stageName='xyStage').y)
        z_vals.append(position.get(stageName='zStage').z)
     
    print ('X : ', x_vals)
    print ('Y : ', y_vals)
    print ('Z : ', z_vals)

    f = scipy.interpolate.interp2d(x_vals, y_vals, z_vals, kind='cubic')
    if xy_location is None:
        return f
    return f(xy_location[0], xy_location[1]), f
 