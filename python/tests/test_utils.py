import unittest
import sys
sys.path.append('../source')
import sc_utils
import numpy as np
import random


class TestUtils(unittest.TestCase):

    def test_get_frame(self):
        frame = sc_utils.get_frame(1)
        assertIsNotNone(frame)
    
    def test_get_live_frame(self):
        cam = sc_utils.start_cam()
        frame = sc_utils.get_live_frame(cam, 1)
        sc_utils.close_cam(cam)
        assertIsNotNone(frame)

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