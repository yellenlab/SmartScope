
import position as pos
import math
import numpy as np
import focus


class Chip:
    ''' Chip properties '''

    def __init__(self, corner_pl):
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

    def get_position_list(self, focused_pl, cam_frame_width=1210.0, cam_frame_height=990.0):
        ''' Calculates the position list for imaging the particular chip

        args:
            focused_pl: The position list of the focused interior points.
            cam_frame_width: x distance between images (default 1210.0 for PVCAM)
            cam_frame_height: y distance between images (default 990.0 for PVCAM)
            
        returns: PositionList()
        '''
        # get the focus model from the focused points
        focus_func = focus.predict_z_height(focused_pl)

        x_steps = int(np.ceil(self.total_x/cam_frame_width))
        y_steps = int(np.ceil(self.total_y/cam_frame_height))
        
        # Get 2D rotation matix for origin point
        origin = np.matmul(np.linalg.inv(self.R), 
                            [self.corner_poslist[0].x, 
                             self.corner_poslist[0].y])

        poslist = pos.PositionList()
        x_list = range(x_steps)
        for y_ctr in range(y_steps):
            for x_ctr in x_list:
                rotation = origin + [cam_frame_width/2 + cam_frame_width*x_ctr, 
                                    (cam_frame_height/2 + cam_frame_height*y_ctr + 100)]
                posit = np.matmul(self.R, rotation)
                s = pos.StagePosition(x=posit[0], y=posit[1], 
                                    z=focus_func(posit[0], posit[1])[0])
                poslist.append(s)
            # Each time though reverse the order to snake through chip
            x_list = xlist[::-1]
        return poslist

    def get_focus_position_list(self, fp_x, fp_y):
        ''' Gets the xy stage positions for the 
        interior focus points 
        args:
            fp_x: number of focus points in the x direction
            fp_y: number of focus points in the y direction

        returns: PositionList()
        '''
        delta_x = self.total_x / fp_x
        delta_y = self.total_y / fp_y

        origin = np.matmul(np.linalg.inv(self.R), 
                           [self.corner_poslist[0].x, 
                            self.corner_poslist[0].y])

        fp_positions = pos.PositionList()
        fp_x_list = range(fp_x)
        for y_ctr in range(fp_y):
            for x_ctr in fp_x_list:
                rotation = origin + [delta_x/2 + delta_x*x_ctr, 
                                    (delta_y/2 + delta_y*y_ctr)]
                fp = np.matmul(self.R, rotation)
                s = pos.StagePosition(x=fp[0], y=fp[1])
                fp_positions.append(s)
            fp_x_list = fp_x_list[::-1]
        return fp_positions
