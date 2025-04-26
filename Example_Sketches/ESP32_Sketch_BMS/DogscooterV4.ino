#include <Arduino.h>
#include <daly-bms-uart.h>

#define BMS_SERIAL Serial1
#define RX1 16
#define TX1 17

Daly_BMS_UART bms(BMS_SERIAL);  // Zuweisung Serial1 für das BMS

void setup() {
  Serial.begin(9600);                                // Baudrate für USB-Serial Monitor
  Serial1.begin(9600, SERIAL_8N1, RX1, TX1);          // Baudrate für BMS UART
  bms.Init();                                        // Initialisierungsfunktion für das BMS  
}

void loop() {
  bms.update();  // Update-Funktion zur Aktualisierung der Werte vom BMS

  // Start der Ausgabe
  Serial.print("U: ");
  Serial.print(bms.get.packVoltage, 2);
  Serial.print(" V | SOC: ");
  Serial.print(bms.get.packSOC, 1);
  Serial.print(" % | Strom: ");
  Serial.print(bms.get.packCurrent / 1000.0, 3);
  Serial.print(" A");

  // Zellspannungen 1-13
  for (int i = 0; i < 13; i++) {
    Serial.print(" | ");
    Serial.print(i + 1);
    Serial.print(".Z: ");
    Serial.print(bms.get.cellVmV[i] / 1000.0, 3);
    Serial.print(" V");
  }

  // Max/Min Zellenspannungen
  Serial.print(" | Max. Zellenspannung: ");
  Serial.print(bms.get.maxCellmV / 1000.0, 3);
  Serial.print(" V (Zelle ");
  Serial.print(bms.get.maxCellVNum);
  Serial.print(") | Min. Zellenspannung: ");
  Serial.print(bms.get.minCellmV / 1000.0, 3);
  Serial.print(" V (Zelle ");
  Serial.print(bms.get.minCellVNum);
  Serial.print(")");

  // Temperaturen
  Serial.print(" | Max. Temp: ");
  Serial.print(bms.get.tempMax);
  Serial.print(" °C | Min. Temp: ");
  Serial.print(bms.get.tempMin);
  Serial.print(" °C | Durchschnittstemperatur: ");
  Serial.print(bms.get.tempAverage);
  Serial.print(" °C");

  // Lade-/Entladezustand und MOS Status
  Serial.print(" | Lade-/Entladezustand: ");
  Serial.print(bms.get.chargeDischargeStatus == 0 ? "Entladen" : "Laden");
  Serial.print(" | Charge MOS: ");
  Serial.print(bms.get.chargeFetState ? "AN" : "AUS");
  Serial.print(" | Discharge MOS: ");
  Serial.print(bms.get.disChargeFetState ? "AN" : "AUS");

  // Zellen Balancing Status
  Serial.print(" | Zellen Balancing: ");
  for (int i = 0; i < 13; i++) {
    Serial.print("Zelle ");
    Serial.print(i + 1);
    Serial.print(": ");
    Serial.print(bms.get.cellBalanceState[i] ? "AN" : "AUS");
    if (i < 12) {
      Serial.print(" | ");
    }
  }

  Serial.println();  // Neue Zeile
  delay(100);        // 100 ms warten
}
