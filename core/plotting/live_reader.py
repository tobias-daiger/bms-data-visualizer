import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import sys
from core.data_source import serial_source
from config import settings

def terminal_gui_mode(port_name):
    port = serial_source.open_serial_port(port_name)
    if not port:
        return

    def read_serial():
        while terminal_running[0]:
            line = serial_source.read_serial_line(port)
            if line:
                text_widget.insert(tk.END, f"{line}\n")
                text_widget.see(tk.END)

    def on_close():
        terminal_running[0] = False
        root.destroy()
        sys.exit(0)

    root = tk.Tk()
    root.title(f"{port_name} Terminal-Ausgabe")
    root.geometry("600x400")
    root.protocol("WM_DELETE_WINDOW", on_close)

    text_widget = ScrolledText(root, wrap=tk.WORD)
    text_widget.pack(expand=True, fill="both")

    terminal_running = [True]
    thread = threading.Thread(target=read_serial, daemon=True)
    thread.start()

    root.mainloop()
