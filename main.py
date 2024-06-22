import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time


def read_data():
    numbers = []
    statuses = []
    x_coords = []
    y_coords = []

    with open('data.txt', 'r') as file:
        for line in file:
            data = line.strip().split(',')
            if len(data) == 4:
                numbers.append(int(data[0]))
                statuses.append(int(data[1]))
                x_coords.append(float(data[2]))
                y_coords.append(float(data[3]))

    min_x, min_y = min(x_coords), min(y_coords)
    x_coords = [x - min_x for x in x_coords]
    y_coords = [y - min_y for y in y_coords]

    return numbers, statuses, x_coords, y_coords


class DataVisualization:
    def __init__(self, master):
        self.master = master
        self.master.title("Data Visualization")
        self.master.geometry("1920x1200")

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
                    break

        for vehicle_type, style in styles.items():
            if style['alive']:
                x, y = zip(*style['alive'])
                self.ax.scatter(x, y, marker=style['marker'], c=style['color'], label=f'{vehicle_type} (Alive)')
            if style['dead']:
                x, y = zip(*style['dead'])
                self.ax.scatter(x, y, marker=style['marker'], c=style['color'], alpha=0.3,
                                label=f'{vehicle_type} (Dead)')

        self.ax.set_title('Object Visualization (Relative Coordinates)')
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.grid(True)
        self.ax.legend()

        self.ax.set_xlim(-0.001, max(x_coords) + 0.001)
        self.ax.set_ylim(-0.001, max(y_coords) + 0.001)

        self.canvas.draw()

    def update_data(self):
        numbers, statuses, x_coords, y_coords = read_data()
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