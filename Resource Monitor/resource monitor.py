import psutil
import time
import os
import nvgpu
from datetime import datetime
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
from tkinter import ttk
import gc
 
 
def display_usage(cpu_usage, memory_usage,
                  disk_usage_C, disk_usage_D, disk_size_C, disk_size_D, disk_total_C, disk_total_D, battery_level,
                  bars=50):
    now = datetime.now()
    time = now.strftime("%d/%m/%Y %H:%M:%S")
 
    cpu_percent = (cpu_usage / 100.0)
    cpu_bar = '*' * int(cpu_percent * bars) + '-' * (bars - int(cpu_percent * bars))
 
    memory_percent = (memory_usage / 100.0)
    memory_bar = '*' * int(memory_percent * bars) + '-' * (bars - int(memory_percent * bars))
 
    disk_percent_C = disk_usage_C / 100.0
    disk_percent_D = disk_usage_D / 100.0
    disk_bar_C = '*' * int(disk_percent_C * bars) + '-' * (bars - int(disk_percent_C * bars))
    disk_bar_D = '*' * int(disk_percent_D * bars) + '-' * (bars - int(disk_percent_D * bars))
 
    disk_used_C = disk_size_C / (1024 ** 3)
    disk_used_D = disk_size_D / (1024 ** 3)
 
    disk_total_C = disk_total_C / (1024 ** 3)
    disk_total_D = disk_total_D / (1024 ** 3)
 
    battery_level = (battery_level / 100.0)
    battery_bar = '*' * int(battery_level * bars) + '-' * (bars - int(battery_level * bars))
 
    os.system('cls')
    print(f"\rCPU Usage: |{cpu_bar}| {cpu_usage: .2f}%  ", end="\n")
    print(f"\rMemory Usage: |{memory_bar}| {memory_usage: .2f}% ", end="\n")
    print(f"\rDisk C Usage: |{disk_bar_C}| {disk_usage_C: .2f}% ", end="\n")
    print(f"\rDisk D Usage: |{disk_bar_D}| {disk_usage_D: .2f}%", end="\n")
    print(f"\rSpace used C: {disk_used_C: .2f} GB | Total space C: {disk_total_C: .2f} GB", end="\n")
    print(f"\rSpace used D: {disk_used_D: .2f} GB | Total space D: {disk_total_D: .2f} GB", end="\n")
    print(f"\rBattery Level: |{battery_bar}| {battery_level * 100: .2f}%  ", end="\n")
    print(f"\r{nvgpu.gpu_info()[0:1]}", end="\r")
 
    f.writelines(f"time = {time}\n")
    f.writelines(f"CPU Usage: |{cpu_bar}| {cpu_usage: .2f}%\n")
    f.writelines(f"Memory Usage: |{memory_bar}| {memory_usage: .2f}%\n")
    f.writelines(f"Disk C Usage: |{disk_bar_C}| {disk_usage_C: .2f}%\n")
    f.writelines(f"Disk D Usage: |{disk_bar_D}| {disk_usage_D: .2f}\n")
    f.writelines(f"Space used C: {disk_used_C: .2f} GB | Total space C: {disk_total_C: .2f} GB\n")
    f.writelines(f"Space used D: {disk_used_D: .2f} GB | Total space D: {disk_total_D: .2f} GB\n")
    f.writelines(f"Battery Level: |{battery_bar}| {battery_level * 100: .2f}%\n")
    f.writelines(f"{nvgpu.gpu_info()[0:1]}\n")
 
 
LARGE_FONT= ("Verdana", 12)
 
 
class ResourceMonitor(tk.Tk):
 
    def __init__(self, *args, **kwargs):
 
        tk.Tk.__init__(self, *args, **kwargs)
 
        tk.Tk.wm_title(self, "Resource Monitor")
 
 
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
 
        self.frames = {}
 
        for F in (StartPage, PageOne, PageTwo):
 
            frame = F(container, self)
 
            self.frames[F] = frame
 
            frame.grid(row=0, column=0, sticky="nsew")
 
        self.show_frame(StartPage)
 
    def show_frame(self, cont):
 
        frame = self.frames[cont]
        frame.tkraise()
 
class StartPage(tk.Frame):
 
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self, text="Start Page", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
 
 
        button2 = ttk.Button(self, text="Visit Page One",
                            command=lambda: controller.show_frame(PageOne))
        button2.pack()
 
        button3 = ttk.Button(self, text="Visit Page Two",
                            command=lambda: controller.show_frame(PageTwo))
        button3.pack()
 
        button_quit = ttk.Button(self, text="Quit",)
        button_quit['command'] = stop
        button_quit.pack(side=tk.BOTTOM)
 
