#include <Arduino.h>

// Zellspannungen persistent speichern
float cellVoltages[13];
float packVoltage;
float soc = 90.0;
float packCurrent = 5.0;  // konstanter Entladestrom
int fastDischargeIndex;   // Zelle mit schnellerer Entladung

void setup() {
  Serial.begin(9600);
  randomSeed(analogRead(0));

  // Initiale Zellspannungen zwischen 3.800 und 3.900 V
  for (int i = 0; i < 13; i++) {
    cellVoltages[i] = random(3800, 3901) / 1000.0;
  }

  // Eine Zelle soll schneller entladen: z.B. Zelle 7
  fastDischargeIndex = random(0, 13);

  // Anfangs-Gesamtspannung berechnen
  packVoltage = 0.0;
  for (int i = 0; i < 13; i++) {
    packVoltage += cellVoltages[i];
  }
}

void loop() {
  // Zellspannungen schrittweise verringern (Entladung simulieren)
  for (int i = 0; i < 13; i++) {
    float dischargeRate = 0.03;  // 0.3 mV/Sekunde

    // Die schnell entladende Zelle entlädt 50 % schneller
    if (i == fastDischargeIndex) {
      dischargeRate *= 1.5;
    }

    // Spannung nicht unter 2.5 V fallen lassen (Schutz)
    if (cellVoltages[i] > 2.5) {
      cellVoltages[i] -= dischargeRate;
    }
  }

  // Gesamtspannung und SOC berechnen
  packVoltage = 0.0;
  for (int i = 0; i < 13; i++) {
    packVoltage += cellVoltages[i];
  }

  soc -= 0.01;  // SOC sinkt langsam
  if (soc < 0) soc = 0;

  // Max und Min Zellspannung
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

  // Temperaturdaten (simuliert stabil)
  float tempMax = 38.0;
  float tempMin = 28.0;
  float tempAvg = 33.0;

  // Zustand/MOS/Balancing (simuliert konstant)
  int chargeDischargeStatus = 0; // Entladen
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

  // Zellspannungen
  for (int i = 0; i < 13; i++) {
    Serial.print(" | ");
    Serial.print(i + 1);
    Serial.print(".Z: ");
    Serial.print(cellVoltages[i], 3);
    Serial.print(" V");
  }

  // Max/Min Zellspannungen
  Serial.print(" | Max. Zellenspannung: ");
  Serial.print(maxCellVoltage, 3);
  Serial.print(" V (Zelle ");
  Serial.print(maxCellNum);
  Serial.print(") | Min. Zellenspannung: ");
  Serial.print(minCellVoltage, 3);
  Serial.print(" V (Zelle ");
  Serial.print(minCellNum);
  Serial.print(") ");

  // Temperaturinformationen
  Serial.print("| Max. Temp: ");
  Serial.print(tempMax);
  Serial.print(" °C | Min. Temp: ");
  Serial.print(tempMin);
  Serial.print(" °C | Durchschnittstemperatur: ");
  Serial.print(tempAvg);
  Serial.print(" °C");

  // MOS Status
  Serial.print(" | Lade-/Entladezustand: ");
  Serial.print(chargeDischargeStatus == 0 ? "Entladen" : "Laden");
  Serial.print(" | Charge MOS: ");
  Serial.print(chargeFetState ? "AN" : "AUS");
  Serial.print(" | Discharge MOS: ");
  Serial.print(disChargeFetState ? "AN" : "AUS");

  // Balancing Status
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
  delay(1000);  // 1 Sekunde
}
