import sys
sys.path.append('C:\\Program Files\\Micro-Manager-2.0beta')

from smartscope.source import run
from smartscope.source import sc_utils
from smartscope.source import position as pos
import os
from tkinter import ttk
import tkinter as tk
from tkinter import filedialog
import tkinter.messagebox
import csv
import cv2
import PIL.Image
import PIL.ImageTk
from imutils.video import VideoStream
from pyzbar import pyzbar
import time
import imutils
from collections import OrderedDict
import yaml
import numpy as np
import tifffile as tif


BARCODE_PATH = os.path.join(os.path.dirname(sys.argv[0]), '../../config/barcode_data/')
CONFIG_YAML_PATH = os.path.join(os.path.dirname(sys.argv[0]), '../../config/experiment_config.yml')
LED_YAML_PATH = os.path.join(os.path.dirname(sys.argv[0]), '../../config/led_intensities.yml')

# BARCODE_PATH = '../../config/barcode_data/'
# CONFIG_YAML_PATH = '../../config/experiment_config.yml'
# LED_YAML_PATH = '../../config/led_intensities.yml'
vid_open = False
# stage_to_pixel_ratio = 0
# first_position = [-1, -1]


class Entry:
    def __init__(self, frame, label_text, default, row, col=0):
        self.label_text = label_text
        self.default = default
        self.frame = frame
        self.entry = tk.StringVar(self.frame, value=self.default)
        self.make_label(row, col)
        self.make_entry(row, col+1)

    def make_label(self, row, col):
        self.label = tk.Label(self.frame, text=self.label_text)
        self.label.grid(row=row, column=col)

    def make_entry(self, row, col):
        tk.Entry(self.frame, textvariable=self.entry).grid(
            row=row, column=col, sticky='EW')


class DropDown(Entry):
    def __init__(self, frame, label_text, default, options, row, col=0):
        self.label_text = label_text
        self.default = default
        self.frame = frame
        self.entry = tk.StringVar(self.frame, value=self.default)
        self.options = options
        self.make_label(row, col)
        self.make_dropdown(row, col+1)

    def make_dropdown(self, row, col):
        tk.OptionMenu(self.frame, self.entry, *
                      self.options).grid(row=row, column=col, sticky='EW')


