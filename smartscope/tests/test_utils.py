import unittest
import sys
sys.path.append('../source')
import sc_utils
import numpy as np
import random


class TestUtils(unittest.TestCase):
    
    # Test camera 
    def test_get_frame(self):
        frame = sc_utils.get_frame(1)
        assertIsNotNone(frame)
    
    def test_get_live_frame(self):
        cam = sc_utils.start_cam()
        frame = sc_utils.get_live_frame(cam, 1)
        sc_utils.close_cam(cam)
        assertIsNotNone(frame)

    # Test stage controller 
    def test_stage_positions(self):
        sp1 = [10.0, 10.0]
        sp2 = [0.0, 0.0]

        # Get the controller instance 
        controller = sc_utils.get_stage_controller()
        
        # Set position 1
        sc_utils.set_xy_position(controller, sp1[0], sp2[1])
        sc_utils.wait_for_system(controller)

        # Get position 1
        x1 = get_x_position(controller)
        y1 = get_y_position(controller)
        assertTrue((np.abs(x1-sp1[0]) < .5))
        assertTrue((np.abs(y1-sp1[1]) < .5))
        
        # Set position 2
        sc_utils.set_xy_position(controller, sp2[0], sp2[1])
        sc_utils.wait_for_system(controller)

        # Get position 2
        x2 = get_x_position(controller)
        y2 = get_y_position(controller)
        assertTrue((np.abs(x2-sp2[0]) < .5))
        assertTrue((np.abs(y2-sp2[1]) < .5))
        

    def test_convert_frame_to_mrcnn_format(self):
        frame = np.ones((500, 1000), 1)
        converted = sc_utils.convert_frame_to_mrcnn_format(frame)
        assertEqual((500,1000,3), converted.shape)
        assertTrue(np.max(converted) < 256)
    
    def test_bytescale(self):
        frame = np.ones((500, 1000))
        for x,y in np.ndindex(frame.shape):
            frame[x,y] = random.randrange(0, 16383)
        converted = sc_utils.bytescale(frame, high=65535)
        assertFalse(np.max(converted) > 65535)
        assertFalse(np.min(converted) < 0)
        


if __name__ == '__main__':
    unittest.main()