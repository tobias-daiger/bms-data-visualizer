import serial.tools.list_ports

def choose_serial_port():
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
