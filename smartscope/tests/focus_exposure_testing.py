import sys
sys.path.append('C:\\Program Files\\Micro-Manager-2.0beta')
import smartscope.source.sc_utils as sc_utils
import smartscope.source.miq.miq as miq
from matplotlib import pyplot as plt
import numpy as np

def get_predictions(mmc, focus_model, focused_z, focus_range, step_size, exposure):
    z_loc = sc_utils.get_z_pos(mmc)
    prediction = []
    cam = sc_utils.start_cam()
    z_range = np.arange(-focus_range/2, focus_range/2, step_size)
    for i in z_range:
        sc_utils.set_z_pos(mmc, focused_z + i)
        sc_utils.waitForSystem()
        frame = sc_utils.get_live_frame(cam, exposure)
        prediction.append(focus_model.score(frame))
    sc_utils.close_cam(cam)
    return prediction

if __name__ == "__main__":
    focus_model = miq.get_classifier('C:/Users/cell_ml/Desktop/SC_WIN10/models/model.ckpt-1000042')
    mmc = sc_utils.get_stage_controller()
    exp1 = int(input("Enter value of 1st Exposure: "))
    exp2 = int(input("Enter value of 2nd Exposure: "))
    exp3 = int(input("Enter value of 3rd Exposure: "))
    exp4 = int(input("Enter value of 4th Exposure: "))
    exp5 = int(input("Enter value of 5th Exposure: "))
    exp6 = int(input("Enter value of 6th Exposure: "))
    exp7 = int(input("Enter value of 7th Exposure: "))
    exp8 = int(input("Enter value of 8th Exposure: "))
    input("Focus scope on interior of chip and make sure that LED intensities match desired values set in led_intensities.yml, then press Enter.")

    x = np.linspace(0, 200, 80)
    focused_z = sc_utils.get_z_pos(mmc)
    f, ((ax1, ax2, ax3, ax4), (ax5, ax6,ax7,ax8)) = plt.subplots(2, 4, sharey=True)
    ax1.scatter(x, get_predictions(mmc, focus_model, focused_z, 200, 2.5, exp1))
    ax2.scatter(x, get_predictions(mmc, focus_model, focused_z, 200, 2.5, exp2))
    ax3.scatter(x, get_predictions(mmc, focus_model, focused_z, 200, 2.5, exp3))
    ax4.scatter(x, get_predictions(mmc, focus_model, focused_z, 200, 2.5, exp4))
    ax5.scatter(x, get_predictions(mmc, focus_model, focused_z, 200, 2.5, exp5))
    ax6.scatter(x, get_predictions(mmc, focus_model, focused_z, 200, 2.5, exp6))
    ax7.scatter(x, get_predictions(mmc, focus_model, focused_z, 200, 2.5, exp7))
    ax8.scatter(x, get_predictions(mmc, focus_model, focused_z, 200, 2.5, exp8))

    sc_utils.set_z_pos(mmc, focused_z)
    f.suptitle('Focus Predictions (True Focus at ~100um)', fontsize=20)

    ax1.set_title(str(exp1) + ' ms Exposure')
    ax2.set_title(str(exp2) + ' ms Exposure')
    ax3.set_title(str(exp3) + ' ms Exposure')
    ax4.set_title(str(exp4) + ' ms Exposure')
    ax5.set_title(str(exp5) + ' ms Exposure')
    ax6.set_title(str(exp6) + ' ms Exposure')
    ax7.set_title(str(exp7) + ' ms Exposure')
    ax8.set_title(str(exp8) + ' ms Exposure')

    ax1.set_ylabel('focus score')
    ax1.set_xlabel('z-axis position (um)')

    plt.show()