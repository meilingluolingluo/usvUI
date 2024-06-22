import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
from collections import deque
import numpy as np
import math


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])

    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # 地球平均半径，单位为公里
    return c * r * 1000  # 转换为米


class DataVisualization:
    def __init__(self, master):
        self.master = master
        self.master.title("Data Visualization")
        self.master.geometry("800x600")

        self.figure, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.master)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.button_frame = ttk.Frame(master)
        self.button_frame.pack(pady=10)

        self.update_button = ttk.Button(self.button_frame, text="Update Data", command=self.update_data)
        self.update_button.pack(side=tk.LEFT, padx=5)

        self.auto_update = True
        self.auto_update_button = ttk.Button(self.button_frame, text="Pause Auto Update",
                                             command=self.toggle_auto_update)
        self.auto_update_button.pack(side=tk.LEFT, padx=5)

        self.update_thread = threading.Thread(target=self.auto_update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()

        self.max_trajectory_length = 10  # 设置最大轨迹长度
        self.trajectories = {}  # 用于存储每个物体的轨迹
        self.origin = None  # 用于存储原点的经纬度

    def read_data(self):
        numbers = []
        statuses = []
        lons = []
        lats = []

        with open('data.txt', 'r') as file:
            for line in file:
                data = line.strip().split(',')
                if len(data) == 4:
                    numbers.append(int(data[0]))
                    statuses.append(int(data[1]))
                    lons.append(float(data[2]))
                    lats.append(float(data[3]))

        return numbers, statuses, lons, lats

    def convert_to_meters(self, lons, lats):
        if self.origin is None:
            # 设置原点为第一个数据点（假设是左下角的物体）
            self.origin = (lons[0], lats[0])

        x_coords = []
        y_coords = []
        for lon, lat in zip(lons, lats):
            x = haversine(self.origin[0], self.origin[1], lon, self.origin[1])
            y = haversine(self.origin[0], self.origin[1], self.origin[0], lat)
            if lon < self.origin[0]:
                x = -x
            if lat < self.origin[1]:
                y = -y
            x_coords.append(x)
            y_coords.append(y)

        return x_coords, y_coords

    def plot_data(self, numbers, statuses, x_coords, y_coords):
        self.ax.clear()

        styles = {
            'USV': {'marker': 'o', 'color': 'blue', 'range': range(1, 101)},
            'AUV': {'marker': 's', 'color': 'green', 'range': range(101, 201)},
            'UAV': {'marker': '^', 'color': 'red', 'range': range(201, 301)}
        }

        for style in styles.values():
            style['alive'] = []
            style['dead'] = []

        for i, number in enumerate(numbers):
            for vehicle_type, style in styles.items():
                if number in style['range']:
                    if statuses[i] == 1:
                        style['alive'].append((x_coords[i], y_coords[i]))
                    else:
                        style['dead'].append((x_coords[i], y_coords[i]))

                    self.ax.annotate(str(number), (x_coords[i], y_coords[i]), xytext=(5, 5),
                                     textcoords='offset points', fontsize=8, color=style['color'])

                    # 更新轨迹
                    if number not in self.trajectories:
                        self.trajectories[number] = deque(maxlen=self.max_trajectory_length)
                    self.trajectories[number].append((x_coords[i], y_coords[i]))
                    if len(self.trajectories[number]) > 1:
                        traj = list(self.trajectories[number])
                        # 创建颜色渐变
                        colors = np.ones((len(traj), 4))
                        colors[:, :3] = plt.cm.colors.to_rgb(style['color'])
                        colors[:, 3] = np.linspace(0.1, 1, len(traj))

                        for j in range(len(traj) - 1):
                            self.ax.plot(*zip(traj[j], traj[j + 1]), color=colors[j], alpha=colors[j, 3], linewidth=1)

                    break

        for vehicle_type, style in styles.items():
            if style['alive']:
                x, y = zip(*style['alive'])
                self.ax.scatter(x, y, marker=style['marker'], c=style['color'], label=f'{vehicle_type} (Alive)')
            if style['dead']:
                x, y = zip(*style['dead'])
                self.ax.scatter(x, y, marker=style['marker'], c=style['color'], alpha=0.3,
                                label=f'{vehicle_type} (Dead)')

        self.ax.set_title('Object Visualization (Meters from Origin)')
        self.ax.set_xlabel('X (m)')
        self.ax.set_ylabel('Y (m)')
        self.ax.grid(True)
        self.ax.legend()

        self.ax.set_xlim(min(x_coords) - 100, max(x_coords) + 100)
        self.ax.set_ylim(min(y_coords) - 100, max(y_coords) + 100)

        self.canvas.draw()

    def update_data(self):
        numbers, statuses, lons, lats = self.read_data()
        x_coords, y_coords = self.convert_to_meters(lons, lats)
        self.plot_data(numbers, statuses, x_coords, y_coords)

    def toggle_auto_update(self):
        self.auto_update = not self.auto_update
        if self.auto_update:
            self.auto_update_button.config(text="Pause Auto Update")
        else:
            self.auto_update_button.config(text="Resume Auto Update")

    def auto_update_loop(self):
        while True:
            if self.auto_update:
                self.update_data()
            time.sleep(30)


if __name__ == "__main__":
    root = tk.Tk()
    app = DataVisualization(root)
    root.mainloop()
