from smartscope.source import position as pos
import math
import numpy as np
from smartscope.source import focus
from smartscope.source import alignment
from smartscope.source import sc_utils
from smartscope.source import chip

import time
import os
 
def auto_image_chip(cur_chip,
                    mmc,
                    save_dir,
                    chip_number,
                    alignment_model_path,
                    focus_model_path,
                    naming_scheme,
                    focus_delta_z,
                    focus_total_z,
                    focus_next_point_range,
                    number_of_focus_points_x,
                    number_of_focus_points_y,
                    focus_exposure,
                    image_rotation,
                    frame_to_pixel_ratio,
                    camera_pixels,
                    exposure,
                    first_position,
                    number_of_apartments_in_frame_x,
                    number_of_apartments_in_frame_y):
    ''' Aligns, focuses, and images given chip

    args:
        chip: an instance of a Chip class (found in chip.py)
        mmc: Micro-Manager instance (can get from sc_utils.get_stage_controller())
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
    sc_utils.print_info ("Starting: Alignment, Focus, and Imaging")

    model = alignment.get_inference_model(alignment_model_path)
    p1 = pos.current(mmc)
    p2 = pos.StagePosition(x=p1.x + cur_chip['chip_width'], y=p1.y)
    p3 = pos.StagePosition(x=p1.x + cur_chip['chip_width'], y=p1.y - cur_chip['chip_height'])
    
    # Create a temporay chip for focusing 
    temp_corners = pos.PositionList(positions=[p1, p2, p3])
    print ('Corners: ', str(temp_corners))
    temp_chip = chip.Chip(temp_corners, first_position, cur_chip, number_of_apartments_in_frame_x, number_of_apartments_in_frame_y)

    focus_pl = temp_chip.get_focus_position_list(number_of_focus_points_x,
                                            number_of_focus_points_y)
    print ('Focus PL: ', str(focus_pl))
    # return
    focused_pl = focus.focus_from_last_point(focus_pl, mmc, focus_model_path,
                                             delta_z=focus_delta_z,
                                             total_z=focus_total_z,
                                             next_point_range=focus_next_point_range,
                                             exposure=focus_exposure)
    focused_pl.save('_focused', save_dir + "/" + chip_number)

    p1.z = focus.predict_z_height(focused_pl, xy_location=(p1.x, p1.y))[0][0]
    p2.z = focus.predict_z_height(focused_pl, xy_location=(p2.x, p2.y))[0][0]
    p3.z = focus.predict_z_height(focused_pl, xy_location=(p3.x, p3.y))[0][0]

    print(p1)

    p1 = alignment.search_and_find_center(mmc, p1, model, exposure, frame_to_pixel_ratio, camera_pixels[0], camera_pixels[1])
    p2 = alignment.search_and_find_center(mmc, p2, model, exposure, frame_to_pixel_ratio, camera_pixels[0], camera_pixels[1])
    p3 = alignment.search_and_find_center(mmc, p3, model, exposure, frame_to_pixel_ratio, camera_pixels[0], camera_pixels[1])
    
    align_time = time.time()
    sc_utils.print_info ('Time for alignment:'+ str(align_time-start))

    # Create a Position List of the corners and save it
    corners = pos.PositionList(positions=[p1,p2,p3])
    corners.save('_corners', save_dir + "/" + chip_number)
    # # Create a chip instance
    imaging_chip = chip.Chip(corners, first_position, cur_chip, number_of_apartments_in_frame_x, number_of_apartments_in_frame_y)
    imaging_pl = imaging_chip.get_position_list(focused_pl)
    imaging_pl.image(mmc, save_dir, naming_scheme, rotation=image_rotation, exposure=exposure)

    end = time.time()
    sc_utils.print_info ('Total time:'+ str(end-start))


def image_from_saved_positions(chip, chip_number, save_dir, mmc, 
                               realign=False, alignment_model_name="alignment_30.h5",
                               alignment_model_path='.', naming_scheme='BFF', 
                               save_jpg=False, image_rotation=0,frame_width=1210.0,
                               frame_height=990.0, camera_pixel_width=2688,
                               camera_pixel_height=2200, exposure=1):
    ''' Images a chip from previously saved positions

    args:
        chip: an instance of a Chip class (found in chip.py)
        chip_number: string to identify chip
        save_dir: directory to save images to
        mmc: Micro-Manager instance (can get from sc_utils.get_stage_controller())
        realign: If true, find the alignment marks again 
        alignment_model_name: name of the trained model for alignment
        alignment_model_path: path to the trained model for alignment
        naming_scheme: Beginning of image file names
        save_jpg: Saves images as both tiff files and jpg files if True
    '''
    if realign:
        print ('Starting: Realignment and Imaging')
        model = alignment.get_inference_model(model_dir=alignment_model_path,
                                            model_name=alignment_model_name)

        center, img, frame, r = alignment.find_alignment_mark(model, exposure)
        alignment.move_to_center(mmc, center, frame_width=frame_width,
                                                frame_height=frame_height,
                                                camera_pixel_width=camera_pixel_width,
                                                camera_pixel_height=camera_pixel_height)
        curx, cury, _ = pos.current(mmc)
        p1 = pos.StagePosition(x=curx, y=cury)
        pos.set_pos(mmc, x=(p1.x - cur_chip['chip_width']),
                        y=p1.y)
        pos.set_pos(mmc, z=focus.focus_point(mmc,exposure=exposure))

        center, img, frame, r = alignment.find_alignment_mark(model, exposure)
        alignment.move_to_center(mmc, center, frame_width=frame_width,
                                            frame_height=frame_height,
                                            camera_pixel_width=camera_pixel_width,
                                            camera_pixel_height=camera_pixel_height)
        curx, cury, _ = pos.current(mmc)
        p2 = pos.StagePosition(x=curx, y=cury)
        pos.set_pos(mmc, x=(p2.x),
                        y=(p2.y - cur_chip['chip_height']))
        pos.set_pos(mmc, z=focus.focus_point(mmc,exposure=exposure))

        center, img, frame, r = alignment.find_alignment_mark(model, exposure)
        alignment.move_to_center(mmc, center, frame_width=frame_width,
                                            frame_height=frame_height,
                                            camera_pixel_width=camera_pixel_width,
                                            camera_pixel_height=camera_pixel_height)
        curx, cury, _ = pos.current(mmc)
        p3 = pos.StagePosition(x=curx, y=cury)
        
        corners = pos.PositionList(positions=[p1,p2,p3])
        corners.save('_corners', save_dir + "/" + chip_number)

        chip.initialize(corners)
        focused_pl = pos.load('\\'+chip_number + '_focused', save_dir)
        imaging_pl = chip.get_position_list(focused_pl)
        imaging_pl.image(mmc, save_dir, naming_scheme, save_jpg=save_jpg, rotation=image_rotation, exposure=exposure)

    else:
        print ('Starting: Loading and Imaging')
        chip.initialize(pos.load('\\'+chip_number + '_corners', save_dir))
        focused_pl = pos.load('\\'+chip_number + '_focused', save_dir)
        imaging_pl = chip.get_position_list(focused_pl)
        imaging_pl.image(mmc, save_dir, naming_scheme, save_jpg=save_jpg, rotation=image_rotation, exposure=exposure)

