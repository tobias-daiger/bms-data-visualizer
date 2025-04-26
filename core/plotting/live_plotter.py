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
            data = simulated_source.simulate_full_data()
        else:
            line = serial_source.read_serial_line(self.port)
            if line is None:
                return
            data = utils.parse_full_data_line(line)
            if data is None:
                return

        # Speichern aller Daten
        row = [
            now.strftime("%H:%M:%S"),
            data["U"],
            data["SOC"],
            *data["cells"]
        ]

        with open(self.filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(row)

        # Plotten nur des ausgewählten Datentyps
        if self.data_type == 1:
            value = data["U"]
        elif self.data_type == 2:
            value = data["SOC"]
        else:
            value = data["cells"][self.data_type - 3]

        self.timestamps.append(now)
        self.values.append(value)

        self.line.set_data(self.timestamps, self.values)
        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.autofmt_xdate()
        return self.line,

    def run(self):
        y_labels = {
            1: "Spannung (V)", 2: "SOC (%)",
            **{i + 3: f"{i + 1}. Zellspannung (V)" for i in range(13)}
        }
        legends = {
            1: "Gesamtspannung (U)", 2: "SOC",
            **{i + 3: f"{i + 1}.Z" for i in range(13)}
        }
        self.ax.set_ylabel(y_labels[self.data_type])
        self.line.set_label(legends[self.data_type])
        self.ax.legend()

        self.filename = utils.create_csv_file(self.data_folder)

        # Header schreiben
        with open(self.filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Zeit", "U", "SOC"] + [f"{i + 1}.Z" for i in range(13)])

        ani = FuncAnimation(self.fig, self.update_plot, interval=settings.UPDATE_INTERVAL_MS, blit=False)
        plt.show()
