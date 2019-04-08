'''
TODO:
    - add check to make sure that corners_pl is in the right 
      order - or else get_focus_xy_points will not work

'''


import position as pos
import math
import numpy as np
import goto
import focus


class Chip:
    ''' Chip properties '''

    def __init__(
        self, chip_name='M Chip', corner_pl=None, apts=None, 
        streets=None, apt_spacing=None, street_spacicng=None):
        ''' Set the Chip properties using the given infomation

        Args:
            chip_name: Name of the chip, (e.g. 'M Chip')
                - Can be 'Custom', see below.
            corner_pl: Position List of three corners of the chip
            
            *** if chip_name is 'Custom', The following args are needed:
            apts: number of apartments in chip
            streets: number of streets in chip
            apt_spacing: sacing of apts 
            street_spacicng: spacing of streets
        '''

        self.chip_choices ={"G Chip": [48, 32, 230, 230], 
                            "G2 Chip": [42, 32, 230, 230], 
                            "G3 Chip": [58, 16, 230, 300], 
                            "Y2 Chip": [62, 16, 220, 390], 
                            "Y Chip 50X50": [50, 50, 160, 160], 
                            "Y Chip 100X100": [100, 100, 160, 160], 
                            "I Chip": [42, 32, 195, 195],
                            "G2_v2 Chip": [48, 32, 259.2, 237.6],
                            "T Chip v3": [47, 128, 200, 200],
                            "M Chip": [47, 128, 205.2, 194.4],
                            "G3_64": [57, 64, 226.8, 302.4]}
        self.chip_name = chip_name
        if chip_name == 'Custom':
            self.apts = apts
            self.streets = streets
            self.apt_spacing = apt_spacing
            self.street_spacicng = street_spacicng
        else:
            try:
                params = self.chip_choices.get(chip_name)
                self.apts = params[0]
                self.streets = params[1]
                self.apt_spacing = params[2]
                self.street_spacicng = params[3]
            except Exception as e:
                print("Not a valid chip name")
                print(e, '\n')

        self.x = []
        self.y = []
        self.z = []
        self.dis12 = 0
        self.dis23 = 0
        self.corner_poslist = corner_pl
        if self.corner_poslist is not None:
            self.getxyz(self.corner_poslist)

    def getxyz(self,pl):
        assert isinstance(pl, pos.PositionList), True
        assert len(pl.positions), 3

        x = []
        y = []
        z = []
        for posit in self.corner_poslist.positions:
            self.x.append(posit.get(index=0).x)
            self.y.append(posit.get(index=0).y)
            self.z.append(posit.get(index=1).z)
        # self.x, self.y, self.z = self.reorder_corners_pl(x,y,z)

        self.dis12 = math.sqrt(math.pow((self.x[1] - self.x[0]), 2) +
                          math.pow((self.y[1] - self.y[0]), 2) +
                          math.pow((self.z[1] - self.z[0]), 2))
        self.dis23 = math.sqrt(math.pow((self.x[2] - self.x[1]), 2) +
                          math.pow((self.y[2] - self.y[1]), 2) +
                          math.pow((self.z[2] - self.z[1]), 2))

    def get_periods(self):
        ''' Gets the x and y periods of a chip
        returns: PeriodX, PeriodY
        '''
        return (self.dis12/self.streets-1), (self.dis23/self.apts-2)

    def get_normals(self):
        ''' Gets the normal values for the chip 
        given associated corner positions
        returns: Nx, Ny, Nz
        '''
        return ((self.y[1]-self.y[0])*(self.z[2]-self.z[0]) - 
                    (self.y[2]-self.y[0])*(self.z[1]-self.z[0]), 
                (self.z[1]-self.z[0])*(self.x[2]-self.x[0]) - 
                    (self.z[2]-self.z[0])*(self.x[1]-self.x[0]), 
                (self.x[1]-self.x[0])*(self.y[2]-self.y[0]) - 
                    (self.x[2]-self.x[0])*(self.y[1]-self.y[0]))

    def get_cosX(self):
        return (self.x[1]-self.x[0])/self.dis12

    def get_sinX(self):
        return (self.y[1]-self.y[0])/self.dis12

    def get_rotation_matrix(self):
        return [[self.get_cosX(), -self.get_sinX()], [self.get_sinX(), self.get_cosX()]]

    def get_inverse_rotation_matrix(self):
        return np.linalg.inv(self.get_rotation_matrix())

    def reorder_corners_pl(self, x, y, z):
        ''' Re-orders the given corners position list to 
            match the coordinate layout of XY Stage:

            args:
                x: list of x values from corners_pl
                y: list of y values from corners_pl
                z: list of z values from corners_pl
            
            3   
            (x,0)                                   (0,0)
              + ------------------------------------- +
                |                                   |
                |                                   |
                |                                   |
              + |               CHIP                | +
                |                                   |
                |                                   |
                |                                   |
              + ------------------------------------- +
            (x,y)                                   (0,y)
            2                                       1
        '''
        # Placeholders for the mins 
        min_x = [x[0], 0]
        min_y = [y[0], 0]
        for i, x_ in enumerate(x):
            # Find the minimum x value 
            # (we want to call this point 1 (above))
            if x_ < min_x[0]:
                min_x = [x_, i]
        for i, y_ in enumerate(y):
            # Find the minimum y value 
            # (we want to call this point 3 (above))  
            if y_ < min_y[0]:
                min_y = [y_, i]

        # Find the index that wasn't found above 
        if min_x[1] + min_y[1] == 1:
            excluded = 2
        elif min_x[1] + min_y[1] == 2:
            excluded = 1
        else:
            excluded = 0
        
        # reorder the lists 
        reordx = np.array([x[excluded]])
        reordx = np.insert(reordx, 0, x[min_x[1]])
        reordx = np.insert(reordx, -1, x[min_y[1]])

        reordy = np.array([y[excluded]])
        reordy = np.insert(reordy, 0, y[min_x[1]])
        reordy = np.insert(reordy, -1, y[min_y[1]])

        reordz = np.array([z[excluded]])
        reordz = np.insert(reordz, 0, z[min_x[1]])
        reordz = np.insert(reordz, -1, z[min_y[1]])
        
        return reordx, reordy, reordz
    
    def get_xy_distances(self):
        ''' Find the height and width from the alignment marks '''
        total_x = math.sqrt(math.pow(self.corner_poslist.positions[1].get(index=0).x -
                   self.corner_poslist.positions[0].get(index=0).x, 2) + 
                   math.pow(self.corner_poslist.positions[1].get(index=0).y -
                   self.corner_poslist.positions[0].get(index=0).y, 2 ))
        total_y = math.sqrt(math.pow(self.corner_poslist.positions[2].get(index=0).y -
                   self.corner_poslist.positions[1].get(index=0).y, 2 ) + 
                   math.pow(self.corner_poslist.positions[2].get(index=0).x -
                   self.corner_poslist.positions[1].get(index=0).x, 2))
        return total_x, total_y

    def get_pos_list(self, focus_pl):
        ''' Calculates the position list for imaging the particular chip

        args:
            focus_pl: The position list of the focused interior points.

        returns: PositionList()
        '''
        focus_func = focus.predict_z_height(focus_pl)

        delta_x = 1210.0 # PVCAM frame width
        delta_y = 990.0 # PVCAM frame height

        total_x, total_y = self.get_xy_distances()
        print('Total X: ', total_x)
        print('Total Y: ', total_y)
        
        
        x_steps = math.ceil(total_x/delta_x)
        y_steps = math.ceil(total_y/delta_y)
        
        # Get 2D rotation matix for chip
        R = self.get_rotation_matrix()
        print(R)

        # x,y = bottom right alignment mark
        x_un_rotated = self.corner_poslist.positions[0].get(index=0).x
        y_un_rotated = self.corner_poslist.positions[0].get(index=0).y
        xy_vect_un_rotated = [x_un_rotated, y_un_rotated]

        xy_vect_rotated = np.matmul(R, xy_vect_un_rotated)
        x_init = xy_vect_rotated[0]
        y_init = xy_vect_rotated[1]

        poslist = pos.PositionList()

        for j in range(y_steps):
            for i in range(x_steps):
                new_x = x_un_rotated - delta_x*i
                new_y = y_un_rotated - delta_y*j
                # print ('i,j = ',i,',',j)
                print('NEW = ',new_x, ',', new_y)
                print('Old = ',x_un_rotated, ',', y_un_rotated)

                new_xy_vect_un_rotated = [new_x, new_y]
                new_xy_vect = np.matmul(R, new_xy_vect_un_rotated)
                new_x_rotated = new_xy_vect[0]
                new_y_rotated = new_xy_vect[1]

                s = pos.StagePosition()
                s.stageName = 'xyStage'
                s.numAxes = 2
                s.x = new_x_rotated
                s.y = new_y_rotated
                print(s.x, ',', s.y)
                
                z = pos.StagePosition()
                z.stageName = 'zStage'
                z.numAxes = 1
                z.z = focus_func(-s.x, -s.y)[0]
                print(z.z)

                msp = pos.MultiStagePosition()
                msp.defaultXYStage = 'xyStage'
                msp.defaultZStage = 'zStage'
                msp.add(s)
                msp.add(z)

                poslist.addPosition(pos=msp)
        return poslist


    def get_focus_xy_points(self, fp_x, fp_y):
        ''' Gets the xy stage positions for the 
        interior focus points 

        param fp_x: number of focus points in the x direction
        param fp_y: number of focus points in the y direction

        returns: StagePosition[]
        
        '''
        focus_points = []
        delta_x = ((self.x[1]-self.x[0]) - (4*((self.x[1]-self.x[0])/(fp_x*3))))/(fp_x-1)
        delta_y = ((self.y[2]-self.y[1]) - (4*((self.y[2]-self.y[1])/(fp_y*3))))/(fp_y-1)

        # Get 2D rotation matix for chip
        R = self.get_rotation_matrix()

        # x,y = R(theta)*(x,y)
        x_un_rotated = (2*((self.x[1]-self.x[0])/(fp_x*3)))
        y_un_rotated = (2*((self.y[2]-self.y[1])/(fp_y*3)))
        xy_vect_un_rotated = [x_un_rotated, y_un_rotated]

        xy_vect_rotated = np.matmul(R, xy_vect_un_rotated)
        x_init = xy_vect_rotated[0]
        y_init = xy_vect_rotated[1]

        print ('DeltaX = ', delta_x)
        print ('DeltaY = ', delta_y)

        for j in range(fp_y):
            for i in range(fp_x):
                new_x = x_un_rotated + delta_x*i
                new_y = y_un_rotated - delta_y*j
                print ('i,j = ',i,',',j)
                print('NEW = ',new_x, ',', new_y)

                new_xy_vect_un_rotated = [new_x, new_y]
                new_xy_vect = np.matmul(R, new_xy_vect_un_rotated)
                new_x_rotated = new_xy_vect[0]
                new_y_rotated = new_xy_vect[1]

                s = pos.StagePosition()
                s.stageName = 'xyStage'
                s.numAxes = 2
                s.x = new_x_rotated - 3000.0
                s.y = new_y_rotated - 2000.0
                print(s.x, ',', s.y)
                focus_points.append(s)
        return focus_points

    def get_focus_z_points(self, fp_z, delta_z):
        ''' Gets the z stage positions for the 
        interior focus points 

        param fp_z: number of focus points in the z direction
        param delta_z: vertical distance between z positions 

        returns: StagePosition[]
        '''
        focus_points = []
        for j in [1,-1]:
            for i in range(math.ceil(fp_z/2)):
                if i == 0 and len(focus_points) == 0:
                    continue
                new_z = self.z[0] + j*i*delta_z
                s = pos.StagePosition()
                s.stageName = 'zStage'
                s.numAxes = 1
                s.z = new_z
                focus_points.append(s)
        return focus_points

    def get_focus_position_list(self, fp_x, fp_y, fp_z, delta_z):
        ''' Gets the position list for focusing 
        interior chip lcoations 

        param fp_x: number of focus points in the x direction
        param fp_y: number of focus points in the y direction
        param fp_z: number of focus points in the z direction
        param delta_z: vertical distance between z positions 

        returns: PositionList
        '''
        xy_points = self.get_focus_xy_points(fp_x, fp_y)
        z_points = self.get_focus_z_points(fp_z, delta_z)

        pl = pos.PositionList()
        for i in range(len(xy_points)):
            for j in range(len(z_points)):
                msp = pos.MultiStagePosition()
                msp.defaultXYStage = 'xyStage'
                msp.defaultZStage = 'zStage'
                msp.add(xy_points[i])
                msp.add(z_points[j])
                msp.properties['xy'] = i
                msp.properties['fp_z'] = len(z_points)
                pl.addPosition(msp)
        return pl

