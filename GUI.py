import tkinter
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
import serial
import time

plt.style.use("seaborn-dark")

for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
    plt.rcParams[param] = '#141417'

for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color','grid.color']:
    plt.rcParams[param] = '#00f0c3'


COM = "/dev/ttyACM0"
data = mesh.Mesh.from_file('RocketFast.stl')

try:
    arduino = serial.Serial(port=COM, baudrate=115200)
except:
    warn("No arduino connected on {COM}.")

class Processing():

    def __init__(self):

        self.DisplayVehicle = True
        self.DisplayGraph = True
        self.numOfGraphs = 3
        self.X = []
        self.Graph1 = []
        self.Graph2 = []
        self.Graph3 = []

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
            self.ax0 = self.fig.add_subplot(1,2,2,projection="3d")

        if self.numOfGraphs == 0 or self.minGraphs == True and self.minDiagram == False:
            self.ax0 = self.fig.add_subplot(1,1,1,projection="3d")

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

    def arduinoDefinition(self, com, baudrate):

        pass

    def getData(self):

        try:
            while arduino.inWaiting() > 0:
                ori = arduino.readline()

            ori = str(arduino.readline().decode("utf-8"))

            ori = ori.split(" , ")
        except:
            return 1

        self.Graph1Temp = []
        self.Graph2Temp = []
        self.Graph3Temp = []
        self.vehicle = []

        self.X.append(float(ori[0]))

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
        return 0

    def animate(self, i):

        if 1 != self.getData():

            previous = 0

            if self.minDiagram != True:

                data = mesh.Mesh.from_file('RocketFast.stl')

                self.ax0.clear()
                data.rotate([1,0,0],np.radians(self.vehicle[1]))
                data.rotate([0,1,0],np.radians(self.vehicle[0])*-1)
                data.rotate([0,0,1],np.radians(self.vehicle[2])*-1)

                collection = mplot3d.art3d.Poly3DCollection(data.vectors)
                collection.set_facecolor('#254A99')
                self.ax0.add_collection3d(collection)

                scale = data.points.flatten("A")
                self.ax0.auto_scale_xyz(scale, scale, scale)

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
                        self.ax3.set_xlabel("#00f0c3")


    def getRawData(self):

        try:
            while arduino.inWaiting() > 0:
                ori = arduino.readline()

            ori = str(arduino.readline().decode("utf-8"))

            return ori.strip()

        except:
            return None

    def reset(self):

        self.X = []

        self.Graph1 = []
        self.Graph2 = []
        self.Graph3 = []

    def sendData(self,input):

        arduino.write(bytes(input, 'utf-8'))

    def transpose(self, item):

        numpyList = np.asarray(item)
        transpose = numpyList.T
        item = transpose.tolist()

        return item

class Events():

    def __init__(self, process, window):

        self.window = window
        self.process = process

    def minAllGraphs(self, input):

        if self.process.minDiagram == True:
            self.process.renderLayout(minDiagram=False)
        else:
            self.process.renderLayout(minDiagram=True)

        self.window.reStart()

    def minThreeDimension(self, input):

        if self.process.minGraphs == True:
            self.process.renderLayout(minGraphs=False)
        else:
            self.process.renderLayout(minGraphs=True)

        self.window.reStart()

    def reset(self, input):

        self.process.reset()

class Window():

    def __init__(self):

        self.root = tkinter.Tk()
        self.root.wm_title("Atlas Aerospace")

        canvas = FigureCanvasTkAgg(process.fig, master=self.root)
        canvas.draw()

        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        event = Events(process, self)

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

        self.text = tkinter.StringVar()

        self.graphs = Button(location, self.text)
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

        location = plt.axes([0.75, 0.035, 0.15, 0.03])
        terminal = Button(location, "Terminal")
        terminal.label.set_fontsize(15)
        terminal.label.set_color('black')

        fancybox = mpatches.FancyBboxPatch((0,0), 1,1,
                                   edgecolor='#1F773D',
                                   facecolor='#00f0c3',
                                   boxstyle="round,pad=0.1",
                                   mutation_aspect=3,
                                   transform=location.transAxes, clip_on=False)
        location.add_patch(fancybox)
        terminal.on_clicked(self.Terminal)

        location = plt.axes([0.5, 0.925, 0.05, 0.0375])
        location.set_frame_on(False)
        reset = Button(location, "RST")
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

        self.minGraph = False
        anim = animation.FuncAnimation(process.fig, process.animate)

        self.root.mainloop()

    def task(self):

        data = str(process.getRawData())

        if data != '1':
            self.data.append(str(process.getRawData()) + "\n")

            if len(self.data) > 30:

                self.data.pop(0)

        text = ''
        for item in self.data:

            text += item

        self.label.config(text=text,bg='#141417',fg='white')
        self.terminal.after(1,self.task)

    def Terminal(self, input):

        self.data = []

        self.terminal = tkinter.Toplevel(self.root)
        self.terminal.title("Terminal")
        self.terminal.configure(bg='#141417')
        self.terminal.geometry('270x500')
        self.terminal.rowconfigure(0, weight=1)
        self.terminal.columnconfigure(0, weight=1)

        self.label = tkinter.Label(self.terminal, text=self.data)
        self.label.pack(side = 'left')

        self.entry = tkinter.Entry(self.terminal,fg='#00f0c3')
        self.entry.pack()

        self.terminal.after(1,self.task)
        self.terminal.mainloop()

    def changeDisplayButton(self):

        if self.minGraph == True:

            self.minGraph = False
            self.text.set("1adhdfhsd")
        else:
            self.minGraph = True
            self.text.set("jkjjkjhjk")

    def changeGraphButton(self):

        self.miniagram = True

    def reStart(self):

        self.changeDisplayButton()
        self.root.destroy()
        self.__init__()

if __name__ == "__main__":
    process = Processing()
    process.data()
    process.renderLayout()
    win = Window()
