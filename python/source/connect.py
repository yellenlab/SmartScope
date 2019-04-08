'''

The purpose of this class is to define scope configurations to load
and to provide feedback that a cfg file would not

'''
import MMCorePy
class Connect:
    def __init__(self):
        print('Connect devices by calling: \n1. Connect.connect_all()',
                                          '\n2. Connect.connect_pvcam()',
                                          '\n3. Connect.connect_scope()\n')
        self.scope_devices = {'Scope': 'LeicaDMI',
                              'IL-Turret': 'LeicaDMI',
                              'ObjectiveTurret': 'LeicaDMI',
                              'TL-FieldDiaphragm': 'LeicaDMI',
                              'IL - FieldDiaphragm': 'LeicaDMI',
                              'IL-ApertureDiaphragm': 'LeicaDMI',
                              'FocusDrive': 'LeicaDMI',
                              'MagnificationChanger': 'LeicaDMI',
                              'SidePort': 'LeicaDMI',
                              'IL-Shutter': 'LeicaDMI',
                              'TL-Shutter': 'LeicaDMI',
                              'Transmitted Light': 'LeicaDMI',
                              'XYStage': 'ASIStage'}

    def connect_all(self):
        return self.connect_pvcam(), self.connect_scope()

    def connect_pvcam(self):
        try:
            pvc.init_pvcam()  # Initialize PVCAM
            cam = next(Camera.detect_camera())  # Use generator to find first camera.
            cam.open()  # Open the camera
        except Exception as e:
            print("Could not connect PVCAM. Got:")
            print(e, '\n')
            return False
        return cam

    def connect_scope(self):
        try:
            mmc = MMCorePy.CMMCore()
            mmc.getVersionInfo()
        except Exception as e:
            print("Could not load micro-manager. Got:")
            print(e, '\n')
            return False

        loaded_devices = []
        for device, module in self.scope_devices.items():
            try:
                if module == 'ASIStage':
                    mmc.loadDevice(device+'_ASI', module, device)
                    loaded_devices.append(device+'ASI')
                else:
                    mmc.loadDevice(device, module, device)
                    loaded_devices.append(device)
            except Exception as e:
                print("Could not load micro-manager device. Got:")
                print(e, '\n')

        try:
           mmc.initializeAllDevices()
        except Exception as e:
            print('Could not load all MM Devices. Got:')
            print(e,'\n')
            return False

        return mmc
