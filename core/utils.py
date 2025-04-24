import os
import datetime
import csv
import re
import random

def ensure_data_folder():
    folder = os.path.join(os.getcwd(), "data")
    os.makedirs(folder, exist_ok=True)
    return folder

def create_csv_file(data_folder):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(data_folder, f"messung_{timestamp}.csv")
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Zeit", "Wert"])
    print(f"CSV-Datei wird gespeichert als: {filename}")
    return filename

def parse_data_line(line, data_type):
    try:
        u_match = re.search(r"U:\s*([\d.]+)\s*V", line)
        soc_match = re.search(r"SOC:\s*([\d.]+)\s*%", line)
        z1_match = re.search(r"1\.Z:\s*([\d.]+)\s*V", line)

        if data_type == 1 and u_match:
            return float(u_match.group(1))
        elif data_type == 2 and soc_match:
            return float(soc_match.group(1))
        elif data_type == 3 and z1_match:
            return float(z1_match.group(1))
    except:
        pass
    return None

def simulate_data(data_type):
    pack_voltage = round(random.uniform(49.0, 50.0), 2)
    soc = round(random.uniform(80.0, 90.0), 1)
    cell_voltages = [round(random.uniform(3.900, 4.100), 3) for _ in range(13)]

    if data_type == 1:
        return pack_voltage
    elif data_type == 2:
        return soc
    elif data_type == 3:
        return cell_voltages[0]
    return 0
