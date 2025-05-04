#include <Arduino.h>

// Zellspannungen persistent speichern
float cellVoltages[13];
float packVoltage;
float soc = 90.0;
float packCurrent = 5.0;  // konstanter Entladestrom
int fastDischargeIndex;   // Zelle mit schnellerer Entladung

// Temperaturvariablen (global)
float tempMax;
float tempMin;
float tempAvg;

void setup() {
  Serial.begin(9600);
  randomSeed(analogRead(0));

  // Initiale Zellspannungen zwischen 3.800 und 3.900 V
  for (int i = 0; i < 13; i++) {
    cellVoltages[i] = random(3800, 3901) / 1000.0;
  }

  fastDischargeIndex = random(0, 13);

  packVoltage = 0.0;
  for (int i = 0; i < 13; i++) {
    packVoltage += cellVoltages[i];
  }

  // Temperatur initial auf 20 °C setzen
  tempMax = 20.0;
  tempMin = 20.0;
  tempAvg = 20.0;
}

void loop() {
  // Zellspannungen schrittweise verringern (Entladung simulieren)
  for (int i = 0; i < 13; i++) {
    float dischargeRate = 0.03;
    if (i == fastDischargeIndex) {
      dischargeRate *= 1.5;
    }
    if (cellVoltages[i] > 2.5) {
      cellVoltages[i] -= dischargeRate;
    }
  }

  // Gesamtspannung und SOC berechnen
  packVoltage = 0.0;
  for (int i = 0; i < 13; i++) {
    packVoltage += cellVoltages[i];
  }

  soc -= 0.01;
  if (soc < 0) soc = 0;

  // Max und Min Zellspannung berechnen
  float maxCellVoltage = cellVoltages[0];
  float minCellVoltage = cellVoltages[0];
  int maxCellNum = 1;
  int minCellNum = 1;
  for (int i = 1; i < 13; i++) {
    if (cellVoltages[i] > maxCellVoltage) {
      maxCellVoltage = cellVoltages[i];
      maxCellNum = i + 1;
    }
    if (cellVoltages[i] < minCellVoltage) {
      minCellVoltage = cellVoltages[i];
      minCellNum = i + 1;
    }
  }

  // Temperatur alle 1 Sekunde um 3°C senken, nicht unter -40°C
  tempMax = max(tempMax - 1.0, -40.0);
  tempMin = max(tempMin - 1.0, -40.0);
  tempAvg = max(tempAvg - 1.0, -40.0);

  // Status simulieren
  int chargeDischargeStatus = 0;
  bool chargeFetState = false;
  bool disChargeFetState = true;
  bool cellBalanceState[13];
  for (int i = 0; i < 13; i++) {
    cellBalanceState[i] = false;
  }

  // Serieller Monitor Output
  Serial.print("U: ");
  Serial.print(packVoltage, 2);
  Serial.print(" V | SOC: ");
  Serial.print(soc, 1);
  Serial.print(" % | Strom: ");
  Serial.print(packCurrent, 3);
  Serial.print(" A");

  for (int i = 0; i < 13; i++) {
    Serial.print(" | ");
    Serial.print(i + 1);
    Serial.print(".Z: ");
    Serial.print(cellVoltages[i], 3);
    Serial.print(" V");
  }

  Serial.print(" | Max. Zellenspannung: ");
  Serial.print(maxCellVoltage, 3);
  Serial.print(" V (Zelle ");
  Serial.print(maxCellNum);
  Serial.print(") | Min. Zellenspannung: ");
  Serial.print(minCellVoltage, 3);
  Serial.print(" V (Zelle ");
  Serial.print(minCellNum);
  Serial.print(") ");

  Serial.print("| Max. Temp: ");
  Serial.print(tempMax);
  Serial.print(" °C | Min. Temp: ");
  Serial.print(tempMin);
  Serial.print(" °C | Durchschnittstemperatur: ");
  Serial.print(tempAvg);
  Serial.print(" °C");

  Serial.print(" | Lade-/Entladezustand: ");
  Serial.print(chargeDischargeStatus == 0 ? "Entladen" : "Laden");
  Serial.print(" | Charge MOS: ");
  Serial.print(chargeFetState ? "AN" : "AUS");
  Serial.print(" | Discharge MOS: ");
  Serial.print(disChargeFetState ? "AN" : "AUS");

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
  delay(1000);
}
