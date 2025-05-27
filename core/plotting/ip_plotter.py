import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from matplotlib.animation import FuncAnimation
from core.plotting.live_plotter import LivePlot
from core.data_source.ip_source import IPLoggerSource
from core import utils
import csv

class IPLoggerPlot(LivePlot):
    def __init__(self, selected_graphs):
        super().__init__(selected_graphs, show_alarms=False)
        self.data_folder = utils.ensure_data_folder()
        self.source = IPLoggerSource()
        self.selected_graphs = selected_graphs
        self.timestamps = []
        self.values = {key: [] for key in selected_graphs}

        # Gruppierung
        self.cell_keys = [k for k in selected_graphs if k.startswith('Z')]
        if 'max_cell_voltage' in selected_graphs:
            self.cell_keys.append('max_cell_voltage')
        if 'min_cell_voltage' in selected_graphs:
            self.cell_keys.append('min_cell_voltage')
        self.temp_keys = [k for k in selected_graphs if k in ['max_temp', 'min_temp', 'avg_temp']]
        self.current_keys = [k for k in selected_graphs if k == 'current']
        self.voltage_soc_keys = [k for k in selected_graphs if k in ['U', 'SOC']]

        nplots = sum([bool(self.cell_keys), bool(self.temp_keys), bool(self.current_keys or self.voltage_soc_keys)])
        self.fig, self.axes = plt.subplots(nplots, 1, figsize=(10, 4 * nplots), constrained_layout=True)
        if nplots == 1:
            self.axes = [self.axes]
        self.plot_map = {}
        idx = 0
        if self.cell_keys:
            self.plot_map['cells'] = idx
            idx += 1
        if self.temp_keys:
            self.plot_map['temps'] = idx
            idx += 1
        if self.current_keys or self.voltage_soc_keys:
            self.plot_map['others'] = idx

        self.lines = {'cells': {}, 'temps': {}, 'others': {}}
        self.csv_header_written = False
        self.filename = None
        self._init_plots()
        self.fig.canvas.manager.set_window_title('IP Logger')

    def _init_plots(self):
        # Zellspannungen
        if self.cell_keys:
            ax = self.axes[self.plot_map['cells']]
            ax.set_title('Zellspannungen')
            ax.set_xlabel('Zeit')
            ax.set_ylabel('Spannung (V)')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.set_ylim(2.7, 4.2)
            ax.grid(True, linestyle='--', alpha=0.6)
            for k in self.cell_keys:
                self.lines['cells'][k], = ax.plot([], [], label=k)
            ax.legend(loc='lower left')
        # Temperaturen
        if self.temp_keys:
            ax = self.axes[self.plot_map['temps']]
            ax.set_title('Temperaturen')
            ax.set_xlabel('Zeit')
            ax.set_ylabel('Temperatur (°C)')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.grid(True, linestyle='--', alpha=0.6)
            for k in self.temp_keys:
                self.lines['temps'][k], = ax.plot([], [], label=k)
            ax.legend(loc='lower left')
        # Strom, U, SOC
        if self.current_keys or self.voltage_soc_keys:
            ax = self.axes[self.plot_map['others']]
            ax.set_title('Strom, Gesamtspannung, SOC')
            ax.set_xlabel('Zeit')
            ax.set_ylabel('Wert')
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            ax.grid(True, linestyle='--', alpha=0.6)
            for k in self.current_keys:
                self.lines['others'][k], = ax.plot([], [], label=k)
            for k in self.voltage_soc_keys:
                self.lines['others'][k], = ax.plot([], [], label=k)
            ax.legend(loc='lower left')

    def update_plot(self, frame):
        now = datetime.now()
        self.timestamps.append(now)
        raw_data = self.source.fetch_data()
        if not raw_data:
            return []

        for key in self.selected_graphs:
            if key.startswith('Z'):
                index = int(key[1:]) - 1
                self.values[key].append(raw_data['cells'][index] if 0 <= index < len(raw_data.get('cells', [])) else 0)
            elif key == 'current':
                # Live-Plot: Strom ×100
                original_value = raw_data.get(key, 0)
                self.values[key].append(original_value * 100)
            else:
                self.values[key].append(raw_data.get(key, 0))

        # Zellspannungen
        if self.cell_keys:
            ax = self.axes[self.plot_map['cells']]
            for k, line in self.lines['cells'].items():
                line.set_data(self.timestamps, self.values[k])
            ax.relim()
            ax.autoscale_view()
            ax.set_ylim(2.7, 4.2)
            ax.legend(loc='lower left')
        # Temperaturen
        if self.temp_keys:
            ax = self.axes[self.plot_map['temps']]
            for k, line in self.lines['temps'].items():
                line.set_data(self.timestamps, self.values[k])
            ax.relim()
            ax.autoscale_view()
            ax.legend(loc='lower left')
        # Strom, U, SOC
        if self.current_keys or self.voltage_soc_keys:
            ax = self.axes[self.plot_map['others']]
            for k, line in self.lines['others'].items():
                line.set_data(self.timestamps, self.values[k])
            ax.relim()
            ax.autoscale_view()
            ax.legend(loc='lower left')

        self._write_csv(now, raw_data)
        return []

    def _write_csv(self, now, raw_data):
        if not self.csv_header_written:
            with open(self.filename, mode="w", newline="") as file:
                writer = csv.writer(file)
                header = ["Zeit"]
                for i in range(1, 14):
                    header.append(f"{i}.Z")
                header += [
                    "U", "SOC", "Strom",
                    "Max. Zellenspannung", "Min. Zellenspannung",
                    "Max. Temp", "Min. Temp", "Durchschnittstemperatur"
                ]
                writer.writerow(header)
            self.csv_header_written = True
        with open(self.filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            row = [now.strftime("%H:%M:%S")]
            cells = raw_data.get('cells', [])
            for i in range(13):
                row.append(cells[i] if i < len(cells) else "")
            row.append(raw_data.get("U", ""))
            row.append(raw_data.get("SOC", ""))
            row.append(raw_data.get("current", ""))  # Originalwert in CSV!
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
            interval=1000,
            blit=False,
            cache_frame_data=False
        )
        plt.show()
