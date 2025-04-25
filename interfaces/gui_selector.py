import tkinter as tk
from tkinter import messagebox
from core.plotting.live_plotter import LivePlot
from core.plotting.live_reader import terminal_gui_mode
from interfaces.com_selector import get_available_ports
from core.data_source import serial_source

class BMSGuiSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BMS Plotter")
        self.mode = None
        self.selected_port = None
        self.data_type = 1

        self.show_mode_selection()

    def show_mode_selection(self):
        tk.Label(self.root, text="Wähle Betriebsmodus", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Terminal-Modus (7)", width=30, command=self.select_terminal).pack(pady=5)
        tk.Button(self.root, text="Simulation (8)", width=30, command=self.select_simulation).pack(pady=5)
        tk.Button(self.root, text="Real-Daten Plot (9)", width=30, command=self.select_real).pack(pady=5)
        self.root.mainloop()

    def select_terminal(self):
        self.mode = "terminal"
        self.show_port_selection()

    def select_simulation(self):
        self.mode = "simulation"
        self.show_data_type_selection()

    def select_real(self):
        self.mode = "real"
        self.show_port_selection()

    def show_port_selection(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        ports = get_available_ports()
        if not ports:
            messagebox.showerror("Fehler", "Keine COM-Ports gefunden.")
            self.root.destroy()
            return

        tk.Label(self.root, text="Wähle COM-Port", font=("Arial", 14)).pack(pady=10)
        for port in ports:
            tk.Button(self.root, text=port, width=30, command=lambda p=port: self.set_port_and_continue(p)).pack(pady=3)

    def set_port_and_continue(self, port):
        self.selected_port = port
        if self.mode == "terminal":
            self.root.destroy()
            terminal_gui_mode(self.selected_port)
        else:
            self.show_data_type_selection()

    def show_data_type_selection(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Welche Daten anzeigen?", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="1 = Gesamtspannung (U)", width=30, command=lambda: self.start_plot(1)).pack(pady=3)
        tk.Button(self.root, text="2 = SOC (%)", width=30, command=lambda: self.start_plot(2)).pack(pady=3)
        tk.Button(self.root, text="3 = Zellspannung 1 (1.Z)", width=30, command=lambda: self.start_plot(3)).pack(pady=3)

    def start_plot(self, selected_type):
        self.data_type = selected_type
        self.root.destroy()

        plotter = LivePlot()
        plotter.data_type = self.data_type
        if self.mode == "simulation":
            plotter.simulation = True
        elif self.mode == "real":
            plotter.port = serial_source.open_serial_port(self.selected_port)
            if not plotter.port:
                return
        plotter.run()


if __name__ == "__main__":
    BMSGuiSelector()
