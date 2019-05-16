try:
    from pyvcam import pvc
    from pyvcam.camera import Camera
except:
    print('WARNING: pyvcam not installed')
try:
    import MMCorePy
except:
    print('WARNING: Micro-Manager is not installed')

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

def get_mmc(cfg="../../config/MMConfig_YellenLab_ubuntu.cfg"):
    mmc = MMCorePy.CMMCore()
    mmc.loadSystemConfiguration(cfg)
    mmc.setFocusDevice('FocusDrive')
    return mmc


