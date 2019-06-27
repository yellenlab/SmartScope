try:
    from pyvcam import pvc
    from pyvcam.camera import Camera
except:
    print('WARNING: pyvcam not installed')
try:
    import MMCorePy
except:
    print('WARNING: Micro-Manager is not installed')

from numba import autojit

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
        raise RuntimeError('Could not start Camera')
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

def get_mmc(cfg="../../config/scope_stage.cfg"):
    mmc = MMCorePy.CMMCore()
    mmc.loadSystemConfiguration(cfg)
    mmc.setFocusDevice('FocusDrive')
    return mmc

def get_frame(exposure):
    cam = sc_utils.start_cam()
    frame = cam.get_frame(exp_time=exposure)
    sc_utils.close_cam(cam)
    print(frame.shape)
    return frame

@autojit
def convert_frame_to_mrcnn_format(frame):
    ''' Converts the output from the PVCAM frame 
    into the format that the mrcnn model was trained on

    args:
        frame: frame output from PVCAM
    returns:
        frame in mrcnn fromat
    '''
    new_im = np.zeros((frame.shape[0], frame.shape[1], 3))
    frame = covert_frame_to_uint8(frame)
    for ix, iy in np.ndindex(frame.shape):
        val = frame[ix,iy]
        new_im[ix,iy] = [val,val,val]
    new_im = new_im.astype('uint8')
    return new_im

def covert_frame_to_uint8(frame):
    uint8_divider = np.max(frame) / 250
    return np.ceil(frame/uint8_divider)