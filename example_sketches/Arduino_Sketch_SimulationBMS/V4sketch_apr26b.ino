#include <Arduino.h>

void setup() {
  Serial.begin(9600);  // Baudrate für USB-Serial Monitor
  randomSeed(analogRead(0));  // Zufallswert initialisieren
}

void loop() {
  // Zufallswerte für Gesamtspannung (49.0 - 50.0 V), SOC (80% - 90%) und Strom (0.0 - 20.0 A)
  float packVoltage = random(4900, 5001) / 100.0;
  float soc = random(800, 901) / 10.0;
  float packCurrent = random(0, 20001) / 1000.0;  // Strom in Ampere (0.0 - 20.0 A)

  // Zellspannungen simulieren (Zellen 1 bis 13)
  float cellVoltages[13];
  for (int i = 0; i < 13; i++) {
    cellVoltages[i] = random(3900, 4101) / 1000.0;
  }

  // Maximale und minimale Zellspannungen simulieren
  float maxCellVoltage = random(4100, 4200) / 1000.0;
  float minCellVoltage = random(3800, 3900) / 1000.0;
  int maxCellNum = random(1, 14);  // Zellnummer der maximalen Spannung
  int minCellNum = random(1, 14);  // Zellnummer der minimalen Spannung

  // Temperaturdaten simulieren
  float tempMax = random(30, 50);  // Maximale Temperatur
  float tempMin = random(20, 30);  // Minimale Temperatur
  float tempAvg = random(25, 35);  // Durchschnittstemperatur

  // Lade-/Entladezustand und MOS-Status simulieren
  int chargeDischargeStatus = random(0, 2);  // 0 = Entladen, 1 = Laden
  bool chargeFetState = random(0, 2);  // 0 = AUS, 1 = AN
  bool disChargeFetState = random(0, 2);  // 0 = AUS, 1 = AN

  // Zell-Balancing Status simulieren
  bool cellBalanceState[13];
  for (int i = 0; i < 13; i++) {
    cellBalanceState[i] = random(0, 2);  // 0 = AUS, 1 = AN
  }

  // Serieller Monitor Output
  Serial.print("U: ");
  Serial.print(packVoltage, 2);
  Serial.print(" V | SOC: ");
  Serial.print(soc, 1);
  Serial.print(" % | Strom: ");
  Serial.print(packCurrent, 3);
  Serial.print(" A");

  // Zellspannungen ausgeben
  for (int i = 0; i < 13; i++) {
    Serial.print(" | ");
    Serial.print(i + 1);
    Serial.print(".Z: ");
    Serial.print(cellVoltages[i], 3);
    Serial.print(" V");
  }

  // Maximale und minimale Zellspannungen ausgeben
  Serial.print(" | Max. Zellenspannung: ");
  Serial.print(maxCellVoltage, 3);
  Serial.print(" V (Zelle ");
  Serial.print(maxCellNum);
  Serial.print(") | Min. Zellenspannung: ");
  Serial.print(minCellVoltage, 3);
  Serial.print(" V (Zelle ");
  Serial.print(minCellNum);
  Serial.print(") ");

  // Temperaturinformationen ausgeben
  Serial.print("| Max. Temp: ");
  Serial.print(tempMax);
  Serial.print(" °C | Min. Temp: ");
  Serial.print(tempMin);
  Serial.print(" °C | Durchschnittstemperatur: ");
  Serial.print(tempAvg);
  Serial.print(" °C");

  // Lade-/Entladezustand und MOS-Status ausgeben
  Serial.print(" | Lade-/Entladezustand: ");
  Serial.print(chargeDischargeStatus == 0 ? "Entladen" : "Laden");
  Serial.print(" | Charge MOS: ");
  Serial.print(chargeFetState ? "AN" : "AUS");
  Serial.print(" | Discharge MOS: ");
  Serial.print(disChargeFetState ? "AN" : "AUS");

  // Zell-Balancing Status ausgeben
  Serial.print(" | Zellen Balancing: ");
  for (int i = 0; i < 13; i++) {
    Serial.print("Zelle ");
    Serial.print(i + 1);
    Serial.print(": ");
    Serial.print(cellBalanceState[i] ? "AN" : "AUS");
    if (i < 12) {
      Serial.print(" | ");
    }
  }
  Serial.println();
  delay(100);  // 1 Sekunde warten für bessere Lesbarkeit im seriellen Monitor
}
