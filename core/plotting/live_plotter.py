import datetime
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation

from config import settings
from core.data_source import serial_source, simulated_source
from core import utils

class LivePlot:
    def __init__(self, selected_graphs):
        self.timestamps = []
        self.values = {key: [] for key in selected_graphs}
        self.filename = ""
        self.port = None
        self.simulation = False
        self.selected_graphs = selected_graphs
        self.data_folder = utils.ensure_data_folder()

        self.fig, self.ax = plt.subplots()
        self.ax.set_xlabel("Zeit")
        self.ax.set_ylabel("Wert")
        self.ax.grid()
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        self.lines = {}

    def update_plot(self, frame):
        now = datetime.datetime.now()

        if self.simulation:
            data = simulated_source.simulate_full_data()
        else:
            line = serial_source.read_serial_line(self.port)
            if line is None:
                return
            data = utils.parse_full_data_line(line)
            if data is None:
                return

        # Daten schreiben
        row = [now.strftime("%H:%M:%S"), data["U"], data["SOC"]] + data["cells"]
        with open(self.filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(row)

        # Plot-Daten aktualisieren
        self.timestamps.append(now)

        for key in self.selected_graphs:
            if key == "U":
                value = data["U"]
                label = "Gesamtspannung (U)"
            elif key == "SOC":
                value = data["SOC"]
                label = "SOC (%)"
            elif key.startswith("Z"):
                index = int(key[1:]) - 1  # Z1 -> Index 0
                if 0 <= index < len(data["cells"]):
                    value = data["cells"][index]
                    label = f"{key}. Zellspannung (V)"
                else:
                    continue
            else:
                continue

            if key not in self.lines:
                self.lines[key], = self.ax.plot([], [], label=label)
            self.values[key].append(value)
            self.lines[key].set_data(self.timestamps, self.values[key])

        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.autofmt_xdate()
        self.ax.legend()
        return list(self.lines.values())

    def run(self):
        self.filename = utils.create_csv_file(self.data_folder)

        # Header schreiben
        with open(self.filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Zeit", "U", "SOC"] + [f"{i+1}.Z" for i in range(13)])

        ani = FuncAnimation(self.fig, self.update_plot, interval=settings.UPDATE_INTERVAL_MS, blit=False)
        plt.show()
