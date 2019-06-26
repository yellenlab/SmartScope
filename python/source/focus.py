
import sys
sys.path.insert(0, 'miq')

import miq
import numpy as np
import sc_utils as utils
import position as pos
import scipy.interpolate
import time

def get_z_list(center, delta_z, total_z):
    ''' Gets an evenly spaced list

    args:
        center: center value of list
        delta_z: step size between points
        total_z: total distance spanned
    returns:
        list 
    '''
    start_pos = center + total_z/2
    end_pos = center - total_z/2
    num_steps = (start_pos-end_pos) / delta_z
    return np.linspace(start_pos, end_pos, num_steps)

def focus_from_last_point_bf(xy_points, mmc, delta_z=5, total_z=150, next_point_range=35, exposure=1):
    ''' Gets a focused position list using a brute force method to find the 
    first focus point, then after that, used the last focused point as the 
    center of the new, shorter focus range.

    args: 
        xy_points: a PositionList() of the locations to 
            focus at
        mmc: Micromanger instance
        delta_z: distacne between images (um)
        total_z: total imaging distance (all focused points on 
            chip should be in this range)
        nex_point_range: range to look (um) for point other than the 
            first point
    
    returns:
        focused PositionList()

    '''
    start_time = time.time()
    focus_model = miq.get_classifier()
    pos_list = pos.PositionList()
    cur_pos = mmc.getPosition()
    z = get_z_list(cur_pos, delta_z, total_z)
    cam = utils.start_cam()
    pos.set_pos(mmc, x=xy_points[0].x, y=xy_points[0].y)
    preds = []
    for curr_z in z:
        pos.set_pos(mmc, z=curr_z)
        frame = cam.get_frame(exp_time=exposure).reshape(cam.sensor_size[::-1])
        preds.append(focus_model.score(frame))
    # find the index of the min focus prediction
    best_focus_index = np.argmin(preds)
    # append to the PositionList 
    last_z = z[best_focus_index]
    sp = pos.StagePosition(x=xy_points[0].x, y=xy_points[0].y,
                            z=last_z)
    pos_list.append(sp)

    z_range = range(-next_point_range, next_point_range, delta_z)

    for i, posit in enumerate(xy_points):
        # We already did the first point
        if i == 0:
            best_focus_index = 0
            continue
        
        preds = []
        # Go to the next x,y position with the previous best focus 
        pos.set_pos(mmc, x=posit.x, y=posit.y, z=last_z)
        # frame = cam.get_frame(exp_time=1).reshape(cam.sensor_size[::-1])
        # first_score = focus_model.score(frame)
        
        if best_focus_index > (len(z_range) / 2):
            # Reverse the order of the list
            z_range = z_range[::-1]

        # Build list from last position
        # in order that makes sense 
        z_list = [(last_z+i) for i in z_range]

        for j, curr_z in enumerate(z_list):
            pos.set_pos(mmc, z=curr_z)
            frame = cam.get_frame(exp_time=exposure).reshape(cam.sensor_size[::-1])
            preds.append(focus_model.score(frame))
        
        # find the index of the min focus prediction
        best_focus_index = np.argmin(preds)
        # append to the PositionList 
        last_z = z_list[best_focus_index]
        sp = pos.StagePosition(x=posit.x, y=posit.y,
                                z=last_z)
        pos_list.append(sp)
    
    utils.close_cam(cam)
    total_time = time.time() - start_time
    # print ('Completed focus in', total_time, 'seconds')
    return pos_list

def focus_from_image_stack(xy_points, mmc, delta_z=5, total_z=150, exposure=1):
    ''' Brute force focus algorthim 
    
    args: 
        xy_points: a PositionList() of the locations to 
            focus at
        mmc: Micromanger instance
        delta_z: distacne between images (um)
        total_z: total imaging distance (all focused points on 
            chip should be in this range)
    
    returns:
        focused PositionList()
    '''
    start_time = time.time()
    # Get focus model
    focus_model = miq.get_classifier()
    pos_list = pos.PositionList()
    # make z position array
    cur_pos = mmc.getPosition()
    z = get_z_list(cur_pos, delta_z, total_z)
    cam = utils.start_cam()
    for posit in xy_points:
        # Go to the x,y position 
        pos.set_pos(mmc, x=posit.x, y=posit.y)
        preds = []
        for curr_z in z:
            mmc.setPosition(curr_z)
            mmc.waitForSystem()
            frame = cam.get_frame(exp_time=exposure).reshape(cam.sensor_size[::-1])
            preds.append(focus_model.score(frame))
        # find the index of the min focus prediction
        best_focus_index = np.argmin(preds)
        # append to the PositionList 
        sp = pos.StagePosition(x=posit.x, y=posit.y,
                               z=z[best_focus_index])
        pos_list.append(sp)
    
    utils.close_cam(cam)
    total_time = time.time() - start_time
    print ('Completed focus in', total_time, 'seconds')
    return pos_list

