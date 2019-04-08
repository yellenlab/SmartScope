from pyvcam import pvc
from pyvcam.camera import Camera

def start_cam():
    ''' Initilizes the PVCAM

    returns: cam instance
    '''
    try:
        pvc.init_pvcam()
        cam = next(Camera.detect_camera())
        cam.open()
        cam.clear_mode = 'Never'
        cam.exp_mode = "Ext Trig Trig First"
        cam.readout_port = 0
        cam.speed_table_index = 0
        cam.gain = 1
    except:
        print('Could not start camera')
        return False
    return cam

def close_cam(cam):
    ''' Closes the PVCAM instance
    args:
        - camera instance 
    '''
    try:
        cam.close()
        pvc.uninit_pvcam()
    except:
        print('Could not close Camera')

def set_pos(mmc, x, y, z=None):
    ''' Sets a microscope position
    args:
        - mmc instance
        - x (float)
        - y (float)
        - z (float) (default is None - keeps previous foucs)
    '''
    if z is not None:
        mmc.setXYPosition(x,y)
        mmc.setPosition(z)
        mmc.waitForSystem()
    else:
        mmc.setXYPosition(x,y)
        mmc.waitForSystem()

