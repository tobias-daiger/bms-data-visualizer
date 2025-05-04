import datetime
import csv
import threading
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
import tkinter as tk
from config import settings
from core.data_source import serial_source, simulated_source
from core import utils


# Status-Tracker für geöffnete Alarmfenster
open_alarms = {
    "min_voltage": False,
    "max_voltage": False,
    "min_temp": False,
    "max_temp": False
}

def show_alarm_popup(message, alarm_type):
    if open_alarms.get(alarm_type, False):
        return  # Fenster ist bereits offen

    open_alarms[alarm_type] = True

    def run_popup():
        popup = tk.Tk()
        popup.title("Alarm")
        popup.protocol("WM_DELETE_WINDOW", lambda: (popup.destroy(), release_alarm(alarm_type)))

        label = tk.Label(popup, text=message, fg="red", font=("Helvetica", 14))
        label.pack(padx=20, pady=20)
        ok_button = tk.Button(popup, text="OK", command=lambda: (popup.destroy(), release_alarm(alarm_type)))
        ok_button.pack(pady=(0, 20))
        popup.mainloop()

    threading.Thread(target=run_popup, daemon=True).start()

def release_alarm(alarm_type):
    open_alarms[alarm_type] = False


class LivePlot:
    def __init__(self, selected_graphs, show_alarms):
        self.timestamps = []
        self.values = {key: [] for key in selected_graphs}
        self.filename = ""
        self.port = None
        self.simulation = False
        self.selected_graphs = selected_graphs
        self.show_alarms = show_alarms  # Neues Feature zur Steuerung der Alarmanzeige
        self.data_folder = utils.ensure_data_folder()

        self.fig, self.ax = plt.subplots(figsize=(12, 6), dpi=100)
        self.ax.set_xlabel("Zeit")
        self.ax.set_ylabel("Wert")
        self.ax.grid()
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

        self.lines = {}

    def check_alarms(self, data):
        if not self.show_alarms:  # Wenn Alarme nicht angezeigt werden sollen, beenden
            return

        min_voltage = data.get("min_cell_voltage")
        max_voltage = data.get("max_cell_voltage")
        min_temp = data.get("min_temp")
        max_temp = data.get("max_temp")

        if min_voltage is not None and min_voltage < settings.MIN_CELL_VOLTAGE:
            show_alarm_popup(f"ALARM: Zellenspannung unter Minimum! ({min_voltage:.2f} V)", "min_voltage")

        if max_voltage is not None and max_voltage > settings.MAX_CELL_VOLTAGE:
            show_alarm_popup(f"ALARM: Zellenspannung über Maximum! ({max_voltage:.2f} V)", "max_voltage")

        if min_temp is not None and min_temp < settings.MIN_TEMPERATURE:
            show_alarm_popup(f"ALARM: Temperatur unter Minimum! ({min_temp:.2f} °C)", "min_temp")

        if max_temp is not None and max_temp > settings.MAX_TEMPERATURE:
            show_alarm_popup(f"ALARM: Temperatur über Maximum! ({max_temp:.2f} °C)", "max_temp")

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

        self.check_alarms(data)

        row = [now.strftime("%H:%M:%S"), data["U"], data["SOC"], data["current"]] + data["cells"] + \
              [data.get("max_cell_voltage", ""), data.get("min_cell_voltage", ""),
               data.get("max_temp", ""), data.get("min_temp", ""), data.get("avg_temp", "")]
        with open(self.filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(row)

        self.timestamps.append(now)

        for key in self.selected_graphs:
            if key == "U":
                value = data["U"]
                label = "Gesamtspannung (U)"
            elif key == "SOC":
                value = data["SOC"]
                label = "SOC (%)"
            elif key == "current":
                value = data["current"]
                label = "Strom (A)"
            elif key.startswith("Z"):
                index = int(key[1:]) - 1
                if 0 <= index < len(data["cells"]):
                    value = data["cells"][index]
                    label = f"{key}. Zellspannung (V)"
                else:
                    continue
            elif key == "max_cell_voltage":
                value = data.get("max_cell_voltage", "")
                label = "Max. Zellenspannung (V)"
            elif key == "min_cell_voltage":
                value = data.get("min_cell_voltage", "")
                label = "Min. Zellenspannung (V)"
            elif key == "max_temp":
                value = data.get("max_temp", "")
                label = "Max. Temperatur (°C)"
            elif key == "min_temp":
                value = data.get("min_temp", "")
                label = "Min. Temperatur (°C)"
            elif key == "avg_temp":
                value = data.get("avg_temp", "")
                label = "Durchschnittstemperatur (°C)"
            else:
                continue

            if key not in self.lines:
                self.lines[key], = self.ax.plot([], [], label=label)
            self.values[key].append(value)
            self.lines[key].set_data(self.timestamps, self.values[key])

        self.ax.relim()
        self.ax.autoscale_view()
        self.fig.autofmt_xdate()
        self.ax.legend(loc='upper right')
        return list(self.lines.values())

    def run(self):
        self.filename = utils.create_csv_file(self.data_folder)

        with open(self.filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Zeit", "U", "SOC", "Strom"] + [f"{i + 1}.Z" for i in range(13)] +
                            ["Max. Zellenspannung", "Min. Zellenspannung", "Max. Temp", "Min. Temp", "Durchschnittstemperatur"])

        ani = FuncAnimation(self.fig, self.update_plot, interval=settings.UPDATE_INTERVAL_MS, blit=False)
        plt.show()
