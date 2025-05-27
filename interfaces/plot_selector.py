import tkinter as tk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

class CSVPlotSelector:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CSV Plotter")
        self.root.geometry("500x700")
        self.data = None
        self.columns = []

    def load_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.data = pd.read_csv(file_path)
            self.columns = list(self.data.columns)[1:]  # Erste Spalte ist Zeit
            self.show_column_selection()

    def show_column_selection(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Wähle Daten zum Plotten", font=("Arial", 14)).pack(pady=10)

        self.var_dict = {}
        for col in self.columns:
            var = tk.BooleanVar()
            chk = tk.Checkbutton(self.root, text=col, variable=var)
            chk.pack(anchor="w", padx=20)
            self.var_dict[col] = var

        plot_button = tk.Button(self.root, text="Plotten", width=30, command=self.plot_selected_columns)
        plot_button.pack(pady=20)

    def plot_selected_columns(self):
        selected_columns = [col for col, var in self.var_dict.items() if var.get()]
        if not selected_columns:
            return  # Keine Auswahl getroffen

        # Gruppiere wie im Live-Plotter
        cell_keys = [col for col in selected_columns if col.endswith('.Z') or 'Zellenspannung' in col]
        if "Max. Zellenspannung" in selected_columns:
            cell_keys.append("Max. Zellenspannung")
        if "Min. Zellenspannung" in selected_columns:
            cell_keys.append("Min. Zellenspannung")
        temp_keys = [col for col in selected_columns if "Temp" in col]
        other_keys = [col for col in selected_columns if col in ["Strom", "U", "SOC"]]

        nplots = sum([bool(cell_keys), bool(temp_keys), bool(other_keys)])
        fig, axes = plt.subplots(nplots, 1, figsize=(10, 4 * nplots), constrained_layout=True)
        if nplots == 1:
            axes = [axes]
        plot_map = {}
        idx = 0
        if cell_keys:
            plot_map['cells'] = idx
            idx += 1
        if temp_keys:
            plot_map['temps'] = idx
            idx += 1
        if other_keys:
            plot_map['others'] = idx

        # Zeit als datetime parsen
        zeit = pd.to_datetime(self.data["Zeit"], format="%H:%M:%S")
        dauer = (zeit.iloc[-1] - zeit.iloc[0]).total_seconds() / 60  # Minuten

        # Tick-Reduktion je nach Messdauer
        if dauer > 180:
            locator = mdates.HourLocator(interval=1)
            formatter = mdates.DateFormatter('%H:%M')
        elif dauer > 60:
            locator = mdates.MinuteLocator(interval=10)
            formatter = mdates.DateFormatter('%H:%M')
        elif dauer > 30:
            locator = mdates.MinuteLocator(interval=5)
            formatter = mdates.DateFormatter('%H:%M')
        elif dauer > 10:
            locator = mdates.MinuteLocator(interval=1)
            formatter = mdates.DateFormatter('%H:%M')
        else:
            locator = mdates.SecondLocator(interval=30)
            formatter = mdates.DateFormatter('%H:%M:%S')

        # Zellspannungen
        if cell_keys:
            ax = axes[plot_map['cells']]
            for col in cell_keys:
                ax.plot(zeit, self.data[col], label=col)
            ax.set_title('Zellspannungen')
            ax.set_xlabel('Zeit')
            ax.set_ylabel('Spannung (V)')
            ax.set_ylim(2.7, 4.2)
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend(loc='lower left')
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(formatter)
            plt.setp(ax.get_xticklabels(), rotation=45)
        # Temperaturen
        if temp_keys:
            ax = axes[plot_map['temps']]
            for col in temp_keys:
                ax.plot(zeit, self.data[col], label=col)
            ax.set_title('Temperaturen')
            ax.set_xlabel('Zeit')
            ax.set_ylabel('Temperatur (°C)')
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend(loc='lower left')
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(formatter)
            plt.setp(ax.get_xticklabels(), rotation=45)
        # Strom, U, SOC
        if other_keys:
            ax = axes[plot_map['others']]
            for col in other_keys:
                # Für Strom: ×100 multiplizieren wie im Live-Plotter
                if col == "Strom":
                    ax.plot(zeit, self.data[col] * 100, label=col + " (x100)")
                else:
                    ax.plot(zeit, self.data[col], label=col)
            ax.set_title('Strom, Gesamtspannung, SOC')
            ax.set_xlabel('Zeit')
            ax.set_ylabel('Wert')
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend(loc='lower left')
            ax.xaxis.set_major_locator(locator)
            ax.xaxis.set_major_formatter(formatter)
            plt.setp(ax.get_xticklabels(), rotation=45)

        plt.show()

    def run(self):
        self.load_csv()
        self.root.mainloop()
