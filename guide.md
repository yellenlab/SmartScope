# SmartScope Documentation

**Table of Contents**

- [GUI](#User-Interface)
  - [Batch File](#Batch-File)
  - [Parameters](#Parameters)
    - [Experiment](#Experiments)
    - [Exposure](#Exposure)
    - [Focus](#Focus)
    - [Saving](#Saving)
    - [General](#General)
    - [Calibration](#Calibration)
- [Adding Parameters](#Adding-Parameters)
- [Changing Camera](#Changing-Camera)
- [Training Models](#Training-Models)
  - [Alignment Model](#Alignment-Model)
  - [Focus Model](#Focus-Model)
- [How It Works](#How-It-Works)
  - [Overall Structure](#Overall-Structure)

    

## User Interface
### Batch File

## Parameters
### Experiment


| Parameter     | Description   | Function |
| ------------- | ------------- | -------- |
| Chip          | The type of chip to be imaged. Included chips are ML and KL style chips. To add a new chip, see the steps in [Adding Parameters](#Adding-Parameters).| Controls where the scope looks for alignment marks, focuses, and images. |
| Cycle Number | The number of cycles used in manufacturing the current chip. | None |
| Drug | Drug used on cells. | Used in file path. |
| Cell | Type of cell on chip. | None |
| Origin | Origin of cells.  | None |
| Start Date | Date at the beginning of the experiment. | Used in file path. |
| Concentration | Concentration of drug used on cells. If Control leave blank. |  Used in file path. |
| Chip Index | Number to identify chip. | Used in file path. |

### Exposure
| Parameter     | Description   | Function |
| ------------- | ------------- | -------- |
| Name of Channel | Exposure time for the particular channel specified in led_intensities.yml | When checked, channel and exposure settings will be imaged. If more than one channel is selected, the scope will image multiple times using the same focus and alignment values. |

### Focus
| Parameter        | Function |
| ------------- | -------- |
| Step Size (um) | Distance moved in the z-direction at each interval. | 
| Initial Focus Range (um) | Total distance moved in the z-direction across all intervals to find focal plane of first point. |
| Focus Range (um) | Total distance moved in the z-direction across all intervals to find focal plane of all focus points following the first point. |
| Focus Points X | Number of points in the x direction for focal adjustment. |
| Focus Points Y | Number of points in the y direction for focal adjustment. |
| Focus Exposure | The camera exposure to use for focusing. This value can be calibrated following the [Focus Exposure Calibration](#Focus-Exposure-Calibration) instructions. |

### Saving
| Parameter    | Function |
| -------------| -------- |
|Folder|
|Output Image Pixel Width|
|Output Image Pixel Height|

### General
| Parameter     | Description   | Function |
| ------------- | ------------- | -------- |
| Alignment Model Name | Alignment Mask-RCNN model file. |
| Focus Model | Focus model file |
| Objective | The magnification used for imaging. | None |
| Apartment per Image | Number of apartments to be captured in a single image | Determines image center. |
| Image Rotation (degrees) | Rotation of the captured images. | This can be adjusted if images are not saved in the proper orientation. |

### Calibration 
| Parameter     | Description   | Function |
| ------------- | ------------- | -------- |
| Stage to Pixel Ratio | This is the ratio that coverts between pixels and microns | This ratio is needed for determining the stage position of the center of an alignment mark. |
| Calibrated First Position | XY distance from the center of the first alignment mark to the center of the first apartment. | This is used to calculate the positions for all of the images. |

#### Advanced Parameters

## Adding Parameters
 To add new parameters and values for imaging, simply add to the   yaml files in following the formats:


### Chips - experiment_config.yml
```
chips: 
 - name: "Name to Identify Chip"
   number_of_apartments: number of apartments in the y direction
   number_of_streets: number of apartments in the x direction
   apartment_spacing: length of one apartment in the y direction
   street_spacing: length of one apartment in the x direction
   chip_width: total distance alignment marks in the x direction
   chip_height: total distance alignment marks in the y direction
``` 
### Drugs, Cells, Origins - experiment_config.yml
```
drugs:
 - name of drug
cells:
 - name of cell type
origins:
 - origins of cells
```
### Lighing and shutters - led_intensities.yml
```
Channel name:
  - shutter: number representing the turret position (defined in mmc cfg file)
    LED name 1: intensity (0-100)
    LED name 2: intensity (0-100) 
    LED name 3: intensity (0-100) 
    LED name 4: intensity (0-100) 
```

For these changes to take effect the application must be restarted.
## Changing Camera
All of the camera functions are located in the 'smartscope/source/sc_utils.py' file. To change the camera used for imaging, replace the following lines at the top of the file to import your camera's python package. Then, the functions start_cam(), close_cam(), get_frame_size(), get_frame(), and get_live_frame() must be adjusted to work with the new camera.
```
# Change these lines to import different camera package
# -----------------------------------------------------
from pyvcam import pvc
from pyvcam.camera import Camera

def start_cam():
    ''' Initializes the PVCAM

    returns: cam instance
    '''
    try:
        # YOUR CODE HERE
    except:
        raise RuntimeError('Could not start Camera')
    return cam

def close_cam(cam):
    ''' Closes the PVCAM instance
    args:
        - cam: camera instance
    '''
    # YOUR CODE HERE

def get_frame_size():
    '''
    returns a tuple (<image pixel width>, <image pixel height>)
    '''
    cam = start_cam()
    shape = cam.shape # YOUR CODE HERE
    close_cam(cam)
    return shape

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
## Changing LED and Shutter Control
To change the LED and shutter control, the change_shutter() and change_LED_value() functions in smartscope/source/sc_utils.py must be adjusted.

## Focus Exposure Calibration

## Training Models
### Alignment Model

### Focus Model
The focus model used in this repo is based on [Google's Microscope Image Focus Quality Classifier](https://github.com/google/microscopeimagequality), follow the instructions in the README on their github page to train a new model.
NOTE: The microscopeimagequality repo must be used with python 2.

## How It Works
### Overall Structure
