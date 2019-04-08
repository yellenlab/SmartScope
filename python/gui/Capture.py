import tkinter as tk
from tkinter import filedialog
import csv
import datetime
import imutils
import time
import cv2
import os
from pyvcam import pvc
from pyvcam.camera import Camera
from matplotlib import pyplot as plt
import sys
import math

sys.path.insert(0, '../source')
import chip
import position as pos
import goto
import App
import _thread
import focus


class Capture:
    def __init__(self, window, mmc ,save_dir):
        self.window = window
        self.window.title('Capture Dataset')
        self.frame = tk.Frame(self.window)
        self.mmc = mmc
        self.save_dir = save_dir

        chips = chip.Chip().chip_choices.keys()
        self.selected_chip = tk.StringVar(self.window)
        chip_label = tk.Label(self.window, text='Select Chip Type:')
        chip_dropdown = tk.OptionMenu(self.window, self.selected_chip, *chips)
        chip_label.grid(row=0, column=0)
        chip_dropdown.grid(row=0, column=1)

        indentify_corners_button = tk.Button(self.window, text="Identify Corners", command=self.identify_corners)
        indentify_corners_button.grid(row=1, column=1)

    def identify_corners(self):
        identify_window = tk.Toplevel(self.window)
        if self.selected_chip.get() == '':
            print("Must select a chip fist")
        else:
            Identify(identify_window, self.selected_chip.get(), self.mmc, self.save_dir)


class Identify:
    def __init__(self, window, chip_name, mmc, save_dir):
        self.window = window
        self.window.title('Identify Corners')
        self.frame = tk.Frame(self.window)
        self.corners_pl = pos.PositionList()
        self.chip_name = chip_name
        self.mmc = mmc
        self.save_dir = save_dir

        first_button = tk.Button(self.window, text="Stage is at Bottom Right Corner", command=self.first_corner)
        first_button.grid(row=0, column=0, padx=10, pady=10)

        second_button = tk.Button(self.window, text="Stage is at Bottom Left Corner", command=self.second_corner)
        second_button.grid(row=1, column=0, padx=10, pady=10)

        third_button = tk.Button(self.window, text="Stage is at Top Left Corner", command=self.third_corner)
        third_button.grid(row=2, column=0, padx=10, pady=10)

        capture_button = tk.Button(self.window, text="Image Chip", command=self.image)
        capture_button.grid(row=3, column=0, padx=10, pady=20)

        af_button = tk.Button(self.window, text="Image Chip Auto Focus", command=self.auto_focus)
        af_button.grid(row=4, column=0, padx=10, pady=20)

    def first_corner(self):
        self.corners_pl.addPosition(pos=self.get_curr_msp(), idx=0)

    def second_corner(self):
        self.corners_pl.addPosition(pos=self.get_curr_msp(), idx=1)

    def third_corner(self):
        self.corners_pl.addPosition(pos=self.get_curr_msp(), idx=2)

    def get_curr_msp(self):
        X = self.mmc.getXPosition()
        Y = self.mmc.getYPosition()
        Z = self.mmc.getPosition()

        xy = pos.StagePosition()
        xy.stageName = 'xyStage'
        xy.numAxes = 2
        xy.x = X
        xy.y = Y

        z = pos.StagePosition()
        z.stageName = 'zStage'
        z.numAxes = 1
        z.z = Z

        msp = pos.MultiStagePosition()
        msp.defaultXYStage = 'xyStage'
        msp.defaultZStage = 'zStage'
        msp.add(xy)
        msp.add(z)

        msp.print_msp()
        return msp

    
    def image(self):
        curr_chip = chip.Chip(chip_name=self.chip_name, corner_pl=self.corners_pl)
        
        xy_focus_points = curr_chip.get_focus_xy_points(6,5)
        for i in xy_focus_points:
            print(i.getVerbose())
        #focused_points = goto.get_focus(xy_focus_points, self.mmc)

        #self.position_list = curr_chip.get_position_list(focused_points)
        #go = goto.Goto(self.mmc, xy_focus_points, '.')
        #go.image_pos_list()

        pl = pos.PositionList()

        for xy in xy_focus_points:
            self.mmc.setXYPosition(xy.x, xy.y)
            self.mmc.waitForSystem()
            # input('Press ENTER when scope is focused')
            
            # Popup Menu
            new = tk.Toplevel()
            label = tk.Label(new, text='Scope is Focused')
            label.pack()
            b2 = tk.Button(new, text = "OK", command = new.destroy)
            b2.pack()
            self.window.wait_window(new)


            z = pos.StagePosition()
            z.stageName = 'zStage'
            z.numAxes = 1
            z.z = self.mmc.getPosition()
            print (z.z) 
            msp = pos.MultiStagePosition()
            msp.defaultXYStage = 'xyStage'
            msp.defaultZStage = 'zStage'
            msp.add(xy)
            msp.add(z)

            pl.addPosition(pos=msp)

        full_pl = curr_chip.get_pos_list(pl)
        go = goto.Goto(self.mmc, full_pl, self.save_dir)
        # go.image_pos_list()
        go.image_z_stack_pos_list(10)
    
    def auto_focus(self):
        curr_chip = chip.Chip(chip_name=self.chip_name, corner_pl=self.corners_pl)
        
        xy_focus_points = curr_chip.get_focus_xy_points(5,4)
        for i in xy_focus_points:
            print(i.getVerbose())
        
        pl = focus.get_focus(xy_focus_points, self.mmc)
        full_pl = curr_chip.get_pos_list(pl)
        go = goto.Goto(self.mmc, full_pl, self.save_dir)
        # go.image_pos_list()
        go.image_z_stack_pos_list(10)

        
    
    def manual_focus(self, focus_stageposlist):
        ''' Generate a focus position list from manual focusing
            args:
            focus_stageposlist: StagePosList[] of xy positions to focus at

            returns: PostionList
        '''
        pl = pos.PositionList()

        for xy in focus_stageposlist:
            self.mmc.setXYPosition(xy.x, xy.y)
            self.mmc.waitForSystem()
            input('Press ENTER when scope is focused')
            z = pos.StagePosition()
            z.stageName = 'zStage'
            z.numAxes = 1
            z.z = self.mmc.getPosition()
            msp = pos.MultiStagePosition()
            msp.defaultXYStage = 'xyStage'
            msp.defaultZStage = 'zStage'
            msp.add(xy)
            msp.add(z)

            pl.addPosition(pos=msp)


