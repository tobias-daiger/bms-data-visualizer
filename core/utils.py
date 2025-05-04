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

def safe_float(value):
    """Versucht, einen Wert in einen float umzuwandeln und gibt None zurück, wenn dies fehlschlägt."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def parse_full_data_line(line):
    try:
        data = {}

        # Parsing der relevanten Daten
        u_match = re.search(r"U:\s*([\d.-]+)\s*V", line)  # angepasst, um auch negative Zahlen zu unterstützen
        soc_match = re.search(r"SOC:\s*([\d.-]+)\s*%", line)  # angepasst, um auch negative Zahlen zu unterstützen
        current_match = re.search(r"Strom:\s*([\d.-]+)\s*A", line)  # angepasst, um auch negative Zahlen zu unterstützen
        cell_matches = re.findall(r"(\d+)\.Z:\s*([\d.-]+)\s*V", line)  # angepasst, um auch negative Zahlen zu unterstützen
        max_cell_voltage_match = re.search(r"Max. Zellenspannung:\s*([\d.-]+)\s*V", line)  # angepasst
        min_cell_voltage_match = re.search(r"Min. Zellenspannung:\s*([\d.-]+)\s*V", line)  # angepasst
        max_temp_match = re.search(r"Max. Temp:\s*([\d.-]+)\s*°C", line)  # angepasst
        min_temp_match = re.search(r"Min. Temp:\s*([\d.-]+)\s*°C", line)  # angepasst
        avg_temp_match = re.search(r"Durchschnittstemperatur:\s*([\d.-]+)\s*°C", line)  # angepasst

        if not (u_match and soc_match and current_match and cell_matches):
            return None

        data["U"] = safe_float(u_match.group(1))
        data["SOC"] = safe_float(soc_match.group(1))
        data["current"] = safe_float(current_match.group(1))
        data["cells"] = [0.0] * 13

        for idx, value in cell_matches:
            index = int(idx) - 1  # 0-basiert
            if 0 <= index < 13:
                data["cells"][index] = safe_float(value)

        # Zusätzliche Daten
        if max_cell_voltage_match:
            data["max_cell_voltage"] = safe_float(max_cell_voltage_match.group(1))
        if min_cell_voltage_match:
            data["min_cell_voltage"] = safe_float(min_cell_voltage_match.group(1))
        if max_temp_match:
            data["max_temp"] = safe_float(max_temp_match.group(1))
        if min_temp_match:
            data["min_temp"] = safe_float(min_temp_match.group(1))
        if avg_temp_match:
            data["avg_temp"] = safe_float(avg_temp_match.group(1))

        return data

    except Exception as e:
        print(f"Fehler beim Parsen der Zeile: {e}")
        return None
