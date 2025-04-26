import os
import datetime
import re

def ensure_data_folder():
    folder = "data"
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder

def create_csv_file(folder):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(folder, f"messung_{timestamp}.csv")
    return filename

def parse_full_data_line(line):
    # Beispiel: U: 49.13 V | SOC: 83.7 % | 1.Z: 3.986 V | ... | 13.Z: 3.904 V
    try:
        data = {}

        u_match = re.search(r"U:\s*([\d.]+)\s*V", line)
        soc_match = re.search(r"SOC:\s*([\d.]+)\s*%", line)
        cell_matches = re.findall(r"(\d+)\.Z:\s*([\d.]+)\s*V", line)

        if not (u_match and soc_match and cell_matches):
            return None

        data["U"] = float(u_match.group(1))
        data["SOC"] = float(soc_match.group(1))
        data["cells"] = [0.0] * 13

        for idx, value in cell_matches:
            index = int(idx) - 1  # 0-basiert
            if 0 <= index < 13:
                data["cells"][index] = float(value)

        return data

    except Exception as e:
        print(f"Fehler beim Parsen der Zeile: {e}")
        return None
