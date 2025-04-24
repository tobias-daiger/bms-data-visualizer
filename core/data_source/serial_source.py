import serial
from config import settings

def open_serial_port(port_name):
    try:
        return serial.Serial(port_name, settings.DEFAULT_BAUDRATE, timeout=settings.DEFAULT_TIMEOUT)
    except Exception as e:
        print(f"Fehler beim Öffnen von {port_name}: {e}")
        return None

def read_serial_line(serial_port):
    try:
        return serial_port.readline().decode('utf-8', errors='ignore').strip()
    except Exception as e:
        print(f"Fehler beim Lesen: {e}")
        return None
