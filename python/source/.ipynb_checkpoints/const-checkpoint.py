'''
List of specific system constants
'''

# Camera
EXPOSURE = 1   # ms
FRAME_WIDTH = 1210.0  # Width of the camera frame in units of the stage
FRAME_HEIGHT = 990.0 
CAMERA_PIXELS = (2200, 2688) 
FRAME_TO_PIXEL_RATIO = FRAME_WIDTH / CAMERA_PIXELS[1]

# Chip
CHIP_WIDTH = 25745.0 # Width of the chip frame in units of the stage
CHIP_HEIGHT = 9455.0