import requests
from config import settings
import json

class IPLoggerSource:
    def __init__(self):
        self.base_url = f"http://{settings.ESP_IP}"
        self.timeout = settings.IP_REQUEST_TIMEOUT

    def fetch_data(self):
        try:
            response = requests.get(
                f"{self.base_url}/data",
                timeout=self.timeout
            )
            if response.status_code == 200:
                return self._parse_response(response.json())
        except Exception as e:
            print(f"IP Logger Fehler: {str(e)}")
        return None

    def _parse_response(self, raw):
        """Transformiert ESP32-Daten ins interne Format"""
        return {
            "U": float(raw.get("voltage", 0.0)),
            "SOC": float(raw.get("soc", 0.0)),
            "current": float(raw.get("current", 0.0)),
            "cells": [float(c) for c in raw.get("cells", [])],
            "max_cell_voltage": float(raw.get("maxCell", 0.0)),
            "min_cell_voltage": float(raw.get("minCell", 0.0)),
            "max_temp": int(raw.get("tempMax", 25)),
            "min_temp": int(raw.get("tempMin", 25)),
            "avg_temp": int(raw.get("tempAvg", 25))
        }