class LiveCam:
    def __init__(self):
        print ('\nPress ENTER in terminal to exit Camera')
        
        # Setup Camera
        # pvc.init_pvcam()
        # cam = next(Camera.detect_camera())
        # cam.open()


        # cam.clear_mode = "Never"
        # cam.exp_mode = "Ext Trig Trig First"
        # cam.readout_port = 0
        # cam.speed_table_index = 0
        # cam.gain = 1
        # cam.start_live(exp_time=1)
        # img = None
        # need to make this a while loop, and find a way to escape 
        try:
            # a_list = []
            # _thread.start_new_thread(input_thread, (a_list,))
            # while not a_list:
            while True:
                frame = cam.get_live_frame().reshape(cam.sensor_size[::-1])
                # frame = cam.get_frame(exp_time=1).reshape(cam.sensor_size[::-1])
                plt.figure(1)
                plt.clf()
                plt.cla()
                plt.imshow(frame, cmap="gray")
                # Plot the crosshairs 
                plt.axhline(math.floor(cam.sensor_size[1]/2))
                plt.axvline(math.floor(cam.sensor_size[0]/2))
                plt.pause(.1)
                plt.draw()
            # cam.close()
            # pvc.uninit_pvcam()
            # plt.close()
                
        except:
            # cam.close()
            # pvc.uninit_pvcam()
            print('cannot get live cam')


# def input_thread(a_list):
#     input()
#     a_list.append(True)


