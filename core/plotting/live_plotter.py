import datetime
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation

from config import settings
from core.data_source import serial_source, simulated_source
from core import utils
from core.plotting.live_reader import terminal_gui_mode


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

    def choose_serial_port(self):
        import serial.tools.list_ports
        ports = serial.tools.list_ports.comports()
        available_ports = [port.device for port in ports]
        if not available_ports:
            print("Keine COM-Ports gefunden.")
            return None

        print("Verfügbare COM-Ports:")
        for i, p in enumerate(available_ports, 1):
            print(f"{i}: {p}")

        while True:
            try:
                index = int(input("Wähle einen Port durch Eingabe der Zahl: "))
                if 1 <= index <= len(available_ports):
                    return available_ports[index - 1]
                else:
                    print("Ungültige Auswahl.")
            except:
                print("Bitte eine gültige Zahl eingeben.")

    def update_plot(self, frame):
        now = datetime.datetime.now()

        if self.simulation:
            value = simulated_source.simulate_data(self.data_type)
            print(f"Simulierter Wert: {value} um {now.strftime('%H:%M:%S')}")
        else:
            line = serial_source.read_serial_line(self.port)
            if line is None:
                return
            print(f"Empfangene Zeile: {line}")
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
        choice = input("Gib 7 für Terminal-GUI-Ausgabe, 8 für Simulation oder 9 für realen COM-Port mit Plot ein: ")
        if choice == "7":
            selected_port = self.choose_serial_port()
            if selected_port:
                terminal_gui_mode(selected_port)
            return
        elif choice == "8":
            self.simulation = True
            print("Simulation gestartet.")
        elif choice == "9":
            self.selected_port = self.choose_serial_port()
            if not self.selected_port:
                return
            self.port = serial_source.open_serial_port(self.selected_port)
            if not self.port:
                return
            print(f"Verbindung zu {self.selected_port} hergestellt.")
        else:
            print("Ungültige Eingabe. Beende...")
            return

        print("Welche Daten sollen angezeigt werden?")
        print("1 = Gesamtspannung (U)")
        print("2 = SOC (%)")
        print("3 = Zellspannung 1 (1.Z)")
        try:
            self.data_type = int(input("Auswahl: "))
            if self.data_type not in [1, 2, 3]:
                raise ValueError
        except:
            print("Ungültige Auswahl.")
            return

        y_labels = {1: "Spannung (V)", 2: "SOC (%)", 3: "Zellspannung 1 (V)"}
        legends = {1: "Gesamtspannung (U)", 2: "SOC", 3: "1.Z"}
        self.ax.set_ylabel(y_labels[self.data_type])
        self.line.set_label(legends[self.data_type])
        self.ax.legend()

        self.filename = utils.create_csv_file(self.data_folder)
        ani = FuncAnimation(self.fig, self.update_plot, interval=settings.UPDATE_INTERVAL_MS, blit=False)
        plt.show()
