
import numpy as np

from smartscope.source.miq import miq

from smartscope.source import sc_utils
from smartscope.source import position as pos
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
    # Get focus model
    focus_model = miq.get_classifier()
    pos_list = pos.PositionList()
    # make z position array
    cur_pos = pos.current(mmc)
    z = get_z_list(cur_pos.z, delta_z, total_z)
    cam = sc_utils.start_cam()
    for posit in xy_points:
        # Go to the x,y position 
        pos.set_pos(mmc, x=posit.x, y=posit.y)
        preds = []
        for curr_z in z:
            mmc.setPosition(curr_z)
            mmc.waitForSystem()
            frame = cam.get_frame(exp_time=exposure).reshape(cam.sensor_size[::-1])
            preds.append(focus_model.score(sc_utils.bytescale(frame, high=65535)))
        # find the index of the min focus prediction
        best_focus_index = np.argmin(preds)
        # append to the PositionList 
        sp = pos.StagePosition(x=posit.x, y=posit.y,
                               z=z[best_focus_index])
        pos_list.append(sp)
    
    sc_utils.close_cam(cam)
    return pos_list

def focus_from_last_point(xy_points, mmc, model_path, delta_z=10, total_z=150, next_point_range=35, exposure=1):
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
    focus_model = miq.get_classifier(model_path)
    pos_list = pos.PositionList()

    # Focus the first point 
    pos.set_pos(mmc, x=xy_points[0].x, y=xy_points[0].y)
    last_z = focus_point(mmc, focus_model, delta_z=delta_z, total_z=total_z, exposure=exposure)
    sp = pos.StagePosition(x=xy_points[0].x, y=xy_points[0].y,
                            z=last_z)
    pos_list.append(sp)

    z_range = np.arange(-next_point_range/2, next_point_range/2, delta_z)
    cam = sc_utils.start_cam()
    for i, posit in enumerate(xy_points):
        # We already did the first point
        if i == 0:
            best_focus_index = 0
            continue
        
        preds = []
        # Go to the next x,y position with the previous best focus 
        pos.set_pos(mmc, x=posit.x, y=posit.y, z=last_z)
        
        if best_focus_index > (len(z_range) / 2):
            # Reverse the order of the list
            z_range = z_range[::-1]

        # Build list from last position
        # in order that makes sense 
        z_list = [(last_z+i) for i in z_range]

        for j, curr_z in enumerate(z_list):
            pos.set_pos(mmc, z=curr_z)
            frame = sc_utils.get_live_frame(cam, exposure)
            preds.append(focus_model.score(sc_utils.bytescale(frame, high=65535)))

            if j > 1:
                if ((preds[j] > preds[j-1]) and (preds[j] > preds[j-2]) and 
                    (np.abs(preds[j] - preds[j-1]) > 2 or np.abs(preds[j] - preds[j-2]) > 2)):
                    # Focus got worse
                    break
        # find the index of the min focus prediction
        best_focus_index = np.argmin(preds)
        # append to the PositionList 
        last_z = z_list[best_focus_index]
        sp = pos.StagePosition(x=posit.x, y=posit.y,
                                z=last_z)
        pos_list.append(sp)

        if len(preds) < len(z_list):
            sc_utils.print_info ('('+ str(posit.x) + ',' +  str(posit.y) +  ') - Score: ' + str(np.min(preds)) +  ' - Good focus')
        elif preds[best_focus_index] > 5:
            sc_utils.print_info ('('+ str(posit.x) + ',' +  str(posit.y) +  ') - Score: ' + str(np.min(preds)) +  ' - BAD FOCUS')
        else:
            sc_utils.print_info ('('+ str(posit.x) + ',' +  str(posit.y) +  ') - Score: ' + str(np.min(preds)) +  ' - OK focus')
    
    sc_utils.close_cam(cam)
    return pos_list

def predict_z_height(pos_list, xy_location=None):
    '''Interpolate the z value at xy_location
 
    args:
    pos_list: a Position List containing at least 4 points
    xy_location: a tuple (x,y) containing the point in question
 
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

def focus_point(mmc, focus_model, delta_z=10, total_z=250, exposure=1):
    cur_z = pos.current(mmc).z
    if total_z == 0:
        return cur_z
    z = get_z_list(cur_z, delta_z, total_z)
    cam = sc_utils.start_cam()

    preds = []
    for curr_z in z:
        pos.set_pos(mmc, z=curr_z)
        frame = sc_utils.get_live_frame(cam, exposure)
        preds.append(focus_model.score(sc_utils.bytescale(frame, high=65535)))
    # find the index of the min focus prediction
    best_focus_index = np.argmin(preds)
    # append to the PositionList 
    last_z = z[best_focus_index]

    sc_utils.close_cam(cam)
    return last_z