class Main(tk.Frame):
    def __init__(self, master):
        self.master = master
        tk.Frame.__init__(self, self.master)
        self.master.title("Smart Scope")
        self.live_class = None

        ######################################################
        # Layout the frames and notebooks
        ######################################################
        row_col_config(self.master, 4, 4)

        self.Sidebar = tk.Frame(self.master)
        self.Sidebar.grid(row=0, column=3, rowspan=4,
                          columnspan=1, sticky=tk.W+tk.E+tk.N+tk.S)
        row_col_config(self.Sidebar, 8, 1)
        self.BarcodeFrame = tk.Frame(
            self.Sidebar, highlightbackground="black", highlightcolor="black", highlightthickness=1)
        self.BarcodeFrame.grid(row=0, column=0, rowspan=4,
                               sticky=tk.W+tk.E+tk.N+tk.S)
        row_col_config(self.BarcodeFrame, 4, 1)
        self.Mainframe = tk.Frame(master)
        self.Mainframe.grid(row=0, column=0, rowspan=4,
                            columnspan=3, sticky=tk.W+tk.E+tk.N+tk.S)

        self.nb = ttk.Notebook(self.Mainframe)

        self.imaging_parameters = ttk.Frame(self.nb)
        self.nb.add(self.imaging_parameters, text='Imaging Parameters')
        row_col_config(self.imaging_parameters, 14, 4)

        self.system = ttk.Frame(self.nb)
        self.nb.add(self.system, text='System Parameters')
        self.nb.pack(expand=1, fill='both')
        row_col_config(self.system, 14, 4)

        ######################################################
        # Layout the buttons, labels, and entries
        ######################################################

        # Sidebar
        tk.Button(self.Sidebar, text="Live Image", command=self.camera).grid(
            row=7, column=0, ipadx=10, ipady=3, padx=3, pady=3)
        tk.Label(self.BarcodeFrame, text="Barcode").grid(row=0, column=0)
        self.barcode_number = tk.StringVar(self.BarcodeFrame, value='')
        self.barcode_val = tk.Entry(
            self.BarcodeFrame, textvariable=self.barcode_number)
        self.barcode_val.grid(row=1, column=0)
        tk.Button(self.BarcodeFrame, text="Scan Barcode", command=self.scan_barcode).grid(
            row=3, column=0, ipadx=10, ipady=3, padx=3, pady=3)
        tk.Button(self.BarcodeFrame, text="Save", command=self.save_barcode).grid(
            row=4, column=0, ipadx=18, ipady=3, padx=3, pady=3)
        tk.Button(self.BarcodeFrame, text="Load", command=self.load_barcode).grid(
            row=5, column=0, ipadx=18, ipady=3, padx=3, pady=3)
        start = tk.Button(self.Sidebar, text="Start", font=(
            'Sans', '10', 'bold'), command=self.image)
        start.grid(row=8, column=0, ipadx=23, ipady=3, padx=3, pady=3)

        # Imaging
        # Experiment
        self.config_yaml_data = read_yaml(CONFIG_YAML_PATH)

        self.experiment_params = {
            'Chip': 1,
            'Cycle Number': 2,
            'Drug': 3,
            'Cell': 4,
            'Origin': 5,
            'Start Date': 6,
            'Concentration': 7,
            'Chip Index': 8
        }
        self.ExperimentFrame = tk.Frame(
            self.imaging_parameters, highlightbackground="black", highlightcolor="black", highlightthickness=1)
        self.ExperimentFrame.grid(
            row=0, column=0, rowspan=9, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S)
        row_col_config(self.ExperimentFrame, 9, 2)
        tk.Label(self.ExperimentFrame, text="Experiment").grid(
            row=0, column=0, columnspan=2)

        for k, v in self.experiment_params.items():
            if k == 'Chip':
                self.experiment_params[k] = DropDown(self.ExperimentFrame, k,
                                                     get_default(k), ([val['name'] for val in self.config_yaml_data['chips']]), v)
            elif k == 'Drug':
                self.experiment_params[k] = DropDown(self.ExperimentFrame, k,
                                                     get_default(k), ([val for val in self.config_yaml_data['drugs']]), v)
            elif k == 'Cell':
                self.experiment_params[k] = DropDown(self.ExperimentFrame, k,
                                                     get_default(k), ([val for val in self.config_yaml_data['cells']]), v)
            elif k == 'Origin':
                self.experiment_params[k] = DropDown(self.ExperimentFrame, k,
                                                     get_default(k), ([val for val in self.config_yaml_data['origins']]), v)
            else:
                self.experiment_params[k] = Entry(
                    self.ExperimentFrame, k, get_default(k), v)

        # Exposure
        self.led_intensities = read_yaml(LED_YAML_PATH)
        # print(self.led_intensities)
        self.exposure_params = {}
        self.exposure_checkboxes = {}

        for i, (key, val) in enumerate(self.led_intensities.items()):
            self.exposure_params[key] = i+1
            self.exposure_checkboxes[key] = tk.BooleanVar()
            if key == 'BFF':
                self.exposure_checkboxes[key].set(True)

        self.ExposureFrame = tk.Frame(self.imaging_parameters)
        self.ExposureFrame.grid(
            row=9, column=0, rowspan=4, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S)
        row_col_config(self.ExposureFrame, 8, 3)
        tk.Label(self.ExposureFrame, text="Exposure").grid(
            row=0, column=0, columnspan=2)

        for i, (k, v) in enumerate(self.exposure_checkboxes.items()):
            tk.Checkbutton(self.ExposureFrame, text=k, variable=v,
                           onvalue=True, offvalue=False).grid(row=i+1, column=2)
        for k, v in self.exposure_params.items():
            self.exposure_params[k] = Entry(
                self.ExposureFrame, k, get_default(k), v)

        # Focus
        self.focus_params = {
            'Step Size (um)': 1,
            'Initial Focus Range (um)': 2,
            'Focus Range (um)': 3,
            'Focus Points X': 4,
            'Focus Points Y': 5,
            'Focus Exposure': 6
        }
        self.FocusFrame = tk.Frame(self.imaging_parameters)
        self.FocusFrame.grid(row=0, column=2, rowspan=9,
                             columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S)
        row_col_config(self.FocusFrame, 7, 2)
        tk.Label(self.FocusFrame, text="Focus").grid(
            row=0, column=0, columnspan=4)
        for k, v in self.focus_params.items():
            self.focus_params[k] = Entry(self.FocusFrame, k, get_default(k), v)

        # Saving
        self.saving_params = {
            'Folder': 1,
            'Output Image Pixel Width': 2,
            'Output Image Pixel Height': 3
        }
        self.SaveFrame = tk.Frame(
            self.imaging_parameters, highlightbackground="black", highlightcolor="black", highlightthickness=1)
        self.SaveFrame.grid(row=9, column=2, rowspan=6,
                            columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S)
        row_col_config(self.SaveFrame, 4, 3)
        tk.Label(self.SaveFrame, text="Saving").grid(
            row=0, column=0, columnspan=4)
        for k, v in self.saving_params.items():
            self.saving_params[k] = Entry(self.SaveFrame, k, get_default(k), v)
        tk.Button(self.SaveFrame, text='...', command=lambda: self.get_directory(
            self.saving_params['Folder'])).grid(row=1, column=2)

        # System Tab Layout
        # General
        self.system_params = {
            'Alignment Model': 1,
            'Focus Model': 2,
            'Objective': 3,
            'Apartments in Image X': 4,
            'Apartments in Image Y': 5,
            'Image Rotation (degrees)': 6,
        }
        self.SystemFrame = tk.Frame(
            self.system, highlightbackground="black", highlightcolor="black", highlightthickness=1)
        self.SystemFrame.grid(row=0, column=0, rowspan=14,
                              columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S)
        row_col_config(self.SystemFrame, 7, 3)
        tk.Label(self.SystemFrame, text="General").grid(
            row=0, column=0, columnspan=4)
        for k, v in self.system_params.items():
            if k == 'Image Rotation (degrees)':
                self.system_params[k] = DropDown(self.SystemFrame, k,
                                                 get_default(k), ['0', '90', '180', '270'], v)
            else:
                self.system_params[k] = Entry(
                    self.SystemFrame, k, get_default(k), v)
        tk.Button(self.SystemFrame, text='...', command=lambda: self.get_filename(
            self.system_params['Alignment Model'])).grid(row=1, column=2)
        tk.Button(self.SystemFrame, text='...', command=lambda: self.get_filename(
            self.system_params['Focus Model'])).grid(row=2, column=2)

        # Calibration
        self.calibration_params = {
            'Frame to Pixel Ratio': 2,
            'First Position X': 5,
            'First Position Y': 6,
        }
        self.CalibrationFrame = tk.Frame(self.system)
        self.CalibrationFrame.grid(
            row=0, column=2, rowspan=14, columnspan=2, sticky=tk.W+tk.E+tk.N+tk.S)
        row_col_config(self.CalibrationFrame, 6, 3)
        tk.Label(self.CalibrationFrame, text="Calibration").grid(
            row=0, column=0, columnspan=4)

        tk.Button(self.CalibrationFrame, text='Calibrate Stage/Pixel Ratio',
                  command=self.ratio_calibrate).grid()
        self.calibration_params['Frame to Pixel Ratio'] = Entry(
                self.CalibrationFrame, 'Calibrated Stage to Pixel Ratio:', get_default('Frame to Pixel Ratio'), 2)
        tk.Label(self.CalibrationFrame,
                 textvariable=self.calibration_params['Frame to Pixel Ratio']).grid()

        tk.Button(self.CalibrationFrame, text='Calibrate First Postion',
                  command=self.first_point_calibration).grid()
        self.calibration_params['First Position X'] = Entry(
                self.CalibrationFrame, 'Calibrated First Postion X:', get_default('First Position X'), 5)
        self.calibration_params['First Position Y'] = Entry(
                self.CalibrationFrame, 'Calibrated First Postion Y:', get_default('First Position Y'), 6)
        tk.Label(self.CalibrationFrame,
                 textvariable=self.calibration_params['First Position X']).grid()
        tk.Label(self.CalibrationFrame,
                 textvariable=self.calibration_params['First Position Y']).grid()
        
        self.x_stage_dir = tk.BooleanVar()
        self.y_stage_dir = tk.BooleanVar()
        
        tk.Checkbutton(self.CalibrationFrame, text='Flip X Stage Direction', variable=self.x_stage_dir,
                           onvalue=True, offvalue=False, command=self.toggle_stage_direction).grid()
        tk.Checkbutton(self.CalibrationFrame, text='Flip X Stage Direction', variable=self.y_stage_dir,
                           onvalue=True, offvalue=False, command=self.toggle_stage_direction).grid()

        ######################################################
        # Get Stage Controller
        ######################################################
        self.mmc = sc_utils.get_stage_controller(os.path.join(os.path.dirname(sys.argv[0]),"../../config/scope_stage2.cfg"))

    def toggle_stage_direction(self):
        # stage = self.mmc.getXYStageDevice()
        # if self.x_stage_dir = True:
        #     self.mmc.setProperty(stage, 'AxisPolarityX', 'Reversed')
        pass

    def camera(self):
        global vid_open
        if not vid_open:
            vid_open = True
            live_cam = tk.Toplevel(self.master)
            self.live_class = Live_Camera(live_cam, self.mmc)
            self.live_class.window.mainloop()

    def first_point_calibration(self):
        global vid_open
        if not vid_open:
            if self.calibration_params['Frame to Pixel Ratio'].entry.get() == '':
                sc_utils.print_error(
                    'Must calibrate the Stage to Pixel Ratio first')
                return
            vid_open = True
            live_cam = tk.Toplevel(self.master)
            self.live_class = First_Point_Calibration(live_cam, self.mmc, self.experiment_params['Chip'],
                                                    self.calibration_params['First Position X'], self.calibration_params['First Position Y'],
                                                    float(self.calibration_params['Frame to Pixel Ratio'].entry.get()))
            self.live_class.window.mainloop()

    def ratio_calibrate(self):
        global vid_open
        if not vid_open:
            vid_open = True
            live_cam = tk.Toplevel(self.master)
            self.live_class = Ratio_Calibration(
                live_cam, self.mmc, self.calibration_params['Frame to Pixel Ratio'])
            self.live_class.window.mainloop()

    def get_directory(self, entry_field):
        folder = filedialog.askdirectory()
        entry_field.entry.set(folder)

    def get_filename(self, entry_field):
        file = filedialog.askopenfilename(title='Choose a file')
        entry_field.entry.set(file)

    def scan_barcode(self):
        barval = get_first_val()
        self.barcode_number.set(barval)

    def save_barcode(self):
        with open(BARCODE_PATH + str(self.barcode_number.get())+'.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            for k, v in self.get_parameter_dictionary().items():
                writer.writerow([k, v.entry.get()])
        sc_utils.print_info('Saved Barcode data to' +
                            BARCODE_PATH + str(self.barcode_number.get())+'.csv')

    def get_parameter_dictionary(self):
        return {**self.experiment_params,
                **self.exposure_params,
                **self.focus_params,
                **self.saving_params,
                **self.system_params,
                **self.calibration_params}

    def load_barcode(self):
        # Load all of the values from the saved barcode
        try:
            csvfile = csv.reader(
                open(BARCODE_PATH + str(self.barcode_number.get())+'.csv', 'r'), delimiter=",")
        except:
            sc_utils.print_error(
                "Could not open file: " + BARCODE_PATH + str(self.barcode_number.get())+'.csv')
            return
        for row in csvfile:
            params = self.get_parameter_dictionary()
            for k, v in params.items():
                if k == row[0]:
                    params[k].entry.set(row[1])
            # if 'Stage to Pixel Ratio' == row[0]:
                # self.stage_to_pixel_ratio = float(row[1])
        sc_utils.print_info('Loaded Barcode data from' +
                            BARCODE_PATH + str(self.barcode_number.get())+'.csv')

    def write_info_file(self, save_dir):
        with open(save_dir + '/info.txt', 'w+') as file:
            for k, v in self.get_parameter_dictionary().items():
                print(f"{k}: {v.entry.get()}", file=file)

    def image(self):
        # Delete Live Camera
        if self.live_class is not None:
            self.live_class.delete()

        save_dir = (self.saving_params['Folder'].entry.get()
                    + '/' + self.experiment_params['Start Date'].entry.get()
                    + '-' + self.experiment_params['Chip'].entry.get()
                    + '-' + self.experiment_params['Cell'].entry.get()
                    + '-' + self.experiment_params['Drug'].entry.get()
                    + '/' + self.experiment_params['Concentration'].entry.get(
        ) + '-' + self.experiment_params['Drug'].entry.get()
            + '/' + self.experiment_params['Chip Index'].entry.get()
            + '/').replace(' ', '-')

        saved_focus = False
        # use the directories in save_dir to determine the number of times this
        # chip has been imaged
        if not os.path.isdir(save_dir):
            time_point = 't00'
        else:
            points = len(next(os.walk(save_dir))[1])
            time_point = "t{0:0=2d}".format(points)
            saved_focus = True
        positions_dir = save_dir + 't00'
        save_dir = save_dir + time_point
        sc_utils.print_info("Set saving directory to "+save_dir)
        os.makedirs(save_dir, exist_ok=True)

        if saved_focus == True:
            saved_focus = start_popup()
        print("Saved Focus", saved_focus)

        # Write info file
        self.write_info_file(save_dir)

        for chip in self.config_yaml_data['chips']:
            if chip['name'] == self.experiment_params["Chip"].entry.get():
                cur_chip = chip

        sc_utils.print_info("Using chip: "+str(cur_chip))

        # Check if number of focus points is too low for interpolation 
        if int(self.focus_params['Focus Points X'].entry.get()) < 4:
            focus_points_x = 4
            sc_utils.print_info('Focus Points X cannot be less than 4, using 4 instead.')
        else:
            focus_points_x = int(self.focus_params['Focus Points X'].entry.get())
        if int(self.focus_params['Focus Points Y'].entry.get()) < 4:
            focus_points_y = 4
            sc_utils.print_info('Focus Points Y cannot be less than 4, using 4 instead.')
        else:
            focus_points_y = int(self.focus_params['Focus Points Y'].entry.get())

        sc_utils.before_imaging()

        first_through = True
        original_point = pos.current(self.mmc)
        for val, check in self.exposure_checkboxes.items():
            if check.get() and first_through and not saved_focus == True:
                if not val == 'BFF':
                    sc_utils.print_error(
                        'Must image in BFF first when aligning and focusing')
                    return
                sc_utils.set_led_and_shutter(
                    self.mmc, read_yaml(LED_YAML_PATH)[val][0])
                run.auto_image_chip(cur_chip,
                                    self.mmc,
                                    save_dir,
                                    self.experiment_params['Chip Index'].entry.get(),
                                    self.system_params['Alignment Model'].entry.get(),
                                    os.path.splitext(self.system_params['Focus Model'].entry.get())[0],
                                    val,
                                    float(self.focus_params['Step Size (um)'].entry.get()),
                                    int(self.focus_params['Initial Focus Range (um)'].entry.get()),
                                    int(self.focus_params['Focus Range (um)'].entry.get()),
                                    focus_points_x,
                                    focus_points_y,
                                    int(self.focus_params['Focus Exposure'].entry.get()),
                                    int(self.system_params['Image Rotation (degrees)'].entry.get()),
                                    float(self.calibration_params['Frame to Pixel Ratio'].entry.get()),
                                    sc_utils.get_frame_size(),
                                    int(self.exposure_params[val].entry.get()),
                                    [float(self.calibration_params['First Position X'].entry.get()),
                                     float(self.calibration_params['First Position Y'].entry.get())],
                                    int(self.system_params['Apartments in Image X'].entry.get()),
                                    int(self.system_params['Apartments in Image Y'].entry.get()),
                                    [int(self.saving_params['Output Image Pixel Width'].entry.get()),
                                    int(self.saving_params['Output Image Pixel Height'].entry.get())])
                                    
                first_through = False

            elif check.get():
                sc_utils.set_led_and_shutter(
                    self.mmc, read_yaml(LED_YAML_PATH)[val][0])
                run.image_from_saved_positions(cur_chip, positions_dir, save_dir, self.mmc,
                                               val, int(self.system_params['Image Rotation (degrees)'].entry.get()),
                                               int(self.exposure_params[val].entry.get()),
                                               [float(self.calibration_params['First Position X'].entry.get()),
                                                   float(self.calibration_params['First Position Y'].entry.get())],
                                               int(self.system_params['Apartments in Image X'].entry.get()),
                                               int(self.system_params['Apartments in Image Y'].entry.get()),
                                               [int(self.saving_params['Output Image Pixel Width'].entry.get()),
                                                int(self.saving_params['Output Image Pixel Height'].entry.get())])
            sc_utils.in_between_channels()
        pos.set_pos(self.mmc, x=original_point.x,
                    y=original_point.y, z=original_point.z)
        
        sc_utils.after_imaging()


def read_yaml(filename):
    with open(filename, 'r') as stream:
        try:
            vals = yaml.safe_load(stream)
            return vals
        except yaml.YAMLError as exc:
            print(exc)


def get_default(name):
    csvfile = csv.reader(open(os.path.join(os.path.dirname(sys.argv[0]),'../../config/default.csv'), "r"), delimiter=",")
    for row in csvfile:
        if name == row[0]:
            return row[1]


def row_col_config(frame, rows, cols):
    for r in range(rows):
        frame.rowconfigure(r, weight=1)
    for c in range(cols):
        frame.columnconfigure(c, weight=1)


def start_popup():
    MsgBox = tk.messagebox.askyesno(
        'Load Saved Focus Positions', 'Do you want to used the previously saved foucs points for this chip?', icon='warning')
    return MsgBox


class Live_Camera:
    def __init__(self, window, mmc):
        self.window = window
        self.window.title("Live Camera")
        self.window.protocol('WM_DELETE_WINDOW', self.delete)
        self.last_channel = ''
        self.mmc = mmc

        row_col_config(self.window, 4,4)

        self.Options = tk.Frame(self.window)
        self.Options.grid(row=0, column=0, rowspan=4, columnspan=1, sticky=tk.W+tk.E+tk.N+tk.S)

        # Base the number of items in the Options frame on how many 
        # LED configurations exist
        self.led_intensities = read_yaml(LED_YAML_PATH)
        row_col_config(self.Options, len(self.led_intensities.keys())+10, 2)

        tk.Label(self.Options, text="Settings").grid(
            row=0, column=0, columnspan=2)
        
        self.channel = tk.StringVar()

        self.channels = {}
        self.exposures = {}

        for i, (key, val) in enumerate(self.led_intensities.items()):
            self.channels[key] = tk.Radiobutton(self.Options, text=key, variable=self.channel, value=key)
            self.channels[key].grid(row=i+3, column=0)
            if key == 'BFF':
                self.channels[key].select()

        for i, (k, v) in enumerate(self.channels.items()):
            self.exposures[k] = tk.StringVar(self.Options, value=get_default(k))
            tk.Entry(self.Options, textvariable=self.exposures[k]).grid(
                        row=i+3, column=1, sticky='EW')

        self.Image = tk.Frame(self.window)
        self.Image.grid(row=0, column=1, rowspan=4, columnspan=3, sticky=tk.W+tk.E+tk.N+tk.S)
        # row_col_config(self.Image, 9, 2)
        # Camera Scale
        self.scale = 3
        self.dim = tuple(
            (np.asarray(sc_utils.get_frame_size()) / self.scale).astype(int))
        # self.dim = (int(self.width / self.scale), int(self.height / self.scale))

        self.vid = VideoCapture(mmc)

        self.canvas = tk.Canvas(self.Image, width=self.dim[0], height=self.dim[1])
        self.canvas.grid()

        # Button that lets the user take a snapshot
        self.btn_snapshot = tk.Button(
            self.Options, text="Snapshot", width=50, command=self.snapshot)
        self.btn_snapshot.grid(row=len(self.led_intensities.keys())+9, column=0, columnspan=2)

        # self.exp_entry = tk.Entry(
        #     window, textvariable=tk.StringVar(window, value="1"))
        # self.exp_entry.grid()

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()
    
    def snapshot(self):
        frame = self.vid.get_frame(self.exp)
        file = filedialog.asksaveasfilename(title='Choose a file')
        
        tif.imwrite(file+'.tif', frame)

    def update(self):
        if self.exposures[self.channel.get()].get() is not '':
            self.exp = int(self.exposures[self.channel.get()].get())
        else:
            self.exp = 1
        if self.last_channel != self.channel.get():
            sc_utils.set_led_and_shutter(self.mmc, self.led_intensities[self.channel.get()][0])
            self.last_channel = self.channel.get()

        frame = self.vid.get_frame(self.exp)
        frame = cv2.resize(frame, self.dim, interpolation=cv2.INTER_AREA)
        # img8 = (frame/4).astype('uint8')
        frame = PIL.Image.fromarray(frame)
        self.photo = PIL.ImageTk.PhotoImage(image=frame)
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.window.after(self.delay, self.update)

    def delete(self):
        global vid_open
        vid_open = False
        self.vid.delete()
        self.window.destroy()


class VideoCapture:
    def __init__(self, mmc):
        self.mmc = mmc
        # sc_utils.set_led_and_shutter(
        #     self.mmc, read_yaml(LED_YAML_PATH)['BFF'][0])
        self.cam = sc_utils.start_cam()

    def get_frame(self, exposure):
        frame = self.cam.get_frame(exp_time=exposure).reshape(
            self.cam.sensor_size[::-1])
        frame = np.flipud(frame)
        frame = sc_utils.bytescale(frame, high=255)
        return frame

    def delete(self):
        try:
            sc_utils.close_cam(self.cam)
        except:
            pass
        try:
            sc_utils.set_LEDs_off(self.mmc)
        except:
            pass


class Ratio_Calibration:
    def __init__(self, window, mmc, pixel_label):
        self.window = window
        self.window.title("Ratio Calibration")
        self.window.protocol('WM_DELETE_WINDOW', self.delete)

        # Camera Scale
        self.scale = 3
        self.width = int(sc_utils.get_frame_size()[0])
        self.height = int(sc_utils.get_frame_size()[1])
        self.dim = (int(self.width / self.scale),
                    int(self.height / self.scale))
        self.mmc = mmc
        self.vid = VideoCapture(self.mmc)
        self.pixel_label = pixel_label

        self.pixel_val_1 = np.array([self.width, self.height]) / 5 / self.scale
        self.pixel_val_2 = np.array(
            [self.width, self.height]) / 5 * 4 / self.scale

        self.canvas = tk.Canvas(window, width=self.dim[0], height=self.dim[1])
        self.canvas.pack()

        self.first_cross = True

        self.label = tk.Label(
            window, text="Align point on chip with cross, then press OK")
        self.label.pack(anchor=tk.CENTER)
        self.btn = tk.Button(window, text="OK", width=50, command=self.ok)
        self.btn.pack(anchor=tk.CENTER, expand=True)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()

    def ok(self):
        if self.first_cross:
            self.label['text'] = 'Align same point on chip with new cross, then press Finish'
            self.btn['text'] = 'Finish'
            self.first_cross = False
            self.first_point = pos.current(self.mmc, axis='xy')
        else:
            self.second_point = pos.current(self.mmc, axis='xy')
            self.delete()

    def update(self):
        exp = 1
        frame = self.vid.get_frame(exp)
        frame = cv2.resize(frame, self.dim, interpolation=cv2.INTER_AREA)
        frame = PIL.Image.fromarray(frame)
        self.photo = PIL.ImageTk.PhotoImage(image=frame)
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        if self.first_cross:
            self.canvas.create_line(self.pixel_val_1[0]-70, self.pixel_val_1[1],
                                    self.pixel_val_1[0]+70, self.pixel_val_1[1])
            self.canvas.create_line(self.pixel_val_1[0], self.pixel_val_1[1]-70,
                                    self.pixel_val_1[0], self.pixel_val_1[1]+70)
        else:
            self.canvas.create_line(self.pixel_val_2[0]-70, self.pixel_val_2[1],
                                    self.pixel_val_2[0]+70, self.pixel_val_2[1])
            self.canvas.create_line(self.pixel_val_2[0], self.pixel_val_2[1]-70,
                                    self.pixel_val_2[0], self.pixel_val_2[1]+70)
        self.window.after(self.delay, self.update)

    def delete(self):
        global vid_open
        try:
            stage_to_pixel_ratio = sc_utils.get_stage_to_pixel_ratio(self.first_point,
                                                                     self.second_point,
                                                                     self.pixel_val_1 * self.scale,
                                                                     self.pixel_val_2 * self.scale)
            self.pixel_label.entry.set(str(stage_to_pixel_ratio))
        except:
            pass
        self.vid.delete()
        self.window.destroy()
        vid_open = False


class First_Point_Calibration:
    def __init__(self, window, mmc, chip_name, point_label_x, point_label_y, frame_to_pixel_ratio):
        self.window = window
        self.window.title("First Point Calibration")
        self.window.protocol('WM_DELETE_WINDOW', self.delete)

        # Camera Scale
        self.scale = 3
        self.width = int(sc_utils.get_frame_size()[0])
        self.height = int(sc_utils.get_frame_size()[1])
        self.dim = (int(self.width / self.scale),
                    int(self.height / self.scale))
        self.mmc = mmc
        self.vid = VideoCapture(self.mmc)

        self.point_label_x = point_label_x
        self.point_label_y = point_label_y

        yaml = read_yaml(CONFIG_YAML_PATH)
        for dict in yaml['chips']:
            for key, val in dict.items():
                if val == chip_name.entry.get():
                    self.chip = dict

        self.pixel_val_1 = np.array([self.width, self.height]) / 2 / self.scale

        # Calculate rectangle size for apartment
        self.rect_width = self.chip['street_spacing'] * \
            (1/frame_to_pixel_ratio) / self.scale
        self.rect_height = self.chip['apartment_spacing'] * \
            (1/frame_to_pixel_ratio) / self.scale

        self.canvas = tk.Canvas(window, width=self.dim[0], height=self.dim[1])
        self.canvas.pack()

        self.first_cross = True

        self.label = tk.Label(
            window, text="Align first alignment mark on chip with cross, then press OK")
        self.label.pack(anchor=tk.CENTER)
        self.btn = tk.Button(window, text="OK", width=50, command=self.ok)
        self.btn.pack(anchor=tk.CENTER, expand=True)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 15
        self.update()

    def ok(self):
        if self.first_cross:
            self.label['text'] = 'Align rectangle with first apartment, then press Finish'
            self.btn['text'] = 'Finish'
            self.first_cross = False
            self.first_point = pos.current(self.mmc, axis='xy')
        else:
            self.second_point = pos.current(self.mmc, axis='xy')
            self.delete()

    def update(self):
        exp = 1
        frame = self.vid.get_frame(exp)
        frame = cv2.resize(frame, self.dim, interpolation=cv2.INTER_AREA)
        frame = PIL.Image.fromarray(frame)
        self.photo = PIL.ImageTk.PhotoImage(image=frame)
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        if self.first_cross:
            self.canvas.create_line(self.pixel_val_1[0]-70, self.pixel_val_1[1],
                                    self.pixel_val_1[0]+70, self.pixel_val_1[1])
            self.canvas.create_line(self.pixel_val_1[0], self.pixel_val_1[1]-70,
                                    self.pixel_val_1[0], self.pixel_val_1[1]+70)
        else:
            self.canvas.create_line(self.pixel_val_1[0]-self.rect_width/2, self.pixel_val_1[1]+self.rect_height/2,
                                    self.pixel_val_1[0]+self.rect_width/2, self.pixel_val_1[1]+self.rect_height/2)
            self.canvas.create_line(self.pixel_val_1[0]-self.rect_width/2, self.pixel_val_1[1]-self.rect_height/2,
                                    self.pixel_val_1[0]+self.rect_width/2, self.pixel_val_1[1]-self.rect_height/2)
            self.canvas.create_line(self.pixel_val_1[0]+self.rect_width/2, self.pixel_val_1[1]-self.rect_height/2,
                                    self.pixel_val_1[0]+self.rect_width/2, self.pixel_val_1[1]+self.rect_height/2)
            self.canvas.create_line(self.pixel_val_1[0]-self.rect_width/2, self.pixel_val_1[1]-self.rect_height/2,
                                    self.pixel_val_1[0]-self.rect_width/2, self.pixel_val_1[1]+self.rect_height/2)

        self.window.after(self.delay, self.update)

    def delete(self):
        global vid_open
        try:
            self.point_label_x.entry.set(
                str(self.first_point.x - self.second_point.x))
            self.point_label_y.entry.set(
                str(self.first_point.y - self.second_point.y))
        except:
            pass
        self.vid.delete()
        self.window.destroy()
        vid_open = False


def get_first_val():
    # vs = VideoStream(src=0).start()
    # JM changing to false since we are not using Pi camera..
    vs = VideoStream(usePiCamera=False).start()
    time.sleep(2.0)

    barcodeData = ''
    # loop over the frames from the video stream
    while True:
        # grab the frame from the threaded video stream and resize it to
        # have a maximum width of 400 pixels
        frame = vs.read()
        frame = imutils.resize(frame, width=400)

        # find the barcodes in the frame and decode each of the barcodes
        barcodes = pyzbar.decode(frame)

        # loop over the detected barcodes
        if len(barcodes) > 0:
            barcodeData = barcodes[0].data.decode("utf-8")
            break

        # show the output frame
        cv2.imshow("Barcode Scanner (q to exit)", frame)
        key = cv2.waitKey(1) & 0xFF

        # if the `q` key was pressed, break from the loop
        if key == ord("q"):
            break

    cv2.destroyAllWindows()
    vs.stop()

    return str(barcodeData)


if __name__ == '__main__':
    root = tk.Tk()
    Main(root)
    root.mainloop()
