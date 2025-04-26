import tkinter as tk
from tkinter import messagebox, filedialog
from core.plotting.live_plotter import LivePlot
from core.plotting.live_reader import terminal_gui_mode
from interfaces.com_selector import get_available_ports
from core.data_source import serial_source
from interfaces.plot_selector import CSVPlotSelector
from PIL import Image, ImageTk
import os

class BMSGuiSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BMS Plotter")
        self.mode = None
        self.selected_port = None
        self.data_type = 1
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        self.show_mode_selection()

    def load_image(self):
        image_path = os.path.join("assets", "BMS2.jpg")
        try:
            img = Image.open(image_path)
            img = img.resize((450, 200))
            self.photo = ImageTk.PhotoImage(img)
            tk.Label(self.root, image=self.photo).pack(pady=10)
        except Exception as e:
            print(f"Bild konnte nicht geladen werden: {e}")

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def add_header(self):
        tk.Label(self.root, text="BMS Plotter", font=("Arial", 20, "bold")).pack(pady=10)

    def show_mode_selection(self):
        self.clear_window()
        self.add_header()

        tk.Label(self.root, text="Wähle Betriebsmodus", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="Terminal-Modus", width=30, command=self.select_terminal).pack(pady=5)
        tk.Button(self.root, text="Simulation", width=30, command=self.select_simulation).pack(pady=5)
        tk.Button(self.root, text="Live-Plotter", width=30, command=self.select_real).pack(pady=5)
        tk.Button(self.root, text="CSV-Plotter", width=30, command=self.select_csv_plot).pack(pady=5)

        self.load_image()
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

    def select_csv_plot(self):
        self.root.destroy()
        selector = CSVPlotSelector()
        selector.run()

    def show_port_selection(self):
        self.clear_window()
        self.add_header()

        ports = get_available_ports()
        if not ports:
            messagebox.showerror("Fehler", "Keine COM-Ports gefunden.")
            self.root.destroy()
            return

        tk.Label(self.root, text="Wähle COM-Port", font=("Arial", 14)).pack(pady=10)
        for port in ports:
            tk.Button(self.root, text=port, width=30, command=lambda p=port: self.set_port_and_continue(p)).pack(pady=3)

        # Add a Back button to go to mode selection
        back_button = tk.Button(self.root, text="Zurück", width=30, command=self.show_mode_selection)
        back_button.pack(pady=10)

    def set_port_and_continue(self, port):
        self.selected_port = port
        if self.mode == "terminal":
            self.root.destroy()
            terminal_gui_mode(self.selected_port)
        else:
            self.show_data_type_selection()

    def show_data_type_selection(self):
        self.clear_window()
        self.add_header()

        tk.Label(self.root, text="Welche Daten anzeigen?", font=("Arial", 14)).pack(pady=10)
        tk.Button(self.root, text="Gesamtspannung (U)", width=30, command=lambda: self.start_plot(1)).pack(pady=3)
        tk.Button(self.root, text="SOC (%)", width=30, command=lambda: self.start_plot(2)).pack(pady=3)
        for i in range(13):
            tk.Button(self.root, text=f"{i+1}. Zellspannung", width=30, command=lambda i=i: self.start_plot(i+3)).pack(pady=2)

        # Add a Back button to go back to port selection
        back_button = tk.Button(self.root, text="Zurück", width=30, command=self.show_port_selection)
        back_button.pack(pady=10)

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
