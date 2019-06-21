import position as pos
import math
import numpy as np
import focus
from const import *
import alignment
import time
import os
 
def auto_image_chip(chip,
                    mmc,
                    save_dir,
                    chip_number,
                    alignemnt_model_name="alignment_30.h5",
                    alignemnt_model_path='.',
                    naming_scheme='BFF',
                    focus_delta_z=10,
                    focus_total_z=150,
                    focus_next_point_range=35,
                    number_of_focus_points_x=5,
                    number_of_focus_points_y=4,
                    save_jpg=False,
                    image_rotation=0,
                    frame_width=1210.0,
                    frame_height=990.0,
                    camera_pixel_width=2688,
                    camera_pixel_height=2200,
                    exposure=1):
    ''' Aligns, focuses, and images given chip

    args:
        chip: an instance of a Chip class (found in chip.py)
        mmc: Mico-Manager instance (can get from sc_utils.get_mmc())
        save_dir: directory to save images to 
        chip_number: string to identify chip
        alignment_model_name: name of the trained model for alignment
        alignment_model_path: path to the trained model for alignment
        naming_scheme: Beginning of image file names
        focus_delta_z: amount to change in the z direction between getting 
                       focus prediction
        focus_total_z: total z in each direction to look for an individual 
                       focus point or the first focus point in a set
        focus_next_point_range: total z in each direction to look for each 
                       focus point that directly follows a nearby point that 
                       we have already focused (this will need to be increased
                       for chips that are not relatively flat)
        number_of_focus_points_x: Number of positions to focus at in the x 
                       direction (must be greater than 3 for interpolation to 
                       work propertly)
        number_of_focus_points_y: Number of positions to focus at in the y 
                       direction (must be greater than 3 for interpolation to 
                       work propertly)
        save_jpg: Saves images as both tiff files and jpg files if True
    '''
    start = time.time()
    print ("Starting: Alignment, Focus, and Imaging")

    model = alignment.get_inference_model(model_dir=alignemnt_model_path,
                                          model_name=alignemnt_model_name)

    center, img, frame, r = alignment.find_alignment_mark(model)
    alignment.move_to_center(mmc, center)
    p1 = pos.StagePosition(x=mmc.getXPosition(),
                           y=mmc.getYPosition())
    pos.set_pos(mmc, x=(p1.x - chip.CHIP_WIDTH),
                     y=p1.y)
    pos.set_pos(mmc, z=focus.focus_point(mmc))

    center, img, frame, r = alignment.find_alignment_mark(model)
    alignment.move_to_center(mmc, center)
    p2 = pos.StagePosition(x=mmc.getXPosition(),
                           y=mmc.getYPosition())
    pos.set_pos(mmc, x=(p2.x),
                     y=(p2.y - chip.CHIP_HEIGHT))
    pos.set_pos(mmc, z=focus.focus_point(mmc))

    center, img, frame, r = alignment.find_alignment_mark(model)
    alignment.move_to_center(mmc, center)
    p3 = pos.StagePosition(x=mmc.getXPosition(),
                           y=mmc.getYPosition())

    align_time = time.time()
    print ('Time for alignment:', align_time-start)

    # Create a Position List of the corners and save it
    corners = pos.PositionList(positions=[p1,p2,p3])
    corners.save('_corners', save_dir + "/" + chip_number)
    # Create a chip instance
    chip.initalize(corners)
    focus_pl = chip.get_focus_position_list(number_of_focus_points_x,
                                            number_of_focus_points_y)

    focused_pl = focus.focus_from_last_point(focus_pl, mmc,
                                             delta_z=focus_delta_z,
                                             total_z=focus_total_z,
                                             next_point_range=focus_next_point_range)
    focused_pl.save('_focused', save_dir + "/" + chip_number)

    focus_time = time.time()
    print ('Time for focus:', focus_time-align_time)
    
    imaging_pl = chip.get_position_list(focused_pl)
    imaging_pl.image(mmc, save_dir, naming_scheme, save_jpg=save_jpg, rotation=image_rotation)

    end = time.time()
    print ('Time for imaging:', end-focus_time)
    print ('Total time:', end-start)


def image_from_saved_positions(chip, chip_number, save_dir, mmc, 
                               realign=False, alignemnt_model_name="alignment_30.h5",
                               alignemnt_model_path='.', naming_scheme='BFF', 
                               save_jpg=False, image_rotation=0,frame_width=1210.0,
                               frame_height=990.0, camera_pixel_width=2688,
                               camera_pixel_height=2200, exposure=1):
    ''' Images a chip from previously saved positions

    args:
        chip: an instance of a Chip class (found in chip.py)
        chip_number: string to identify chip
        save_dir: directory to save images to
        mmc: Mico-Manager instance (can get from sc_utils.get_mmc())
        realign: If true, find the alignment marks again 
        alignment_model_name: name of the trained model for alignment
        alignment_model_path: path to the trained model for alignment
        naming_scheme: Beginning of image file names
        save_jpg: Saves images as both tiff files and jpg files if True
    '''
    if realign:
        print ('Starting: Realignment and Imaging')
        model = alignment.get_inference_model(model_dir=alignemnt_model_path,
                                              model_name=alignemnt_model_name)

        center, img, frame, r = alignment.find_alignment_mark(model)
        alignment.move_to_center(mmc, center)
        p1 = pos.StagePosition(x=mmc.getXPosition(),
                               y=mmc.getYPosition())
        pos.set_pos(mmc, x=(p1.x - chip.CHIP_WIDTH),
                         y=p1.y)
        pos.set_pos(mmc, z=focus.focus_point(mmc))

        center, img, frame, r = alignment.find_alignment_mark(model)
        alignment.move_to_center(mmc, center)
        p2 = pos.StagePosition(x=mmc.getXPosition(),
                               y=mmc.getYPosition())
        pos.set_pos(mmc, x=(p2.x),
                         y=(p2.y - chip.CHIP_HEIGHT))
        pos.set_pos(mmc, z=focus.focus_point(mmc))

        center, img, frame, r = alignment.find_alignment_mark(model)
        alignment.move_to_center(mmc, center)
        p3 = pos.StagePosition(x=mmc.getXPosition(),
                               y=mmc.getYPosition())
        
        corners = pos.PositionList(positions=[p1,p2,p3])
        corners.save('_corners', save_dir + "/" + chip_number)

        chip.initalize(corners)
        focused_pl = pos.load('\\'+chip_number + '_focused', save_dir)
        imaging_pl = chip.get_position_list(focused_pl)
        imaging_pl.image(mmc, save_dir, naming_scheme, save_jpg=save_jpg)

    else:
        print ('Starting: Loading and Imaging')
        chip.initalize(pos.load('\\'+chip_number + '_corners', save_dir))
        focused_pl = pos.load('\\'+chip_number + '_focused', save_dir)
        imaging_pl = chip.get_position_list(focused_pl)
        imaging_pl.image(mmc, save_dir, naming_scheme, save_jpg=save_jpg, rotation=image_rotation)