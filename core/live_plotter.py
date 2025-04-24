import serial
import time
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.animation import FuncAnimation
import random
import os
import csv

class LivePlot:
    def __init__(self):
        self.timestamps = []  # Liste für Zeitstempel
        self.percentages = []  # Liste für Prozentwerte
        self.filename = ""
        self.port = None
        self.simulation = False

        # Pfad zum Datenordner im Projektverzeichnis (PyCharm-Projekt)
        self.data_folder = os.path.join(os.getcwd(), "data")
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)  # Ordner erstellen, falls er nicht existiert

        # Matplotlib Figure und Achsen
        self.fig, self.ax = plt.subplots()
        self.line, = self.ax.plot([], [], "-", label="Prozent")
        self.ax.set_xlabel("Zeit")
        self.ax.set_ylabel("Prozent (%)")
        self.ax.grid()
        self.ax.legend()
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

    def create_csv_file(self):
        # Aktuelles Datum und Uhrzeit für Dateinamen
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.filename = os.path.join(self.data_folder, f"simulation_{timestamp}.csv")

        # CSV-Datei erstellen und Header schreiben
        with open(self.filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Zeit", "Prozent (%)"])
        print(f"CSV-Datei wird gespeichert als: {self.filename}")

    def update_plot(self, frame):
        # Hier erfolgt das Update der Plot-Daten
        if self.simulation:
            # Zufälliger Wert zwischen 0 und 100 für die Simulation
            percentage = round(random.uniform(0, 100), 2)
            now = datetime.datetime.now()
            print(f"Simulierter Wert: {percentage}% um {now.strftime('%H:%M:%S')}")
        else:
            try:
                line = self.port.readline().decode('utf-8').strip()  # Liest die nächste Zeile vom COM-Port
                print(f"Empfangene Zeile: {line}")  # Debug-Ausgabe
                # Annahme: Die empfangenen Daten sind Prozentwerte zwischen 0 und 100
                percentage = float(line)
                now = datetime.datetime.now()
                print(f"Empfangen: {percentage}% um {now.strftime('%H:%M:%S')}")
            except Exception as e:
                print(f"Fehler beim Lesen von der seriellen Schnittstelle: {e}")
                return

        # Daten in die Listen einfügen
        self.timestamps.append(now)
        self.percentages.append(percentage)

        # Daten in CSV-Datei schreiben
        with open(self.filename, mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([now.strftime("%H:%M:%S"), percentage])

        # Plotdaten aktualisieren
        self.line.set_data(self.timestamps, self.percentages)
        self.ax.relim()  # Achsenlimits neu berechnen
        self.ax.autoscale_view()  # Ansichtsbereich anpassen
        self.fig.autofmt_xdate()  # Zeitstempel formatieren
        return self.line,

    def run(self):
        # Wählen, ob Simulation oder echte Daten verwendet werden
        choice = input("Gib 8 für Simulation oder 9 für realen COM-Port ein: ")
        if choice == "8":
            self.simulation = True
            print("Simulation gestartet.")
        elif choice == "9":
            try:
                self.port = serial.Serial('COM4', 9600, timeout=1)  # COM4 anstelle von COM8
                print("Verbindung zu COM4 hergestellt.")
            except Exception as e:
                print(f"Fehler beim Öffnen von COM4: {e}")
                return
        else:
            print("Ungültige Eingabe. Beende...")
            return

        # CSV-Datei erstellen
        self.create_csv_file()

        # Funktionsanimation starten (interval 500ms)
        ani = FuncAnimation(self.fig, self.update_plot, interval=500, blit=False)
        plt.show()  # Plot-Fenster anzeigen

if __name__ == "__main__":
    plotter = LivePlot()
    plotter.run()
