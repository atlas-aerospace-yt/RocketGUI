import tkinter
import os
import webbrowser
from tkinter.ttk import *
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib import pyplot as plt, animation
from matplotlib.widgets import Button
from matplotlib.widgets import TextBox
from mpl_toolkits import mplot3d
import matplotlib.patches as mpatches
from math import sin,cos,pi
from warnings import warn
from stl import mesh
import numpy as np
import threading
import serial
import time

plt.style.use("seaborn-dark")

for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
    plt.rcParams[param] = '#141417'

for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color','grid.color']:
    plt.rcParams[param] = '#00f0c3'


COM = "COM8"

try:
    arduino = serial.Serial(port=COM, baudrate=115200)
except:
    warn("No arduino connected on {COM}.")

time = 0

class Processing():

    def __init__(self):

        self.DisplayVehicle = True
        self.DisplayGraph = True
        self.numOfGraphs = 3
        self.X = []
        self.Graph1 = []
        self.Graph2 = []
        self.Graph3 = []

        self.transx = []
        self.transy = []
        self.transz = []


    def data(self):

        self.getData()

        try:
            if len(self.Graph3[0]) == 0:
                self.numOfGraphs = 2

            if len(self.Graph2[0]) == 0:
                self.numOfGraphs = 1

            if len(self.Graph1[0]) == 0:
                self.numOfGraphs = 0

            if len(self.vehicle) == 0:
                self.DisplayVehicle = False

        except:
            pass

    def renderLayout(self, minDiagram=False, minGraphs=False):

        self.minDiagram = minDiagram
        self.minGraphs = minGraphs

        self.fig = plt.figure()
        self.fig.clear()

        if self.numOfGraphs >= 1 and self.minGraphs == False and self.minDiagram == False:
            self.ax0 = self.fig.add_subplot(2,2,2,projection="3d")
            self.ax4 = self.fig.add_subplot(2,2,4,projection="3d")

        if self.numOfGraphs == 0 or self.minGraphs == True and self.minDiagram == False:
            self.ax0 = self.fig.add_subplot(1,2,1,projection="3d")
            self.ax4 = self.fig.add_subplot(1,2,2,projection="3d")

        if self.numOfGraphs == 3 and self.minDiagram == False and self.minGraphs == False:
            self.ax1 = self.fig.add_subplot(3,2,1)
            self.ax1.grid(color='#00f0c3')
            self.ax2 = self.fig.add_subplot(3,2,3)
            self.ax2.grid(color='#00f0c3')
            self.ax3 = self.fig.add_subplot(3,2,5)
            self.ax3.grid(color='#00f0c3')

        if self.numOfGraphs == 3 and self.minDiagram == True and self.minGraphs == False:
            self.ax1 = self.fig.add_subplot(3,1,1)
            self.ax1.grid(color='#00f0c3')
            self.ax2 = self.fig.add_subplot(3,1,2)
            self.ax2.grid(color='#00f0c3')
            self.ax3 = self.fig.add_subplot(3,1,3)
            self.ax3.grid(color='#00f0c3')

        if self.numOfGraphs == 2 and self.minDiagram == True and self.minGraphs == False:

            self.ax1 = self.fig.add_subplot(2,1,1)
            self.ax1.grid(color='#00f0c3')
            self.ax2 = self.fig.add_subplot(2,1,2)
            self.ax2.grid(color='#00f0c3')

        if self.numOfGraphs == 2 and self.minDiagram == False and self.minGraphs == False:

            self.ax1 = self.fig.add_subplot(2,2,1)
            self.ax1.grid(color='#00f0c3')
            self.ax2 = self.fig.add_subplot(2,2,3)
            self.ax2.grid(color='#00f0c3')

        if self.numOfGraphs == 1 and self.minDiagram == False and self.minGraphs == False:
            self.ax1 = self.fig.add_subplot(3,2,3)
            self.ax1.grid(color='#00f0c3')

        if self.numOfGraphs == 1 and self.minDiagram == True and self.minGraphs == False:
            self.ax1 = self.fig.add_subplot(3,1,2)
            self.ax1.grid(color='#00f0c3')


    def getData(self):

        try:
            while True:
                ori = arduino.readline()
                ori = str(ori.decode("utf-8"))
                if not "t: " in ori:
                    break
            arduino.reset_input_buffer()
        except:
            pass

        try:

            ori = ori.split(" , ")

            self.Graph1Temp = []
            self.Graph2Temp = []
            self.Graph3Temp = []
            self.vehicle = []

            self.X.append(float(ori[0]) - time)

            for item in ori:

                if item.split(":")[0] == "0":
                    self.Graph1Temp.append(float(item.split(":")[1]))

                elif item.split(":")[0] == "1":
                    self.Graph2Temp.append(float(item.split(":")[1]))

                elif item.split(":")[0] == "2":
                    self.Graph3Temp.append(float(item.split(":")[1]))

                elif item.split(":")[0] == "3d":
                    self.vehicle.append(float(item.split(":")[1]))
                    self.vehicle.append(float(item.split(":")[2]))
                    self.vehicle.append(float(item.split(":")[3]))
                    self.vehicle.append(float(item.split(":")[4]))
                    self.vehicle.append(float(item.split(":")[5]))
                    self.vehicle.append(float(item.split(":")[6]))

                else:
                    pass

            self.Graph1.append(self.Graph1Temp)
            self.Graph2.append(self.Graph2Temp)
            self.Graph3.append(self.Graph3Temp)

            if len(self.Graph1) > 30:

                self.Graph1.pop(0)

            if len(self.Graph2) > 30:

                self.Graph2.pop(0)

            if len(self.Graph3) > 30:

                self.Graph3.pop(0)

            if len(self.X) > 30:

                self.X.pop(0)

        except:

            return 1

        return 0

    def animate(self, i):

        if 1 != self.getData():

            previous = 0

            if self.minDiagram != True:

                data = mesh.Mesh.from_file('Textures/RocketFast.stl')

                self.ax0.clear()

                data.rotate([1,0,0],np.radians(self.vehicle[1]))
                data.rotate([0,1,0],np.radians(self.vehicle[0])*-1)
                data.rotate([0,0,1],np.radians(self.vehicle[2])*-1)

                collection = mplot3d.art3d.Poly3DCollection(data.vectors)
                collection.set_facecolor('#254A99')
                self.ax0.add_collection3d(collection)

                scale = data.points.flatten("A")
                self.ax0.auto_scale_xyz(scale, scale, scale)

                data = mesh.Mesh.from_file('Textures/RocketFast.stl')

                self.ax4.clear()

                data.x += float(self.vehicle[3])
                data.y += float(self.vehicle[4])
                data.z += float(self.vehicle[5])

                self.transx.append(self.vehicle[3])
                self.transy.append(self.vehicle[4])
                self.transz.append(self.vehicle[5])

                self.ax4.plot(self.transx, self.transy, self.transz, marker='o')

                collection = mplot3d.art3d.Poly3DCollection(data.vectors)
                collection.set_facecolor('#254A99')
                self.ax4.add_collection3d(collection)

                scale = data.points.flatten("A")
                self.ax4.auto_scale_xyz(scale, scale, scale)

            if self.minGraphs != True:

                if self.numOfGraphs >= 1:
                    self.ax1.clear()
                    self.Graph = self.transpose(self.Graph1)
                    for y in range(0, len(self.Graph)):

                        self.ax1.plot(self.X, self.Graph[y])
                        self.ax1.set_xlabel("time")
                        self.ax1.grid(color='#00f0c3')

                if self.numOfGraphs >= 2:
                    self.ax2.clear()
                    self.Graph = self.transpose(self.Graph2)
                    for y in range(0, len(self.Graph)):

                        self.ax2.plot(self.X, self.Graph[y])
                        self.ax2.set_xlabel("time")
                        self.ax2.grid(color='#00f0c3')

                if self.numOfGraphs >= 3:
                    self.ax3.clear()
                    self.Graph = self.transpose(self.Graph3)
                    for y in range(0, len(self.Graph)):

                        self.ax3.plot(self.X, self.Graph[y])
                        self.ax3.set_xlabel("time")
                        self.ax3.grid(color='#00f0c3')

        return self.ax4

    def getRawData(self):

        #while arduino.inWaiting() > 0:
        #    data = arduino.readline()
        try:
            data = str(arduino.readline().decode("utf-8"))
        except:
            return ""
        return data.strip()

    def reset(self):

        global time

        time += self.X[len(self.X) - 1]
        self.X = []

        self.Graph1 = []
        self.Graph2 = []
        self.Graph3 = []

    def send(self):

        arduino.write(str(win.command.get()).encode("utf-8"))

    def sendData(self, input):

        send = threading.Thread(target=self.send)
        send.start()

    def transpose(self, item):

        numpyList = np.asarray(item)
        transpose = numpyList.T
        item = transpose.tolist()

        return item

