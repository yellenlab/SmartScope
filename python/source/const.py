'''
List of specific system constants
'''

# Camera
EXPOSURE = 3   # ms
# FRAME_WIDTH = 1020.0  # Width of the camera frame in units of the stage
# FRAME_HEIGHT = 769.0

FRAME_WIDTH = 1210.0  # Width of the camera frame in units of the stage
FRAME_HEIGHT = 990.0 

CAMERA_PIXELS = (1024, 1376) 
FRAME_TO_PIXEL_RATIO = FRAME_WIDTH / CAMERA_PIXELS[1]

# Chip
CHIP_WIDTH = 26000.0 # Width of the chip frame in units of the stage
CHIP_HEIGHT = 9500.0