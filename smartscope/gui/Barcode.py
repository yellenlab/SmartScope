import tkinter as tk
from tkinter import filedialog
import csv
from imutils.video import VideoStream
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time
import cv2
import os

class Barcode:
    def __init__(self, window):
        self.window = window
        self.window.title('Cell Experiment Barcode Setup')
        self.frame = tk.Frame(self.window)

        # Lists with options
        choices = []
        choices.append([ '','G1','G2','G3','M1','K1'])
        choices.append([ '','1','2','3','4','5', '6'])
        choices.append([ '','140','150','160','170','180', '190', '200'])
        choices.append([ '', 'K562', 'K562R','K562S','K562-GFP','MOLM13', 'OCI1', 'MV411'])
        choices.append([ '','Sigma','ATCC', 'Duke CCF'])
        choices.append([1*i for i in range(21)])
        choices.append([ '', 'Control', 'Imatinib', 'Nilotinib', 'Dasatinib', 'Ponatinib'])
        choices.append([50*i for i in range(21)])
        choices.append([ '','pM','nM','uM','mM','M'])
        choices.append([1*i for i in range(21)])
        choices.append(['', 'mbar'])

        defaluts = ['G1', '1', '140', 'K562', 'Sigma', '1', 'Control', '50', 'uM', '1', 'mbar']
        names = ["Chip Type", "Cond Num", "Fab Cycle", "Cell Type", "Origin",
                 "Passage Num", "Drug Type", "Drug Conc", "Conc Unit", 
                 "Pressure Value", "Unit"]
        
        # Create a Tkinter variables
        self.popvar = []
        popupMenu = []
        label = []
        for i in range(11):
            self.popvar.append(tk.StringVar(self.window))
            self.popvar[i].set(defaluts[i])
            popupMenu.append(tk.OptionMenu(self.window, self.popvar[i], *choices[i]))
            label.append(tk.Label(self.window, text=names[i]))

        # Header Labels
        header = []
        header.append(tk.Label(self.window, text="Cell Line", font='Helvetica 13 bold'))
        header.append(tk.Label(self.window, text="Chip Config", font='Helvetica 13 bold'))
        header.append(tk.Label(self.window, text="Drug Assay", font='Helvetica 13 bold'))
        header.append(tk.Label(self.window, text="Flow Profile", font='Helvetica 13 bold'))
        header.append(tk.Label(self.window, text="Barcode Value", font='Helvetica 10'))

        # Enter Barcode using numpad on keyboard
        self.e = tk.Entry(self.window, width=10)
        scan_button = tk.Button(self.window, text="Scan", command=self.scan)

        # Save Button
        save_button = tk.Button(self.window, text="Save Values", command = self.record)
        self.window.bind('<Return>', self.record)
        self.window.bind('<KP_Enter>', self.record)

        # Layout
        ctr = 0
        for i in range(16):
            if (i % 4 == 0):
                header[int(i/4)].grid(row=i, column=0, columnspan=2)
                continue
            elif (i == 15):
                tk.Label(self.window, text="").grid(row=i, column=0)
                header[4].grid(row=i+1, column=0, columnspan=1)
                self.e.grid(row=16, column=1)
                scan_button.grid(row=17, column=0)
                save_button.grid(row=17, column=1)
                break
            else:
                label[ctr].grid(row=i, column=0)
                popupMenu[ctr].grid(row=i, column=1)
                ctr = ctr+1

    # Saves and records entered values from dropdown menu and barcode entry
    def record(self, event=None):
        # Directs which file to use
        myFile = open('csvexample.csv', 'a+')
        myData = [[(str(self.popvar[0].get())), (str(self.popvar[1].get())), 
                   (str(self.popvar[2].get())), (str(self.popvar[3].get())), 
                   (str(self.popvar[4].get())), (str(self.popvar[5].get())), 
                   (str(self.popvar[6].get())), (str(self.popvar[7].get())), 
                   (str(self.popvar[8].get())), (str(self.popvar[9].get())), 
                   (str(self.popvar[10].get())), (str(self.e.get()))]]
        with myFile:
            writer = csv.writer(myFile, )
            writer.writerows(myData)

        print('Entry was stored successfully!')
        print(myData)
        
        self.window.destroy()
    
    def scan(self):
        self.e.delete(0,len(str(self.e.get())))
        self.e.insert(0,Barcode_Scanner().get_first_val())


class Barcode_Scanner:
    def __init__(self):
        print('init')

    def continuous_mode(self):
        # initialize the video stream and allow the camera sensor to warm up
        print("[INFO] starting video stream...")

        # vs = VideoStream(src=0).start()
        vs = VideoStream(usePiCamera=False).start() #JM changing to false since we are not using Pi camera..
        time.sleep(2.0)

        # open the output CSV file for writing and initialize the set of
        # barcodes found thus far
        csv = open(args["output"], "w")
        found = set()

        # loop over the frames from the video stream
        while True:
            # grab the frame from the threaded video stream and resize it to
            # have a maximum width of 400 pixels
            frame = vs.read()
            frame = imutils.resize(frame, width=400)

            # find the barcodes in the frame and decode each of the barcodes
            barcodes = pyzbar.decode(frame)

            # loop over the detected barcodes
            for barcode in barcodes:
                # extract the bounding box location of the barcode and draw
                # the bounding box surrounding the barcode on the image
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)

                # the barcode data is a bytes object so if we want to draw it
                # on our output image we need to convert it to a string first
                barcodeData = barcode.data.decode("utf-8")
                barcodeType = barcode.type

                # draw the barcode data and barcode type on the image
                text = "{} ({})".format(barcodeData, barcodeType)
                cv2.putText(frame, text, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                # if the barcode text is currently not in our CSV file, write
                # the timestamp + barcode to disk and update the set
                if barcodeData not in found:
                    csv.write("{},{}\n".format(datetime.datetime.now(),
                        barcodeData))
                    csv.flush()
                    found.add(barcodeData)


            # show the output frame
            cv2.imshow("Barcode Scanner", frame)
            key = cv2.waitKey(1) & 0xFF
        
            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break

        # close the output CSV file do a bit of cleanup
        print("[INFO] cleaning up...")
        csv.close()
        cv2.destroyAllWindows()
        vs.stop()


    def get_first_val(self):
        # vs = VideoStream(src=0).start()
        vs = VideoStream(usePiCamera=False).start() #JM changing to false since we are not using Pi camera..
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

def main():
    root = tk.Tk()
    Barcode(root)
    root.mainloop()
 
if __name__ == '__main__':
    main()