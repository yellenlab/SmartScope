# SmartScope Documentation

**Table of Contents**

- [GUI](#User-Interface)
  - [Batch File](#Batch-File)
  - [Parameters](#Parameters)
    - [General Imaging Parameters](#General-Imaging-Parameters)
    - [Advanced Parameters](#General-Imaging-Parameters)
- [Adding Parameters](#Adding-Parameters)
    

## User Interface
### Batch File

### Parameters
#### General Imaging Parameters
| Parameter     | Description   |
| ------------- | ------------- |
| Chip          | This is the type of chip to be imaged. Included chips are ML and KL style chips. To add a new chip, see the steps in [Adding Parameters](#Adding-Parameters).|
| Objective | The magification of the objective used for imaging. |
| Drug | Drug used on cells (used in info.txt file and in directory naming) |
| | | 
#### Advanced Parameters

## Adding Parameters
### Chip
 To add new chips for imaging, a new chip class must be added to chip.py. This can be done in the same way as the ML and KL chip classes in that file. Also the chip name must be added to teh self.chip list in App.py in order for it to appear in the GUI drop down menu. Lastly, in App.py ExpParams.image, an if statement must be added to set currchip to the new chip class. For Example: |
```
# Add a class with new values to chip.py 
class My_New_Chip(Chip):
    ''' This class inherits from the main Chip class, it adjusts the 
    constant values for the specific chip types
    '''
    # Number of apartment on chip in the y direction
    NUMBER_OF_APARTMENTS = 100.0
    # Number of apartents on chip in the x direction
    NUMBER_OF_STREETS = 100.0
    # Distance in um between the center of two apartments in x direction
    APARTMENT_SPACING = 200.0
    # Distance in um between the center of two apartments in y direction
    STREET_SPACING = 200.0

    # Chip Dimentions from alignment mark to alignment mark
    CHIP_WIDTH = 26000.0
    CHIP_HEIGHT = 9500.0

    # These values are optional, if they are not provided (delete lines below)
    # they will be calculated using the height and width of 
    # the camera frame, and the spacing of the apartments
    NUMBER_OF_APTS_IN_FRAME_X = 5
    NUMBER_OF_APTS_IN_FRAME_Y = 4
```
```
# Add to App.py
# ---------------------
# Add your chip name to the chip list in ExpParmas.setup_window
# ---------------------
self.chips = ["ML Chip", "KL Chip", "<new chip name>"]

# ---------------------
# Add this line in ExpParmas.image after the extisting chips 
# ---------------------
elif chip_type == '<your new chip name>':
    curr_chip = chip.<your new chip class name>()
``` 
### 