'''
get rid of constants
allow manual declaration of apts_in_frame

'''


import position as pos
import math
import numpy as np
import focus


class Chip:
    ''' Default Chip properties '''
    NUMBER_OF_APARTMENTS = 47
    NUMBER_OF_STREETS = 128
    APARTMENT_SPACING = 205.2
    STREET_SPACING = 194.4

    # Chip Dimensions from alignment mark to alignment mark
    CHIP_WIDTH = 26000.0
    CHIP_HEIGHT = 9500.0

    # This is the first imaging position relative to the first alignment mark
    # FIRST_POSITION = (1165.4, 266.0)
    # FIRST_POSITION = (1098.2, 266.0)
    FIRST_POSITION = (1066.2, 266.0)
    # FIRST_POSITION = ((CHIP_WIDTH - (NUMBER_OF_STREETS * STREET_SPACING)
    #                   + (STREET_SPACING / 4),
    #                   (CHIP_HEIGHT - (NUMBER_OF_APARTMENTS * APARTMENT_SPACING))
    #                   + ((NUMBER_OF_APTS_IN_FRAME_Y / 2) * APARTMENT_SPACING)))



    def initialize(self, corner_pl, number_of_apartments_in_frame_x, 
                                   number_of_apartments_in_frame_y):
        ''' Set the Chip properties using the given infomation

        Args:
            corner_pl: Position List of three corners of the chip
        '''
        assert len(corner_pl) == 3, "corner_pl must have length 3"
        self.corner_poslist = corner_pl
        self.order_corners_pl()

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

    def order_corners_pl(self):
        ''' Re-orders the given corners position list to 
            match the coordinate layout of XY Stage, 
            if the corner that we don't use is given, 
            we estimate it:

            NOTE: The x coordinate value displayed on
            the ASI Stage controller is negated when
            returned from mmc.getXPosition() (I don't 
            know why this is), The layout below represents 
            the values that is returned from mmc.
            
            3   
            (0,0)                                   (x,0)
              + ------------------------------------- +
                |                                   |
                |                                   |
                |                                   |
              + |               CHIP                | +
                |                                   |
                |                                   |
                |                                   |
              + ------------------------------------- +
            (0,y)                                   (x,y)
            2                                       1
        '''
        # Find the position with the max x value, 
        # place it at the beginning of the list
        max_x = np.argmax([p.x for p in self.corner_poslist])
        temp_pos = self.corner_poslist[max_x]
        del self.corner_poslist[max_x]
        self.corner_poslist.insert(temp_pos, 0)

        # Find the position with the min y value, 
        # place it at the end
        min_y = np.argmin([p.y for p in self.corner_poslist])
        temp_pos = self.corner_poslist[min_y]
        del self.corner_poslist[min_y]
        self.corner_poslist.append(temp_pos)

    def get_position_list(self, focused_pl):
        ''' Calculates the position list for imaging

        args:
            focused_pl: The position list of the focused interior points.
            
        returns: PositionList()
        '''
        # get the focus model from the focused points
        focus_func = focus.predict_z_height(focused_pl)
 
        x_steps = int(np.ceil(self.NUMBER_OF_STREETS/self.NUMBER_OF_APTS_IN_FRAME_X))
        y_steps = int(np.ceil(self.NUMBER_OF_APARTMENTS/self.NUMBER_OF_APTS_IN_FRAME_Y))
        x_step_size = self.NUMBER_OF_APTS_IN_FRAME_X * self.STREET_SPACING
        y_step_size = self.NUMBER_OF_APTS_IN_FRAME_Y * self.APARTMENT_SPACING

        # Get 2D rotation matix for origin point
        origin = np.matmul(np.linalg.inv(self.R), 
                            [self.corner_poslist[0].x, 
                             self.corner_poslist[0].y])

        poslist = pos.PositionList()
        x_list = range(x_steps)
        for y_ctr in range(y_steps):
            for x_ctr in x_list:
                rotation = origin + [(self.CHIP_WIDTH - (self.FIRST_POSITION[0] + 
                                      self.STREET_SPACING * self.NUMBER_OF_APTS_IN_FRAME_X *
                                      (x_steps - 1)) + (self.STREET_SPACING / 4)) + 
                                      x_step_size*x_ctr, 
                                     self.FIRST_POSITION[1] + y_step_size*y_ctr]
                posit = np.matmul(self.R, rotation)
                name = ("_ST_"+ str((x_steps-1)*self.NUMBER_OF_APTS_IN_FRAME_X
                                     - x_ctr*self.NUMBER_OF_APTS_IN_FRAME_X).zfill(3) + 
                        "_APT_" + str(y_ctr*self.NUMBER_OF_APTS_IN_FRAME_Y).zfill(3) + "_")
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

        delta_x = (self.total_x - self.FIRST_POSITION[0]*2) / (fp_x-1)
        delta_y = (self.total_y - self.FIRST_POSITION[1]*2) / (fp_y-1)
        origin = np.matmul(np.linalg.inv(self.R), 
                           [self.corner_poslist[0].x, 
                            self.corner_poslist[0].y])

        fp_positions = pos.PositionList()
        fp_x_list = range(fp_x)
        for y_ctr in range(fp_y):
            for x_ctr in fp_x_list:
                rotation = origin + [self.FIRST_POSITION[0] + delta_x*x_ctr, 
                                    (self.FIRST_POSITION[1] + delta_y*y_ctr)]
                fp = np.matmul(self.R, rotation)
                s = pos.StagePosition(x=fp[0], y=fp[1])
                fp_positions.append(s)
            fp_x_list = fp_x_list[::-1]
        return fp_positions


class ML_Chip(Chip):
    ''' This class inherits from the main Chip class, it adjusts the 
    constant values for the specific chip types
    '''
    NUMBER_OF_APARTMENTS = 47
    NUMBER_OF_STREETS = 128
    APARTMENT_SPACING = 205.2
    STREET_SPACING = 194.4

    # Chip Dimensions from alignment mark to alignment mark
    CHIP_WIDTH = 26000.0
    CHIP_HEIGHT = 9500.0

    NUMBER_OF_APTS_IN_FRAME_X = 5
    NUMBER_OF_APTS_IN_FRAME_Y = 4
    # FIRST_POSITION = (1165.4, 266.0)


class KL_Chip(Chip):
    NUMBER_OF_APARTMENTS = 34
    NUMBER_OF_STREETS = 128
    APARTMENT_SPACING = 280.6
    STREET_SPACING = 194.4
    CHIP_WIDTH = 26000.0
    CHIP_HEIGHT = 9500.0

    NUMBER_OF_APTS_IN_FRAME_X = 5
    NUMBER_OF_APTS_IN_FRAME_Y = 3

    # FIRST_POSITION = (1165.4, 266.0)