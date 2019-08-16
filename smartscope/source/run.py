from smartscope.source import position as pos
import math
import numpy as np
from smartscope.source import focus
from smartscope.source import alignment
import time
import os
 
def auto_image_chip(chip,
                    mmc,
                    save_dir,
                    chip_number,
                    alignment_model_name="alignment_30.h5",
                    alignment_model_path='.',
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
    print ("Starting: Alignment, Focus, and Imaging")

    model = alignment.get_inference_model(model_dir=alignment_model_path,
                                          model_name=alignment_model_name)

    center, img, frame, r = alignment.find_alignment_mark(model, exposure)
    alignment.move_to_center(mmc, center, frame_width=frame_width,
                                        frame_height=frame_height,
                                        camera_pixel_width=camera_pixel_width,
                                        camera_pixel_height=camera_pixel_height)
    curx, cury, _ = pos.current(mmc)
    p1 = pos.StagePosition(x=curx, y=cury)
    pos.set_pos(mmc, x=(p1.x - chip.CHIP_WIDTH + 150),
                     y=p1.y)
    pos.set_pos(mmc, z=focus.focus_point(mmc, exposure=exposure))

    center, img, frame, r = alignment.find_alignment_mark(model, exposure)
    alignment.move_to_center(mmc, center, frame_width=frame_width,
                                        frame_height=frame_height,
                                        camera_pixel_width=camera_pixel_width,
                                        camera_pixel_height=camera_pixel_height)
    curx, cury, _ = pos.current(mmc)
    p2 = pos.StagePosition(x=curx, y=cury)
    pos.set_pos(mmc, x=(p2.x + 150),
                     y=(p2.y - chip.CHIP_HEIGHT))
    pos.set_pos(mmc, z=focus.focus_point(mmc, exposure=exposure))

    center, img, frame, r = alignment.find_alignment_mark(model, exposure)
    alignment.move_to_center(mmc, center, frame_width=frame_width,
                                        frame_height=frame_height,
                                        camera_pixel_width=camera_pixel_width,
                                        camera_pixel_height=camera_pixel_height)
    curx, cury, _ = pos.current(mmc)
    p3 = pos.StagePosition(x=curx, y=cury)

    align_time = time.time()
    print ('Time for alignment:', align_time-start)

    # Create a Position List of the corners and save it
    corners = pos.PositionList(positions=[p1,p2,p3])
    corners.save('_corners', save_dir + "/" + chip_number)
    # Create a chip instance
    chip.initialize(corners)
    focus_pl = chip.get_focus_position_list(number_of_focus_points_x,
                                            number_of_focus_points_y)

    focused_pl = focus.focus_from_last_point(focus_pl, mmc,
                                             delta_z=focus_delta_z,
                                             total_z=focus_total_z,
                                             next_point_range=focus_next_point_range,
                                             exposure=exposure)
    focused_pl.save('_focused', save_dir + "/" + chip_number)

    focus_time = time.time()
    print ('Time for focus:', focus_time-align_time)
    
    imaging_pl = chip.get_position_list(focused_pl)
    imaging_pl.image(mmc, save_dir, naming_scheme, save_jpg=save_jpg, rotation=image_rotation, exposure=exposure)

    end = time.time()
    print ('Time for imaging:', end-focus_time)
    print ('Total time:', end-start)


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
        pos.set_pos(mmc, x=(p1.x - chip.CHIP_WIDTH),
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
                        y=(p2.y - chip.CHIP_HEIGHT))
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


def auto_image_chip_focus_first(chip,
                    mmc,
                    save_dir,
                    chip_number,
                    alignment_model_name="alignment_30.h5",
                    alignment_model_path='.',
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
    print ("Starting: Alignment, Focus, and Imaging")

    model = alignment.get_inference_model(model_dir=alignment_model_path,
                                          model_name=alignment_model_name)
    curx, cury, _ = pos.current(mmc)
    p1 = pos.StagePosition(x=curx, y=cury)
    
    # Create a temporay chip for focusing 
    temp_corners = pos.PositionList(positions=[p1, 
                                    pos.StagePosition(x=p1.x - chip.CHIP_WIDTH, y=p1.y),
                                    pos.StagePosition(x=p1.x - chip.CHIP_WIDTH, y=p1.y - chip.CHIP_HEIGHT)])
    temp_chip = chip
    temp_chip.initialize(temp_corners)

    focus_pl = temp_chip.get_focus_position_list(number_of_focus_points_x,
                                            number_of_focus_points_y)

    focused_pl = focus.focus_from_last_point(focus_pl, mmc,
                                             delta_z=focus_delta_z,
                                             total_z=focus_total_z,
                                             next_point_range=focus_next_point_range,
                                             exposure=exposure)
    focused_pl.save('_focused', save_dir + "/" + chip_number)

    align_z1, _ = focus.predict_z_height(focused_pl, xy_location=(p1.x, p1.y))
    align_z2, _ = focus.predict_z_height(focused_pl, xy_location=(p1.x - chip.CHIP_WIDTH, p1.y))
    align_z3, _ = focus.predict_z_height(focused_pl, xy_location=(p1.x - chip.CHIP_WIDTH, p1.y - chip.CHIP_HEIGHT))
    
    # print(align_z1)

    pos.set_pos(mmc, x=p1.x, y=p1.y, z=align_z1[0])
    center, img, frame, r = alignment.find_alignment_mark(model, exposure)
    alignment.move_to_center(mmc, center, frame_width=frame_width,
                                        frame_height=frame_height,
                                        camera_pixel_width=camera_pixel_width,
                                        camera_pixel_height=camera_pixel_height)
    curx, cury, _ = pos.current(mmc)
    p1 = pos.StagePosition(x=curx, y=cury)
    pos.set_pos(mmc, x=p1.x - chip.CHIP_WIDTH, y=p1.y, z=align_z2[0])
    center, img, frame, r = alignment.find_alignment_mark(model, exposure)
    alignment.move_to_center(mmc, center, frame_width=frame_width,
                                        frame_height=frame_height,
                                        camera_pixel_width=camera_pixel_width,
                                        camera_pixel_height=camera_pixel_height)
    curx, cury, _ = pos.current(mmc)
    p2 = pos.StagePosition(x=curx, y=cury)
    pos.set_pos(mmc, x=p1.x - chip.CHIP_WIDTH, y=p1.y - chip.CHIP_HEIGHT, z=align_z3[0])
    center, img, frame, r = alignment.find_alignment_mark(model, exposure)
    alignment.move_to_center(mmc, center, frame_width=frame_width,
                                        frame_height=frame_height,
                                        camera_pixel_width=camera_pixel_width,
                                        camera_pixel_height=camera_pixel_height)
    curx, cury, _ = pos.current(mmc)
    p3 = pos.StagePosition(x=curx, y=cury)
    
    align_time = time.time()
    print ('Time for alignment:', align_time-start)

    # Create a Position List of the corners and save it
    corners = pos.PositionList(positions=[p1,p2,p3])
    corners.save('_corners', save_dir + "/" + chip_number)
    # # Create a chip instance
    chip.initialize(corners)    
    imaging_pl = chip.get_position_list(focused_pl)
    imaging_pl.image(mmc, save_dir, naming_scheme, save_jpg=save_jpg, rotation=image_rotation, exposure=exposure)

    end = time.time()
    print ('Total time:', end-start)