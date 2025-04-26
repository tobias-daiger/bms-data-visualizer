import random

def simulate_full_data():
    u = random.uniform(48.0, 52.0)  # Gesamtspannung
    soc = random.uniform(20.0, 100.0)  # Ladezustand
    current = random.uniform(-10.0, 10.0)  # Strom (positiv für Laden, negativ für Entladen)

    cells = [random.uniform(3.6, 4.2) for _ in range(13)]  # 13 Zellen
    max_cell_voltage = max(cells)
    min_cell_voltage = min(cells)

    # Temperaturwerte simulieren
    temperatures = [random.uniform(20.0, 50.0) for _ in range(13)]
    max_temp = max(temperatures)
    min_temp = min(temperatures)
    avg_temp = sum(temperatures) / len(temperatures)

    data = {
        "U": round(u, 2),
        "SOC": round(soc, 1),
        "current": round(current, 2),
        "cells": [round(cell, 3) for cell in cells],
        "max_cell_voltage": round(max_cell_voltage, 3),
        "min_cell_voltage": round(min_cell_voltage, 3),
        "max_temp": round(max_temp, 1),
        "min_temp": round(min_temp, 1),
        "avg_temp": round(avg_temp, 1)
    }

    return data
