import tkinter
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib import pyplot as plt, animation
from matplotlib.widgets import Button
from matplotlib.widgets import TextBox
from mpl_toolkits import mplot3d
from math import sin,cos,pi
from warnings import warn
from stl import mesh
import numpy as np
import serial
import time


plt.style.use("seaborn-dark")

for param in ['figure.facecolor', 'axes.facecolor', 'savefig.facecolor']:
    plt.rcParams[param] = '141417'  # bluish dark grey

for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
    plt.rcParams[param] = '0.9'  # very light grey

fig = plt.figure()
ax1 = fig.add_subplot(1,2,2,projection="3d")
ax2 = fig.add_subplot(3,2,1)
ax2.grid(color='#676767')
ax3 = fig.add_subplot(3,2,3)
ax3.grid(color='#676767')
ax4 = fig.add_subplot(3,2,5)
ax4.grid(color='#676767')

COM = "COM6"
data = mesh.Mesh.from_file('RocketFast.stl')

try:
    arduino = serial.Serial(port=COM, baudrate=115200, timeout=0.1)
except:
    warn("No arduino connected on {COM}.")

X = []
Yx = []
Yy = []
Yz = []
Yux = []
Yuy = []
Yha = []
Yh = []

class Processing():
    def animate(self, i):

        # Get data from rocket
        try:
            while arduino.inWaiting() > 0:
                ori = arduino.readline()

            ori = str(arduino.readline().decode("utf-8"))

            ori = ori.split(" , ")

        except:

            ori = [0,0,0,0,0,0,0,0,0]

        try:
            # Gets data for other graphs
            X.append(float(ori[3]))
            Yx.append(float(ori[0]))
            Yy.append(float(ori[1]))
            Yz.append(float(ori[2]))
            Yux.append(float(ori[4]))
            Yuy.append(float(ori[5]))
            Yha.append(float(ori[6]))
            Yh.append(float(ori[7]))
        except:
            return 1

        # Deals with 3D graphing
        if Yy[len(Yy)-2] != ori[1] or Yx[len(Yx)-2] != ori[1] or Yz[len(Yz)-2] != ori[1]:

            ax1.clear()
            data.rotate([1,0,0],np.radians(Yy[len(Yy)-2]-float(ori[1])))
            data.rotate([0,1,0],np.radians(-Yx[len(Yx)-2]+float(ori[0])))
            data.rotate([0,0,1],np.radians(-Yz[len(Yz)-2]+float(ori[2])))

            collection = mplot3d.art3d.Poly3DCollection(data.vectors)
            collection.set_facecolor('#17205B')
            ax1.add_collection3d(collection)

            scale = data.points.flatten("A")
            ax1.auto_scale_xyz(scale, scale, scale)

        if len(X) > 30:
            X.pop(0)
            Yx.pop(0)
            Yy.pop(0)
            Yz.pop(0)
            Yux.pop(0)
            Yuy.pop(0)
            Yha.pop(0)
            Yh.pop(0)

        # Deals with plotting the orientation outputs
        ax2.clear()
        ax2.plot(X,Yx, label="X")
        ax2.plot(X,Yy, label="Y")
        ax2.plot(X,Yz, label="Z")
        ax2.grid(b=True)

        # Deals with ploting the control outputs
        ax3.clear()
        ax3.plot(X,Yux, label="X")
        ax3.plot(X,Yuy, label="Y")
        ax3.grid(b=True)

        # Deals with plotting height inputs
        ax4.clear()
        ax4.plot(X,Yha, label="ACC")
        ax4.plot(X,Yh, label="ALT")
        ax4.grid(b=True)

        ax2.legend()
        ax3.legend()
        ax4.legend()

        return 1

class Events():

    def parachute(self, input):

        print("parachutes")

    def lockTVC(self, input):

        print("lockTVC")

    def demoTVC(self, input):

        print("demoTVC")

    def text(self, input):

        global arduino

        arduino = serial.Serial(port=str(input), baudrate=115200, timeout=0.1)

class Window():

    def __init__(self):

        root = tkinter.Tk()
        root.wm_title("Atlas Aerospace")

        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()

        canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        # Adds Buttons in a weird way
        event = Events()

        location = plt.axes([0.85, 0.05, 0.1, 0.075])
        chutes = Button(location, "Parachute", color="#676767")
        chutes.on_clicked(event.parachute)

        location = plt.axes([0.70, 0.05, 0.1, 0.075])
        lockTVC = Button(location, "Lock TVC", color="#676767")
        lockTVC.on_clicked(event.lockTVC)

        location = plt.axes([0.55, 0.05, 0.1, 0.075])
        TVCDemo = Button(location, "Demo TVC", color="#676767")
        TVCDemo.on_clicked(event.demoTVC)

        axbox = plt.axes([0.85, 0.9, 0.1, 0.05])
        text_box = TextBox(axbox, 'COM Port:  ', initial="", color="#676767")
        text_box.on_submit(event.text)

        process = Processing()

        anim = animation.FuncAnimation(fig, process.animate)


        #root.update_idletasks()
        root.mainloop()

if __name__ == "__main__":

    win = Window()
