import serial.tools.list_ports

def get_available_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]