class Events():

    def __init__(self):

        self.save = False

    def minAllGraphs(self, input):

        if process.minDiagram == True:
            process.renderLayout(minDiagram=False)
        else:
            process.renderLayout(minDiagram=True)

        win.reStart()

    def minThreeDimension(self, input):

        if process.minGraphs == True:
            process.renderLayout(minGraphs=False)
        else:
            process.renderLayout(minGraphs=True)

        win.reStart()

    def reset(self, input):

        process.reset()

    def help(self, input):

        webbrowser.open('http://example.com')#

    def record(self, input):


        self.save = not self.save

        if self.save:

            self.data = threading.Thread(target=self.recordData)
            self.data.start()


    def recordData(self):

        while self.save:

            try:
                pass
            except:
                pass

class Window():

    def __init__(self):

        if not os.path.isdir("Recordings"):
            os.mkdir("Recordings")

        self.color = False

    def start(self):

        self.root = tkinter.Tk()
        self.root.wm_title("Side Kick - Live Data")

        canvas = FigureCanvasTkAgg(process.fig, master=self.root)
        canvas.draw()

        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        location = plt.axes([0.875, 0.925, 0.05, 0.0375])
        location.set_frame_on(False)
        display = Button(location, "+")
        display.label.set_fontsize(20)
        display.label.set_color('black')

        fancybox = mpatches.FancyBboxPatch((0,0), 1,1,
                                   edgecolor='#1F773D',
                                   facecolor='#00f0c3',
                                   boxstyle="round,pad=0.1",
                                   mutation_aspect=3,
                                   transform=location.transAxes, clip_on=False)


        location.add_patch(fancybox)
        display.on_clicked(event.minThreeDimension)

        location = plt.axes([0.025, 0.925, 0.05, 0.0375])

        self.graphs = Button(location, "+")
        self.graphs.label.set_fontsize(20)
        self.graphs.label.set_color('black')

        fancybox = mpatches.FancyBboxPatch((0,0), 1,1,
                                   edgecolor='#1F773D',
                                   facecolor='#00f0c3',
                                   boxstyle="round,pad=0.1",
                                   mutation_aspect=3,
                                   transform=location.transAxes, clip_on=False)
        location.add_patch(fancybox)
        self.graphs.on_clicked(event.minAllGraphs)

        location = plt.axes([0.65, 0.925, 0.15, 0.0375])
        terminal = Button(location, "TERMINAL")
        terminal.label.set_fontsize(12)
        terminal.label.set_color('black')

        fancybox = mpatches.FancyBboxPatch((0,0), 1,1,
                                   edgecolor='#1F773D',
                                   facecolor='#00f0c3',
                                   boxstyle="round,pad=0.1",
                                   mutation_aspect=3,
                                   transform=location.transAxes, clip_on=False)
        location.add_patch(fancybox)
        terminal.on_clicked(self.terminal)

        location = plt.axes([0.4, 0.925, 0.15, 0.0375])
        location.set_frame_on(False)
        reset = Button(location, "RESET")
        reset.label.set_fontsize(12)
        reset.label.set_color('black')

        fancybox = mpatches.FancyBboxPatch((0,0), 1,1,
                                   edgecolor='#1F773D',
                                   facecolor='#00f0c3',
                                   boxstyle="round,pad=0.1",
                                   mutation_aspect=3,
                                   transform=location.transAxes, clip_on=False)


        location.add_patch(fancybox)
        reset.on_clicked(event.reset)

        location = plt.axes([0.02 , 0.02, 0.075, 0.0375])
        location.set_frame_on(False)
        help = Button(location, "HELP")
        help.label.set_fontsize(12)
        help.label.set_color('black')

        fancybox = mpatches.FancyBboxPatch((0,0), 1,1,
                                   edgecolor='#153a4a',
                                   facecolor='#3db1e3',
                                   boxstyle="round,pad=0.1",
                                   mutation_aspect=3,
                                   transform=location.transAxes, clip_on=False)


        location.add_patch(fancybox)
        help.on_clicked(event.help)

        location = plt.axes([0.19, 0.925, 0.1, 0.0375])
        location.set_frame_on(False)
        record = Button(location, "REC")
        record.label.set_fontsize(12)
        record.label.set_color('white')

        self.fancybox = mpatches.FancyBboxPatch((0,0), 1,1,
                                   edgecolor='#540000',
                                   facecolor='#FF0000',
                                   boxstyle="round,pad=0.1",
                                   mutation_aspect=3,
                                   transform=location.transAxes, clip_on=False)


        location.add_patch(self.fancybox)
        record.on_clicked(event.record)

        self.minGraph = False

        anim = self.animation()

        rec = threading.Thread(target=self.recordLight)

        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(500, rec.start)
        self.root.mainloop()

    def recordLight(self):

        if event.save:

            if self.color:
                self.fancybox.set(facecolor="#FFFFFF")
            else:
                self.fancybox.set(facecolor="#FF0000")

            self.color = not self.color

        else:

            self.fancybox.set(facecolor="#FF0000")

        print(event.save)

        rec = threading.Thread(target=self.recordLight)
        self.root.after(500, rec.start)

    def close(self):

        if not event.save:

            self.root.destroy()

        else:

            event.save = False

            self.root.destroy()

    def terminal(self, input):

        self.terminal = tkinter.Toplevel(self.root)
        self.terminal.title("Side Kick - Terminal")
        self.terminal.configure(bg="#141417")
        self.terminal.minsize(width=750, height=500)
        self.terminal.maxsize(width=750, height=500)

        self.command = tkinter.Entry(self.terminal, bg="#141417",highlightthickness=2,font="Helvetica 20 bold", fg="#00f0c3", borderwidth=0)
        self.command.place(x = 30,
                     y = 430,
                     width = 690,
                     height=50)
        self.command.config(highlightbackground = "#00f0c3", highlightcolor= "#00f0c3")
        self.command.bind("<Return>", process.sendData)

        self.display = tkinter.Text(self.terminal, bg="#141417", fg="#FFFFFF", font=("Helvetica",12), borderwidth=0, highlightthickness=2)
        self.display.insert(tkinter.INSERT, "")
        self.display.config(highlightbackground = "#141417", highlightcolor= "#141417")
        self.display.place(x = 30,
                     y = 50,
                     width = 690,
                     height=370)

        self.terminalData = []
        self.text = ""

        self.terminal.after(1, self.updateText)

    def updateText(self):

        data = str(process.getRawData())

        if "t: " in data:

            self.terminalData.append(str(data.replace("t: ", "")))

            if len(self.terminalData) > 20:

                self.terminalData.pop(0)

            self.text = ""

            self.display.delete("1.0", "end")

            self.display.tag_add(">", "1.0", "1.1")
            self.display.tag_config(">", foreground="#00f0c3")

            for item in self.terminalData:

                tag = (">",)

                self.display.insert(tkinter.INSERT, f"SideKick$>", tag)
                self.display.insert(tkinter.END, f"  {item}\n")

        self.terminal.after(1, self.updateText)

    def animation(self):

        return animation.FuncAnimation(process.fig, process.animate, interval=100)

    def changeGraphButton(self):

        self.miniagram = True

    def reStart(self):

        self.root.destroy()
        self.start()

if __name__ == "__main__":


    event = Events()
    process = Processing()
    process.data()
    process.renderLayout()
    win = Window()
    win.start()
