import random

def simulate_data(data_type):
    if data_type == 1:
        return round(random.uniform(49.0, 50.0), 2)  # Spannung
    elif data_type == 2:
        return round(random.uniform(80.0, 90.0), 1)  # SOC
    elif data_type == 3:
        return round(random.uniform(3.900, 4.100), 3)  # Zellspannung 1
    return 0