def focus_from_last_point(xy_points, mmc, delta_z=10, total_z=150, next_point_range=35, exposure=1):
    ''' Gets a focused position list using a brute force method to find the 
    first focus point, then after that, used the last focused point as the 
    center of the new, shorter focus range. 

    args: 
        xy_points: a PositionList() of the locations to 
            focus at
        mmc: Micromanger instance
        delta_z: distacne between images (um)
        total_z: total imaging distance (all focused points on 
            chip should be in this range)
        nex_point_range: range to look (um) for point other than the 
            first point
    
    returns:
        focused PositionList()

    '''
    start_time = time.time()
    focus_model = miq.get_classifier()
    pos_list = pos.PositionList()
    cur_pos = mmc.getPosition()
    z = get_z_list(cur_pos, delta_z, total_z)
    cam = utils.start_cam()
    pos.set_pos(mmc, x=xy_points[0].x, y=xy_points[0].y)
    preds = []
    for curr_z in z:
        pos.set_pos(mmc, z=curr_z)
        frame = cam.get_frame(exp_time=exposure).reshape(cam.sensor_size[::-1])
        preds.append(focus_model.score(frame))
    # find the index of the min focus prediction
    best_focus_index = np.argmin(preds)
    
    # append to the PositionList 
    last_z = z[best_focus_index]
    sp = pos.StagePosition(x=xy_points[0].x, y=xy_points[0].y,
                            z=last_z)
    pos_list.append(sp)

    z_range = range(-next_point_range, next_point_range, delta_z)

    for i, posit in enumerate(xy_points):
        # We already did the first point
        if i == 0:
            best_focus_index = 0
            continue
        
        preds = []
        # Go to the next x,y position with the previous best focus 
        pos.set_pos(mmc, x=posit.x, y=posit.y, z=last_z)
        # frame = cam.get_frame(exp_time=1).reshape(cam.sensor_size[::-1])
        # first_score = focus_model.score(frame)
        
        if best_focus_index > (len(z_range) / 2):
            # Reverse the order of the list
            z_range = z_range[::-1]

        # Build list from last position
        # in order that makes sense 
        z_list = [(last_z+i) for i in z_range]

        for j, curr_z in enumerate(z_list):
            pos.set_pos(mmc, z=curr_z)
            frame = cam.get_frame(exp_time=exposure).reshape(cam.sensor_size[::-1])
            preds.append(focus_model.score(frame))

            if j > 1:
                if (preds[j] > preds[j-1]) and (preds[j] > preds[j-2]):
                    # Focus got worse
                    break
        # find the index of the min focus prediction
        best_focus_index = np.argmin(preds)
        # append to the PositionList 
        last_z = z_list[best_focus_index]
        sp = pos.StagePosition(x=posit.x, y=posit.y,
                                z=last_z)
        pos_list.append(sp)
    
    utils.close_cam(cam)
    total_time = time.time() - start_time
    # print ('Completed focus in', total_time, 'seconds')
    return pos_list



def predict_z_height(pos_list, xy_location=None):
    '''Interpolate the z value at xy_location
 
    args:
    pos_list: a Position List containing at least 4 points
    xy_location: a tuple (x,y) containg the point in question
 
    returns: interpolated z height (float), interpolation function
    '''
    if len(pos_list) < 4:
        raise ValueError("Position List must have at least 4 values")
 
    f = scipy.interpolate.interp2d(
            [p.x for p in pos_list], 
            [p.y for p in pos_list], 
            [p.z for p in pos_list], 
            kind='cubic')
    
    if xy_location is None:
        return f
    return f(xy_location[0], xy_location[1]), f

def focus_point(mmc, delta_z=10, total_z=250, exposure=1):
    # Get focus model
    focus_model = miq.get_classifier()
    
    # make z position array
    cur_pos = mmc.getPosition()
    start_pos = cur_pos + total_z/2
    end_pos = cur_pos - total_z/2
    num_steps = (start_pos-end_pos) / delta_z
    z = np.linspace(start_pos, end_pos, num_steps)

    cam = utils.start_cam()

    preds = []
    for curr_z in z:
        pos.set_pos(mmc, z=curr_z)
        frame = cam.get_frame(exp_time=exposure).reshape(cam.sensor_size[::-1])
        # frame = (frame/4).astype('uint8')
        preds.append(focus_model.score(frame))
        print (preds)
    # find the index of the min focus prediction
    best_focus_index = np.argmin(preds)
    # best_focus_index = np.argmax(preds)
    print('Best index:', best_focus_index)
    # append to the PositionList 
    last_z = z[best_focus_index]

    print('Best index:', last_z)

    utils.close_cam(cam)
    return last_z