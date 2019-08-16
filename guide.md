# SmartScope Documentation

**Table of Contents**

- [GUI](#User-Interface)
  - [Batch File](#Batch-File)
  - [Parameters](#Parameters)
    - [General Imaging Parameters](#General-Imaging-Parameters)
    - [Advanced Parameters](#General-Imaging-Parameters)
- [Adding Parameters](#Adding-Parameters)
  - [Chip](#Chip)
- [Changing Camera](#Changing-Camera)
- [Training Models](#Training-Models)
  - [Alignment Model](#Alignment-Model)
  - [Focus Model](#Focus-Model)
- [How It Works](#How-It-Works)
  - [Overall Structure](#Overall-Structure)

    

## User Interface
### Batch File

### Parameters
#### General Imaging Parameters
| Parameter     | Description   |
| ------------- | ------------- |
| Chip          | The type of chip to be imaged. Included chips are ML and KL style chips. To add a new chip, see the steps in [Adding Parameters](#Adding-Parameters).|
| Objective | The magnification used for imaging. |
| Drug | Drug used on cells (used in info.txt file and in directory naming) |
| Focus Step Size (um) | Distance moved in the z-direction at each interval. | 
| Initial Focus Range (um) | Total distance moved in the z-direction across all intervals to find focal plane of first point. |
| Focus Range (um) | Total distance moved in the z-direction across all intervals to find focal plane of all focus points except the first point. |
| Focus Grid | Number of points in the x and y directions for focal adjustment. |
| Alignment Model Name | File name of the alignment machine learning model. |
| Image Rotation (degrees) | Rotation of the captured images. |
| Apartment per Image | Number of apartments to be captured in a single image, determines image center. |
|||
|||

#### Advanced Parameters

## Adding Parameters
### Chip
 To add new chips for imaging, a new chip class must be added to chip.py. This can be done in the same way as the ML and KL chip classes in that file. Also the chip name must be added to the self.chip list in App.py in order for it to appear in the GUI drop down menu. Lastly, in App.py ExpParams.image, an if statement must be added to set currchip to the new chip class. For Example: |
```
# Add a class with new values to chip.py 
class My_New_Chip(Chip):
    ''' This class inherits from the main Chip class, it adjusts the 
    constant values for the specific chip types
    '''
    # Number of apartment on chip in the y direction
    NUMBER_OF_APARTMENTS = 100.0
    # Number of apartments on chip in the x direction
    NUMBER_OF_STREETS = 100.0
    # Distance in um between the center of two apartments in x direction
    APARTMENT_SPACING = 200.0
    # Distance in um between the center of two apartments in y direction
    STREET_SPACING = 200.0

    # Chip Dimensions from alignment mark to alignment mark
    CHIP_WIDTH = 26000.0
    CHIP_HEIGHT = 9500.0

    # These values are optional, if they are not provided (delete lines below)
    # they will be calculated using the height and width of 
    # the camera frame, and the spacing of the apartments
    NUMBER_OF_APTS_IN_FRAME_X = 5
    NUMBER_OF_APTS_IN_FRAME_Y = 4

    # This is the first imaging position relative to the first alignment mark
    FIRST_POSITION = (1066.2, 266.0)
```
```
# Add to App.py
# ---------------------
# Add your chip name to the chip list in ExpParmas.setup_window
# ---------------------
self.chips = ["ML Chip", "KL Chip", "<new chip name>"]

# ---------------------
# Add this line in ExpParmas.image after the existing chips 
# ---------------------
elif chip_type == '<your new chip name>':
    curr_chip = chip.<your new chip class name>()
``` 
## Changing  Camera
All of the camera functions are located in the 'python/source/sc_utils.py' file. To change the camera used for imaging, replace the following lines at the top of the file to import your camera's python package. Then, the functions start_cam(), close_cam(), get_frame(), and get_live_frame() must be adjusted to work with the new camera.
```
# Change these lines to import different camera package
# -----------------------------------------------------
from pyvcam import pvc
from pyvcam.camera import Camera

def start_cam():
    ''' Initializes the PVCAM

    returns: cam instance
    '''
    # YOUR CODE HERE

def close_cam(cam):
    ''' Closes the PVCAM instance
    args:
        - cam: camera instance
    '''
    # YOUR CODE HERE

def get_frame(exposure):
    ''' Gets a frame from the camera '''
    cam = start_cam()
    frame = cam.get_frame(exp_time=exposure) # YOUR CODE HERE
    close_cam(cam)
    return frame

def get_live_frame(cam, exposure):
    ''' Gets a frame from the passed camera instance. This is a faster 
    way to get consecutive frames from a camera, used for focus and 
    imaging.

    args:
        - cam: camera instance 
        - exposure: exposure time

    '''
    return cam.get_frame(exp_time=exposure) # YOUR CODE HERE
# -----------------------------------------------------
```
## Training Models
### Alignment Model

### Focus Model
The focus model used in this repo is based on [Google's Microscope Image Focus Quality Classifier](https://github.com/google/microscopeimagequality), follow the instructions in the README on their github page to train a new model.
NOTE: The microscopeimagequality repo must be used with python 2.

## How It Works
### Overall Structure
