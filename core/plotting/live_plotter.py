import datetime
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation

from config import settings
from core.data_source import serial_source, simulated_source
from core import utils

class LivePlot:
    def __init__(self):
        self.timestamps = []
        self.values = []
        self.filename = ""
        self.port = None
        self.simulation = False
        self.data_type = 1
        self.data_folder = utils.ensure_data_folder()

        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], "-", label="Messwert")
        self.ax.set_xlabel("Zeit")
        self.ax.set_ylabel("Wert")
        self.ax.grid()
        self.ax.legend()
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

    def update_plot(self, frame):
        now = datetime.datetime.now()
        if self.simulation:
            value = simulated_source.simulate_data(self.data_type)
        else:
            line = serial_source.read_serial_line(self.port)
            if line is None:
                return
            value = utils.parse_data_line(line, self.data_type)
            if value is None:
                return

        self.timestamps.append(now)
        self.values.append(value)

        with open(self.filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([now.strftime("%H:%M:%S"), value])

        self.line.set_data(self.timestamps, self.values)
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.autofmt_xdate()
        return self.line,

    def run(self):
        y_labels = {1: "Spannung (V)", 2: "SOC (%)", 3: "Zellspannung 1 (V)"}
        legends = {1: "Gesamtspannung (U)", 2: "SOC", 3: "1.Z"}
        self.ax.set_ylabel(y_labels[self.data_type])
        self.line.set_label(legends[self.data_type])
        self.ax.legend()

        self.filename = utils.create_csv_file(self.data_folder)
        ani = FuncAnimation(self.fig, self.update_plot, interval=settings.UPDATE_INTERVAL_MS, blit=False)
        plt.show()
