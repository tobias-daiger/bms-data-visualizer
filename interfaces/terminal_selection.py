from core.data_source import serial_source
from core.plotting.live_reader import terminal_gui_mode
from interfaces.com_selector import choose_serial_port


def handle_user_selection(live_plot):
    choice = input("Gib 7 für Terminal-GUI-Ausgabe, 8 für Simulation oder 9 für realen COM-Port mit Plot ein: ")

    if choice == "7":
        selected_port = choose_serial_port()
        if selected_port:
            terminal_gui_mode(selected_port)
        return False  # Kein Plot, Terminal-Modus

    elif choice == "8":
        live_plot.simulation = True
        print("Simulation gestartet.")

    elif choice == "9":
        selected_port = choose_serial_port()
        if not selected_port:
            return False
        port = serial_source.open_serial_port(selected_port)
        if not port:
            return False
        live_plot.selected_port = selected_port
        live_plot.port = port
        print(f"Verbindung zu {selected_port} hergestellt.")

    else:
        print("Ungültige Eingabe. Beende...")
        return False

    print("Welche Daten sollen angezeigt werden?")
    print("1 = Gesamtspannung (U)")
    print("2 = SOC (%)")
    print("3 = Zellspannung 1 (1.Z)")
    try:
        data_type = int(input("Auswahl: "))
        if data_type not in [1, 2, 3]:
            raise ValueError
        live_plot.data_type = data_type
    except:
        print("Ungültige Auswahl.")
        return False

    return True  # Plot starten
