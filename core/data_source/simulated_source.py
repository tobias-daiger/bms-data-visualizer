import random
import datetime

from core.data_source.base_source import DataSource

class SimulatedSource(DataSource):
    def read_voltage(self):
        voltage = round(random.uniform(3.5, 4.2), 3)
        now = datetime.datetime.now()
        print(f"Simulierter Wert: 1.Z: {voltage}V um {now.strftime('%H:%M:%S')}")
        return now, voltage
