import tkinter as tk
from tkinter import filedialog
import pandas as pd
import matplotlib.pyplot as plt

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

        plt.figure(figsize=(10, 6))
        for col in selected_columns:
            plt.plot(self.data["Zeit"], self.data[col], label=col)

        plt.xlabel("Zeit")
        plt.ylabel("Wert")
        plt.title("Daten aus CSV")
        plt.grid()
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

    def run(self):
        self.load_csv()
        self.root.mainloop()
