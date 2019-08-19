"""
SmartScope 
Chip related functions and classes.

Duke University - 2019
Licensed under the MIT License (see LICENSE for details)
Written by Caleb Sanford
"""


from smartscope.source import position as pos
from smartscope.source import focus
import math
import numpy as np

class Chip:

    def __init__(self,corner_pl, 
                        first_position,
                        chip,
                        number_of_apartments_in_frame_x, 
                        number_of_apartments_in_frame_y):
        ''' Set the Chip properties using the given infomation

        Args:
            corner_pl: Position List of three corners of the chip
        '''
        assert len(corner_pl) == 3, "corner_pl must have length 3"
        self.corner_poslist = corner_pl
        self.chip = chip
        self.number_of_apartments_in_frame_x = number_of_apartments_in_frame_x
        self.number_of_apartments_in_frame_y = number_of_apartments_in_frame_y
        # The given first position is the center of the first apartment 
        # we need to conver that to the center of the fist image 
        self.first_position = [
            ((((self.number_of_apartments_in_frame_x + .5) / 2) - .5) 
                * self.chip['street_spacing']) - first_position[0],
            -(((self.number_of_apartments_in_frame_y /2 ) - .5) 
                * self.chip['apartment_spacing']) - first_position[1]
        ]

        # get rotation and size of chip
        self.cos = ((self.corner_poslist[1].x - self.corner_poslist[0].x)
                    / (self.corner_poslist[1].dist(self.corner_poslist[0])))
        self.sin = ((self.corner_poslist[1].y - self.corner_poslist[0].y)
                    / (self.corner_poslist[1].dist(self.corner_poslist[0])))
        self.R = [[self.cos, -self.sin], 
                  [self.sin, self.cos]]
        self.total_x = np.abs(self.corner_poslist[0].x
                       - self.corner_poslist[1].x)
        self.total_y = np.abs(self.corner_poslist[0].y 
                       - self.corner_poslist[2].y)

    def get_position_list(self, focused_pl):
        ''' Calculates the position list for imaging

        args:
            focused_pl: The position list of the focused interior points.
            
        returns: PositionList()
        '''
        # get the focus model from the focused points
        focus_func = focus.predict_z_height(focused_pl)
 
        x_steps = int(np.ceil(self.chip['number_of_streets']/self.number_of_apartments_in_frame_x))
        y_steps = int(np.ceil(self.chip['number_of_apartments']/self.number_of_apartments_in_frame_y))
        x_step_size = self.number_of_apartments_in_frame_x * self.chip['street_spacing']
        y_step_size = self.number_of_apartments_in_frame_y * self.chip['apartment_spacing']

        # Get 2D rotation matix for origin point
        origin = np.matmul(np.linalg.inv(self.R), 
                            [self.corner_poslist[0].x, 
                             self.corner_poslist[0].y])

        poslist = pos.PositionList()
        x_list = range(x_steps)
        for y_ctr in range(y_steps):
            for x_ctr in x_list:
                rotation = origin + [self.first_position[0] + x_step_size*x_ctr, 
                                     self.first_position[1] - y_step_size*y_ctr]
                posit = np.matmul(self.R, rotation)
                name = ("_ST_"+ str(x_ctr*self.number_of_apartments_in_frame_x).zfill(3) + 
                        "_APT_" + str(y_ctr*self.number_of_apartments_in_frame_y).zfill(3) + "_")
                s = pos.StagePosition(x=posit[0], y=posit[1], 
                                    z=focus_func(posit[0], posit[1])[0],
                                    name=name)
                poslist.append(s)
            # Each time though reverse the order to snake through chip
            x_list = x_list[::-1]
        return poslist

    def get_focus_position_list(self, fp_x, fp_y):
        ''' Gets the xy stage positions for the 
        interior focus points 
        args:
            fp_x: number of focus points in the x direction
            fp_y: number of focus points in the y direction

        returns: PositionList()
        '''
        print ("--------------")
        print (self.first_position[0])
        print (self.first_position[1])
        
        delta_x = (self.total_x - np.abs(self.first_position[0])*2) / (fp_x-1)
        delta_y = (self.total_y - np.abs(self.first_position[1])*2) / (fp_y-1)
        origin = np.matmul(np.linalg.inv(self.R), 
                           [self.corner_poslist[0].x, 
                            self.corner_poslist[0].y])

        print (delta_x)
        print (delta_y)

        fp_positions = pos.PositionList()
        fp_x_list = range(fp_x)
        for y_ctr in range(fp_y):
            for x_ctr in fp_x_list:
                rotation = origin + [self.first_position[0] + delta_x*x_ctr, 
                                    (self.first_position[1] - delta_y*y_ctr)]
                fp = np.matmul(self.R, rotation)
                s = pos.StagePosition(x=fp[0], y=fp[1])
                fp_positions.append(s)
            fp_x_list = fp_x_list[::-1]
        return fp_positions
