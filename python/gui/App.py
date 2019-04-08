import tkinter as tk
from tkinter import filedialog
# from tkthread import tk, TkThread

import Barcode
import Capture
import MMCorePy
from pyvcam import pvc
from pyvcam.camera import Camera
import sys
sys.path.insert(0, '../source')
import connect
from matplotlib import pyplot as plt
import _thread
import math
import time


class App:
    def __init__(self, master):
        self.master = master
        self.master.title('Smart Scope')
        self.master.geometry('{}x{}'.format(350, 200))

        # Some default path for new images
        self.image_directory = '../data/'

        #self.mmc = connect.Connect().connect_all()
        # This should be temparary. Want to use ^^^
        # Connect micro-manager
        self.mmc = MMCorePy.CMMCore()
        # Load Scope Config from file
        self.mmc.loadSystemConfiguration("../../config/MMConfig_YellenLab_ubuntu.cfg")
        print ("Devices loaded from config file:\n", self.mmc.getLoadedDevices())
        print ("\n Stage at: (", self.mmc.getXPosition(), ",", self.mmc.getYPosition(), ")")
        xyStage = self.mmc.getXYStageDevice()
        zStage = self.mmc.setFocusDevice('FocusDrive')

        # create all of the main containers
        # the crazy colors are to give a visual of the containers during development
        top_frame = tk.Frame(self.master, width=450, height=50, pady=3)
        center = tk.Frame(self.master, width=50, height=40, padx=3, pady=3)
        btm_frame = tk.Frame(self.master, width=450, height=60, pady=3)
        ctr_left = tk.Frame(center, width=150, height=50)
        ctr_right = tk.Frame(center, width=150, height=50, padx=3, pady=3)

        # layout all of the main containers
        self.master.grid_rowconfigure(1, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        top_frame.grid(row=0, sticky="ew")
        center.grid(row=1, sticky="nsew")
        btm_frame.grid(row=3, sticky="ew")

        # createcenter widgets
        center.grid_rowconfigure(0, weight=1)
        center.grid_columnconfigure(1, weight=1)
        ctr_left.grid(row=0, column=0, sticky="ns")
        ctr_right.grid(row=0, column=1, sticky="nsew")

        # create the widgets for the top frame
        title_label = tk.Label(top_frame, text='Smart Scope', font=("Helvetica", 30))
        directory_label = tk.Label(btm_frame, text='Current Image Directory:')
        self.directory_label_path = tk.Label(btm_frame, text=self.image_directory)
        button2 = tk.Button(btm_frame, text='...', command=self.get_directory)

        # layout the widgets in the top frame
        title_label.grid(row=0, column=0, padx='65', pady='10')
        directory_label.grid(row=0, column=0, padx='10')
        self.directory_label_path.grid(row=0, column=1, padx='10', pady='10')
        button2.grid(row=0, column=2)

        # create the widgets forcenter frames
        camera_button = tk.Button(ctr_left, text='Live Camera', command=self.live_window)
        move_button = tk.Button(ctr_left, text='Move Manually', command=self.move_window)
        barcode_button = tk.Button(ctr_right, text='Add Barcode', command=self.barcode_window)
        capture_button = tk.Button(ctr_right, text='Capture', command=self.capture_window)

        # layout the widgets incenter frames
        camera_button.grid(row=0, column=0, padx='30', pady='10')
        move_button.grid(row=1, column=0, padx='30', pady='10')
        barcode_button.grid(row=0,column=0, padx='20', pady='10')
        capture_button.grid(row=1, column=0, padx='20', pady='10')

    def live_window(self):
        _thread.start_new_thread(live_cam, (self.cam, ))
        # Capture.LiveCam(self.cam)

    def capture_window(self):
        capture_window_cont = tk.Toplevel(self.master)
        Capture.Capture(capture_window_cont, self.mmc, self.image_directory)

    def get_directory(self):
        folder = filedialog.askdirectory()
        self.image_directory = folder
        self.directory_label_path['text'] = folder

    def move_window(self):
        move_window_cont = tk.Toplevel(self.master)
        MoveArrows(move_window_cont, "Move", self.mmc)
    
    def barcode_window(self):
        barc = tk.Toplevel(self.master)
        Barcode.Barcode(barc)

def live_cam(camera):
    # try:
    while True:
        print ('hello')
        frame = camera.get_live_frame().reshape(camera.sensor_size[::-1])
        # frame = cam.get_frame(exp_time=1).reshape(cam.sensor_size[::-1])
        plt.figure(1)
        plt.clf()
        # plt.cla()
        plt.imshow(frame, cmap="gray")
        # Plot the crosshairs 
        plt.axhline(math.floor(camera.sensor_size[1]/2))
        plt.axvline(math.floor(camera.sensor_size[0]/2))
        plt.pause(.2)
        plt.draw()
    # cam.close()
    # pvc.uninit_pvcam()
    # plt.close()
            
    # except:
    #     # cam.close()
    #     # pvc.uninit_pvcam()
    #     print('cannot get live cam')

class MoveArrows:
    def __init__(self, window, window_title, mmc):
        self.window = window
        self.window.title(window_title)
        self.frame = tk.Frame(self.window)
        self.mmc = mmc

        # Bind the keys to the window so arrow keys register
        self.window.bind_all('<Key>', self.key)

        # create layout of containers
        self.window.grid_rowconfigure(1, weight=1)
        self.window.grid_columnconfigure(0, weight=1)

        # create the frames for the buttons
        self.bottomframe = tk.Frame(self.window)
        self.bottomframe.grid(row=2, column=1, padx=3, pady=3)
        self.topframe = tk.Frame(self.window)
        self.topframe.grid(row=0, column=1, padx=3, pady=3)
        self.leftframe = tk.Frame(self.window)
        self.leftframe.grid(row=1, column=0, padx=3, pady=3)
        self.rightframe = tk.Frame(self.window)
        self.rightframe.grid(row=1, column=2, padx=3, pady=3)

        # pack the buttons into te corresponding frames
        self.upbutton = tk.Button(self.topframe, text='up', command=self.moveup)
        self.upbutton.pack(side="top")
        self.downbutton = tk.Button(self.topframe, text='down', command=self.movedown)
        self.downbutton.pack(side="bottom")
        self.leftbutton = tk.Button(self.topframe, text='left', command=self.moveleft)
        self.leftbutton.pack(side="left")
        self.rightbutton = tk.Button(self.topframe, text='right', command=self.moveright)
        self.rightbutton.pack(side="right")

        self.window.mainloop()

    def key(self, event):

        if event.keysym == "Up":
            self.upbutton.invoke()
            self.upbutton.flash()
        if event.keysym == "Down":
            self.downbutton.invoke()
            self.downbutton.flash()
        if event.keysym == "Left":
            self.leftbutton.invoke()
            self.leftbutton.flash()
        if event.keysym == "Right":
            self.rightbutton.invoke()
            self.rightbutton.flash()

    def moveup(self):
        # Move scope up
        self.mmc.setXYPosition(self.mmc.getXPosition(), self.mmc.getYPosition()-50.0)

    def movedown(self):
        # Move scope down
        self.mmc.setXYPosition(self.mmc.getXPosition(), self.mmc.getYPosition()+50.0)

    def moveleft(self):
        # Move scope left
        self.mmc.setXYPosition(self.mmc.getXPosition()+50.0, self.mmc.getYPosition())

    def moveright(self):
        # Move scope right
        self.mmc.setXYPosition(self.mmc.getXPosition()-50.0, self.mmc.getYPosition())


def main():
    # # Start Camera
    try:
        pvc.init_pvcam()
        cam = next(Camera.detect_camera())
        cam.open()
        time.sleep(0.1)
        cam.close()
        pvc.uninit_pvcam()
    except:
        print ('WARNING: Cannot Start PVCAM')

    root = tk.Tk()
    def on_closing():
        try:
            cam.close()
            pvc.uninit_pvcam()
        except:
            pass

    root.protocol("WM_DELETE_WINDOW", on_closing)
    App(root)
    root.mainloop()


if __name__ == '__main__':
    main()