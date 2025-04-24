import serial
import time
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
import random
import os
import csv
import re
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import sys

class LivePlot:
    def __init__(self):
        self.timestamps = []
        self.values = []
        self.filename = ""
        self.port = None
        self.simulation = False
        self.data_type = 1  # 1=Spannung, 2=SOC, 3=Zelle 1
        self.terminal_running = False

        self.data_folder = os.path.join(os.getcwd(), "data")
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)

        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], "-", label="Messwert")
        self.ax.set_xlabel("Zeit")
        self.ax.set_ylabel("Wert")
        self.ax.grid()
        self.ax.legend()
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

    def create_csv_file(self):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.filename = os.path.join(self.data_folder, f"messung_{timestamp}.csv")

        with open(self.filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Zeit", "Wert"])
        print(f"CSV-Datei wird gespeichert als: {self.filename}")

    def parse_line(self, line):
        try:
            u_match = re.search(r"U:\s*([\d.]+)\s*V", line)
            soc_match = re.search(r"SOC:\s*([\d.]+)\s*%", line)
            z1_match = re.search(r"1\.Z:\s*([\d.]+)\s*V", line)

            if self.data_type == 1 and u_match:
                return float(u_match.group(1))
            elif self.data_type == 2 and soc_match:
                return float(soc_match.group(1))
            elif self.data_type == 3 and z1_match:
                return float(z1_match.group(1))
        except:
            pass
        return None

    def simulate_data(self):
        pack_voltage = round(random.uniform(49.0, 50.0), 2)
        soc = round(random.uniform(80.0, 90.0), 1)
        cell_voltages = [round(random.uniform(3.900, 4.100), 3) for _ in range(13)]

        if self.data_type == 1:
            return pack_voltage
        elif self.data_type == 2:
            return soc
        elif self.data_type == 3:
            return cell_voltages[0]
        return 0

    def update_plot(self, frame):
        now = datetime.datetime.now()

        if self.simulation:
            value = self.simulate_data()
            print(f"Simulierter Wert: {value} um {now.strftime('%H:%M:%S')}")
        else:
            try:
                line = self.port.readline().decode('utf-8', errors='ignore').strip()
                print(f"Empfangene Zeile: {line}")
                value = self.parse_line(line)
                if value is None:
                    return
            except Exception as e:
                print(f"Fehler beim Lesen von der seriellen Schnittstelle: {e}")
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

    def terminal_gui_mode(self):
        def read_serial():
            while self.terminal_running:
                try:
                    line = self.port.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        text_widget.insert(tk.END, f"{line}\n")
                        text_widget.see(tk.END)
                except Exception as e:
                    text_widget.insert(tk.END, f"Fehler: {e}\n")
                    break

        def on_close():
            self.terminal_running = False
            root.destroy()
            sys.exit(0)  # Beendet das gesamte Programm sauber

        print("Starte Terminal-GUI-Ausgabe von COM4...")
        try:
            self.port = serial.Serial('COM4', 9600, timeout=1)
        except Exception as e:
            print(f"Fehler beim Öffnen von COM4: {e}")
            return

        root = tk.Tk()
        root.title("COM4 Terminal-Ausgabe")
        root.geometry("600x400")
        root.protocol("WM_DELETE_WINDOW", on_close)

        text_widget = ScrolledText(root, wrap=tk.WORD)
        text_widget.pack(expand=True, fill="both")

        self.terminal_running = True
        thread = threading.Thread(target=read_serial, daemon=True)
        thread.start()

        root.mainloop()

    def run(self):
        choice = input("Gib 7 für Terminal-GUI-Ausgabe, 8 für Simulation oder 9 für realen COM-Port mit Plot ein: ")
        if choice == "7":
            self.terminal_gui_mode()
            return  # sys.exit wird in der GUI selbst aufgerufen
        elif choice == "8":
            self.simulation = True
            print("Simulation gestartet.")
        elif choice == "9":
            try:
                self.port = serial.Serial('COM4', 9600, timeout=1)
                print("Verbindung zu COM4 hergestellt.")
            except Exception as e:
                print(f"Fehler beim Öffnen von COM4: {e}")
                return
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

        if self.data_type == 1:
            self.ax.set_ylabel("Spannung (V)")
            self.line.set_label("Gesamtspannung (U)")
        elif self.data_type == 2:
            self.ax.set_ylabel("SOC (%)")
            self.line.set_label("SOC")
        elif self.data_type == 3:
            self.ax.set_ylabel("Zellspannung 1 (V)")
            self.line.set_label("1.Z")

        self.ax.legend()
        self.create_csv_file()
        ani = FuncAnimation(self.fig, self.update_plot, interval=500, blit=False)
        plt.show()

if __name__ == "__main__":
    plotter = LivePlot()
    plotter.run()
