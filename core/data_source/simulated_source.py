import random

def simulate_full_data():
    u = random.uniform(48.0, 52.0)  # Gesamtspannung
    soc = random.uniform(20.0, 100.0)  # Ladezustand

    cells = [random.uniform(3.6, 4.2) for _ in range(13)]  # 13 Zellen

    data = {
        "U": round(u, 2),
        "SOC": round(soc, 1),
        "cells": [round(cell, 3) for cell in cells]
    }

    return data
