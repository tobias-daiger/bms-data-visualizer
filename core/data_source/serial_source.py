import serial
import re
import datetime
import serial.tools.list_ports
from core.data_source.base_source import DataSource

class SerialSource(DataSource):
    def __init__(self, port=None, baudrate=9600, timeout=1):
        if port is None:
            port = self.select_port()  # Wenn kein Port angegeben wird, den Port auswählen
        self.port = serial.Serial(port, baudrate, timeout=timeout)

    def select_port(self):
        """Liste alle verfügbaren COM-Ports und lass den Benutzer einen auswählen"""
        ports = serial.tools.list_ports.comports()
        print("Verfügbare COM-Ports:")
        for idx, p in enumerate(ports):
            print(f"{idx + 1}: {p.device}")

        while True:
            try:
                port_select = int(input("Wählen Sie den COM-Port (Nummer): ")) - 1
                if port_select >= 0 and port_select < len(ports):
                    selected_port = ports[port_select].device
                    print(f"Verbindung zu {selected_port} wird hergestellt...")
                    return selected_port
                else:
                    print("Ungültige Auswahl, bitte wählen Sie erneut.")
            except ValueError:
                print("Ungültige Eingabe, bitte geben Sie eine Zahl ein.")

    def read_voltage(self):
        """Liest die Spannung von einem angeschlossenen Gerät über die serielle Verbindung"""
        try:
            line = self.port.readline().decode('utf-8').strip()
            match = re.search(r"1\.Z:\s*([\d.]+)", line)
            if match:
                voltage = float(match.group(1))
                now = datetime.datetime.now()
                print(f"Empfangen: 1.Z: {voltage}V um {now.strftime('%H:%M:%S')}")
                return now, voltage
        except Exception as e:
            print(f"Fehler beim Lesen vom COM-Port: {e}")
        return None, None