class PageOne(tk.Frame):
 
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page One!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
 
        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()
 
        button2 = ttk.Button(self, text="Page Two",
                            command=lambda: controller.show_frame(PageTwo))
        button2.pack()
 
        global axs
        fig, axs = plt.subplots(2,2)
        fig.tight_layout(pad=3)
        ani_cpu = FuncAnimation(fig, animate_cpupercent, interval= 1000)
        ani_virtualmemory = FuncAnimation(fig, animate_virtualmemory, interval = 1000)
        ani_battery = FuncAnimation(fig, animate_battery, interval = 1000)
        ani_gpu = FuncAnimation(fig , animate_gpuusage, interval = 1000)
 
        canvas = FigureCanvasTkAgg(fig, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
 
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
 
class PageTwo(tk.Frame):
 
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Page Two", font=LARGE_FONT)
        label.pack(pady=10,padx=10)
 
        button1 = ttk.Button(self, text="Back to Home",
                            command=lambda: controller.show_frame(StartPage))
        button1.pack()
 
        fig2, axs2 = plt.subplots(2)
        fig2.tight_layout(pad=2)
        slicesC = [psutil.disk_usage('C:').used, psutil.disk_usage('C:').free]
        slicesD = [psutil.disk_usage('D:').used, psutil.disk_usage('D:').free]
        labelsC = ['Space Used C', 'Free Space C'] 
        labelsD = ['Space Used D', 'Free Space D']
        colors = ['red', 'blue']
        axs2[0].pie(slicesC, labels = labelsC, colors = colors, shadow = True, autopct = "%1.1f%%", wedgeprops = {'edgecolor': 'black'})
        axs2[0].set_title('Disk C')  
 
        axs2[1].pie(slicesD, labels = labelsD, colors = colors, shadow = True, autopct = "%1.1f%%", wedgeprops = {'edgecolor': 'black'})
        axs2[1].set_title('Disk D') 
 
 
 
        canvas = FigureCanvasTkAgg(fig2, self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
 
        toolbar = NavigationToolbar2Tk(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
 
 
frame_len = 200
y = []
z = []
x = []
w = []

def animate_cpupercent(i):
 
    y.append(psutil.cpu_percent())
 
    if len(y) <= frame_len:
        axs[0, 0].cla()
        axs[0, 0].plot(y, 'r', label='Real-Time Cpu Uses')
 
    else:
        axs[0, 0].cla()
        axs[0, 0].plot(y[-frame_len:], 'r', label='Real-Time Cpu Uses')
 
    if len(y) >= 10:
        y[:] = y[1:]
 
    axs[0, 0].set_title('Cpu Uses (%)')
    axs[0, 0].set(xlabel='Time (s)', ylabel='Cpu Uses (%)')
 
def animate_virtualmemory(i):
    z.append(psutil.virtual_memory().percent)
 
    if len(z) <= frame_len:
        axs[0, 1].cla()
        axs[0, 1].plot(z, 'r', label = 'Real-Time Memory Usage')
 
    else:
        axs[0, 1].cla()
        axs[0, 1].plot(z[-frame_len:], 'r', label = 'Real-Time Memory Usage')
 
    if len(z) >= 10:
        z[:] = z[1:]
 
    axs[0, 1].set_title('Memory Usage (%)')
    axs[0, 1].set(xlabel = 'Time (s)', ylabel = 'Memory Usage (%)')
 
def animate_battery(i):
    x.append(psutil.sensors_battery().percent)
 
    if len(x) <= frame_len:
        axs[1, 0].cla()
        axs[1, 0].plot(x, 'r', label = 'Battery level')
 
    else:
        axs[1, 0].cla()
        axs[1, 0].plot(x[-frame_len:], 'r', label = 'Battery level')
 
    if len(x) >= 10:
        x[:] = x[1:]
 
    axs[1, 0].set_title('Batter level')
    axs[1, 0].set(xlabel = 'Time (s)', ylabel = 'Battery level')
 
def animate_gpuusage(i):
    w.append(nvgpu.gpu_info()[0].get('mem_used_percent'))
 
    if len(w) <= frame_len:
        axs[1, 1].cla()
        axs[1, 1].plot(w, 'r', label = 'GPU Memory Usage')
 
    else:
        axs[1, 1].cla()
        axs[1, 1].plot(w[-frame_len:], 'r', label = 'Gpu Memory Usage')
 
    if len(w) >= 10: 
        w[:] = w[1:]
 
    axs[1, 1].set_title('GPU Memory Usage')
    axs[1, 1].set(xlabel = 'Time (s)', ylabel = 'GPU Memory Usage')
 
def stop():
    global alfa
    alfa = 0


root= ResourceMonitor()
 
alfa = 1
gc.disable()
while alfa == 1:
    f = open("resource.txt", 'a')
    root.update()
    root.update_idletasks()
    
    display_usage(psutil.cpu_percent(), psutil.virtual_memory().percent,
                  psutil.disk_usage('C:').percent, psutil.disk_usage('D:').percent, psutil.disk_usage('C:').used,
                  psutil.disk_usage('D:').used,
                  psutil.disk_usage('C:').total, psutil.disk_usage('D:').total, psutil.sensors_battery().percent, 30)
    f.close()
    time.sleep(1)