from core.plotting.live_plotter import LivePlot
from core.data_source.ip_source import IPLoggerSource
import matplotlib.dates as mdates
from datetime import datetime
import matplotlib.pyplot as plt
from core import utils
from matplotlib.animation import FuncAnimation
import csv

class IPLoggerPlot(LivePlot):
    def __init__(self, selected_graphs):
        super().__init__(selected_graphs, show_alarms=False)
        self.data_folder = utils.ensure_data_folder()
        self.source = IPLoggerSource()
        self._configure_plot()
        self._init_lines()
        self.fig.canvas.manager.set_window_title('IP Logger')
        self.csv_header_written = False
        self.filename = None

    def _configure_plot(self):
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax.set_title("Live-Daten vom BMS (IP)", pad=20)
        self.ax.grid(True, linestyle='--', alpha=0.6)
        self.fig.tight_layout()

    def _init_lines(self):
        label_mapping = {
            "U": "Gesamtspannung (V)",
            "SOC": "Ladezustand (%)",
            "current": "Strom (A)",
            "max_cell_voltage": "Max. Zelle (V)",
            "min_cell_voltage": "Min. Zelle (V)",
            "max_temp": "Max. Temp (°C)",
            "min_temp": "Min. Temp (°C)",
            "avg_temp": "Ø Temp (°C)"
        }
        for key in self.selected_graphs:
            label = label_mapping.get(key, key.replace('_', ' ').title())
            if key.startswith('Z'):
                label = f"Zelle {key[1:]} (V)"
            if key not in self.lines:
                self.lines[key], = self.ax.plot([], [], label=label)

    def update_plot(self, frame):
        raw_data = self.source.fetch_data()
        now = datetime.now()

        if raw_data:
            self._process_data(now, raw_data)
            self._update_plot_lines()
            self._write_csv(now, raw_data)

        return list(self.lines.values())

    def _process_data(self, timestamp, data):
        self.timestamps.append(timestamp)
        for key in self.selected_graphs:
            if key.startswith('Z'):
                cell_index = int(key[1:]) - 1
                self.values[key].append(
                    data['cells'][cell_index]
                    if 0 <= cell_index < len(data.get('cells', []))
                    else 0
                )
            else:
                self.values[key].append(data.get(key, 0))

    def _update_plot_lines(self):
        for key in self.selected_graphs:
            if key in self.lines:
                self.lines[key].set_data(self.timestamps, self.values[key])
        self.ax.relim()
        self.ax.autoscale_view()
        self.ax.legend(loc='upper right')
        self.ax.grid(True, linestyle='--', alpha=0.6)
        plt.draw_all()

    def _write_csv(self, now, raw_data):
        # Schreibe Header nur einmal
        if not self.csv_header_written:
            with open(self.filename, mode="w", newline="") as file:
                writer = csv.writer(file)
                header = ["Zeit"]
                # 13 Zellspannungen
                for i in range(1, 14):
                    header.append(f"{i}.Z")
                header += [
                    "U", "SOC", "Strom",
                    "Max. Zellenspannung", "Min. Zellenspannung",
                    "Max. Temp", "Min. Temp", "Durchschnittstemperatur"
                ]
                writer.writerow(header)
            self.csv_header_written = True

        # Schreibe Werte in fester Reihenfolge
        with open(self.filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            row = [now.strftime("%H:%M:%S")]
            # Zellspannungen
            cells = raw_data.get('cells', [])
            for i in range(13):
                row.append(cells[i] if i < len(cells) else "")
            # Restliche Werte
            row.append(raw_data.get("U", ""))
            row.append(raw_data.get("SOC", ""))
            row.append(raw_data.get("current", ""))
            row.append(raw_data.get("max_cell_voltage", ""))
            row.append(raw_data.get("min_cell_voltage", ""))
            row.append(raw_data.get("max_temp", ""))
            row.append(raw_data.get("min_temp", ""))
            row.append(raw_data.get("avg_temp", ""))
            writer.writerow(row)

    def run(self):
        self.filename = utils.create_csv_file(self.data_folder)
        self.csv_header_written = False
        ani = FuncAnimation(
            self.fig,
            self.update_plot,
            interval=1000,  # 1 Sekunde
            blit=False,
            cache_frame_data=False
        )
        plt.show()
