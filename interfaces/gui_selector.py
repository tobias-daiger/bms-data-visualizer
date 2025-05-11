import tkinter as tk
from tkinter import messagebox
from core.plotting.live_plotter import LivePlot
from core.plotting.live_reader import terminal_gui_mode
from interfaces.com_selector import get_available_ports
from core.data_source import serial_source
from interfaces.plot_selector import CSVPlotSelector
from PIL import Image, ImageTk
import os
from core.plotting.ip_plotter import IPLoggerPlot


class BMSGuiSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("BMS Plotter")
        self.mode = None
        self.selected_port = None
        self.selected_graphs = []
        self.root.geometry("500x900")
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
        tk.Button(self.root, text="IP Logger", width=30, command=self.select_ip_logger).pack(pady=5)
        tk.Button(self.root, text="CSV-Plotter", width=30, command=self.select_csv_plot).pack(pady=5)

        self.load_image()
        self.root.mainloop()

    def select_terminal(self):
        self.mode = "terminal"
        self.show_port_selection()

    def select_simulation(self):
        self.mode = "simulation"
        self.show_graph_selection()

    def select_real(self):
        self.mode = "real"
        self.show_port_selection()

    def select_ip_logger(self):
        self.mode = "ip_logger"
        self.show_graph_selection(skip_port=True)

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
            tk.Button(self.root, text=port, width=30,
                      command=lambda p=port: self.set_port_and_continue(p)).pack(pady=3)

        back_button = tk.Button(self.root, text="Zurück", width=30,
                                command=self.show_mode_selection)
        back_button.pack(pady=10)

    def set_port_and_continue(self, port):
        self.selected_port = port
        if self.mode == "terminal":
            self.root.destroy()
            terminal_gui_mode(self.selected_port)
        else:
            self.show_graph_selection(skip_port=True)  # <-- WICHTIG: skip_port=True

    def show_graph_selection(self, skip_port=False):
        if not skip_port and self.mode in ["real", "terminal"]:
            self.show_port_selection()
            return

        self.clear_window()
        self.add_header()

        tk.Label(self.root, text="Welche Daten anzeigen?", font=("Arial", 14)).pack(pady=10)

        self.graph_vars = {
            "U": tk.BooleanVar(),
            "SOC": tk.BooleanVar(),
            "current": tk.BooleanVar(),
        }
        for i in range(1, 14):
            self.graph_vars[f"Z{i}"] = tk.BooleanVar()

        self.graph_vars["max_cell_voltage"] = tk.BooleanVar()
        self.graph_vars["min_cell_voltage"] = tk.BooleanVar()
        self.graph_vars["max_temp"] = tk.BooleanVar()
        self.graph_vars["min_temp"] = tk.BooleanVar()
        self.graph_vars["avg_temp"] = tk.BooleanVar()

        for key, var in self.graph_vars.items():
            label = "Gesamtspannung (U)" if key == "U" else \
                "SOC (%)" if key == "SOC" else \
                    "Strom (A)" if key == "current" else \
                        f"{key}. Zellspannung" if key.startswith("Z") else \
                            f"{key.replace('_', ' ').title()}"
            tk.Checkbutton(self.root, text=label, variable=var).pack(pady=2)

        self.show_alarms_var = tk.BooleanVar()
        tk.Checkbutton(self.root,
                       text="Alarme anzeigen (Spannung/Temperatur)",
                       variable=self.show_alarms_var).pack(pady=10)

        tk.Button(self.root, text="Weiter", width=30,
                  command=self.start_plot).pack(pady=10)
        back_button = tk.Button(self.root, text="Zurück", width=30,
                                command=self.show_mode_selection)
        back_button.pack(pady=10)

    def start_plot(self):
        self.selected_graphs = [key for key, var in self.graph_vars.items() if var.get()]

        if not self.selected_graphs:
            messagebox.showerror("Fehler", "Es wurde keine Datenquelle ausgewählt.")
            return

        try:
            if self.mode == "ip_logger":
                plotter = IPLoggerPlot(self.selected_graphs)
            else:
                plotter = LivePlot(
                    selected_graphs=self.selected_graphs,
                    show_alarms=self.show_alarms_var.get()
                )

                if self.mode == "real":
                    plotter.port = serial_source.open_serial_port(self.selected_port)
                    if not plotter.port:
                        messagebox.showerror("Fehler", f"Konnte {self.selected_port} nicht öffnen!")
                        return

            self.root.destroy()
            plotter.run()

        except Exception as e:
            messagebox.showerror("Kritischer Fehler", f"Unerwarteter Fehler:\n{str(e)}")
            self.root.destroy()


if __name__ == "__main__":
    BMSGuiSelector()
