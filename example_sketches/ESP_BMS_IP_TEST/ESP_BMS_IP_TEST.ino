#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

WebServer server(80);

const char* ssid = "BMS-Monitor";
const char* password = "12345678";

// Simulierte Datenstruktur
struct SimulatedData {
  float packVoltage = 48.0f;
  float packSOC = 100.0f;
  float packCurrent = 0.0f;
  uint16_t cellVmV[13] = {3300, 3310, 3290, 3320, 3305, 3315, 3295, 3300, 3310, 3290, 3305, 3315, 3295};
  int8_t tempMax = 25;
  int8_t tempMin = 22;
  int8_t tempAverage = 23;
  uint16_t maxCellmV = 3320;
  uint8_t maxCellVNum = 4;
  uint16_t minCellmV = 3290;
  uint8_t minCellVNum = 3;
  bool chargeFetState = false;
  bool disChargeFetState = true;
  bool cellBalanceState[13] = {false};
  uint8_t chargeDischargeStatus = 0;
} simData;

unsigned long lastUpdate = 0;

void setup() {
  Serial.begin(115200);
  
  WiFi.softAP(ssid, password);
  IPAddress IP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(IP);

  server.on("/", handleRoot);
  server.on("/data", handleData);
  server.begin();

  randomSeed(analogRead(0));
}

void loop() {
  server.handleClient();
  
  if(millis() - lastUpdate > 1000) {
    updateSimulation();
    lastUpdate = millis();
  }
}

void updateSimulation() {
  // Dynamische Wertänderungen
  simData.packVoltage = 44.0f + 4.0f * sin(millis() / 5000.0f);
  simData.packSOC = fmod(simData.packSOC - 0.1f, 100.0f);
  if(simData.packSOC < 5.0f) simData.packSOC = 100.0f;
  
  simData.packCurrent = random(-500, 2000) / 1000.0f;
  
  // Zellspannungen aktualisieren
  for(int i=0; i<13; i++) {
    simData.cellVmV[i] = 3200 + random(-50, 50) + 100 * sin(millis()/3000.0f + i);
  }
  
  // Temperaturen
  simData.tempMax = 20 + random(0, 10);
  simData.tempMin = simData.tempMax - 3;
  simData.tempAverage = (simData.tempMax + simData.tempMin) / 2;
  
  // MOSFET-Status
  simData.chargeFetState = (simData.packSOC < 95.0f);
  simData.disChargeFetState = (simData.packSOC > 5.0f);
  
  // Max/Min Zellspannung
  uint16_t maxV = 0;
  uint16_t minV = 0xFFFF;
  for(int i=0; i<13; i++) {
    if(simData.cellVmV[i] > maxV) {
      maxV = simData.cellVmV[i];
      simData.maxCellVNum = i+1;
    }
    if(simData.cellVmV[i] < minV) {
      minV = simData.cellVmV[i];
      simData.minCellVNum = i+1;
    }
  }
  simData.maxCellmV = maxV;
  simData.minCellmV = minV;
  
  // Balancing
  for(int i=0; i<13; i++) {
    simData.cellBalanceState[i] = (random(0, 100) > 85) && (simData.cellVmV[i] > 3300);
  }
  
  simData.chargeDischargeStatus = (simData.packCurrent > 0) ? 1 : 0;
}

void handleRoot() {
  String html = R"rawliteral(
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta charset="UTF-8">
  <style>
    body {font-family: Arial; padding: 20px;}
    .card {background: #f5f5f5; padding: 15px; border-radius: 8px; margin-bottom: 15px;}
    h2 {color: #34495e; border-bottom: 2px solid #3498db;}
    .cellgrid {display: grid; grid-template-columns: repeat(3, 1fr);}
  </style>
  <script>
    function updateData() {
      fetch('/data')
        .then(response => response.json())
        .then(data => {
          document.getElementById('voltage').innerText = data.voltage;
          document.getElementById('soc').innerText = data.soc;
          document.getElementById('current').innerText = data.current;
          for(let i=1; i<=13; i++) {
            document.getElementById('cell'+i).innerText = data.cells[i-1];
          }
          document.getElementById('tempMax').innerText = data.tempMax;
          document.getElementById('tempMin').innerText = data.tempMin;
          document.getElementById('tempAvg').innerText = data.tempAvg;
          document.getElementById('status').innerText = data.status;
          document.getElementById('maxCell').innerText = data.maxCell;
          document.getElementById('maxCellNum').innerText = data.maxCellNum;
          document.getElementById('minCell').innerText = data.minCell;
          document.getElementById('minCellNum').innerText = data.minCellNum;
          document.getElementById('chargeMos').innerText = data.chargeMos;
          document.getElementById('dischargeMos').innerText = data.dischargeMos;
          for(let i=1; i<=13; i++) {
            document.getElementById('bal'+i).innerText = data.balancing[i-1];
          }
        });
    }
    setInterval(updateData, 1000);
    document.addEventListener('DOMContentLoaded', updateData);
  </script>
</head>
<body>
  <h1>BMS Live-Daten</h1>
  
  <div class="card">
    <h2>Gesamtwerte</h2>
    <div>Spannung: <span id="voltage">0.00</span> V</div>
    <div>SOC: <span id="soc">0.0</span> %</div>
    <div>Strom: <span id="current">0.000</span> A</div>
  </div>

  <div class="card">
    <h2>Zellspannungen</h2>
    <div class="cellgrid">
      <div>Zelle 1: <span id="cell1">0.000</span> V</div>
      <div>Zelle 2: <span id="cell2">0.000</span> V</div>
      <div>Zelle 3: <span id="cell3">0.000</span> V</div>
      <div>Zelle 4: <span id="cell4">0.000</span> V</div>
      <div>Zelle 5: <span id="cell5">0.000</span> V</div>
      <div>Zelle 6: <span id="cell6">0.000</span> V</div>
      <div>Zelle 7: <span id="cell7">0.000</span> V</div>
      <div>Zelle 8: <span id="cell8">0.000</span> V</div>
      <div>Zelle 9: <span id="cell9">0.000</span> V</div>
      <div>Zelle 10: <span id="cell10">0.000</span> V</div>
      <div>Zelle 11: <span id="cell11">0.000</span> V</div>
      <div>Zelle 12: <span id="cell12">0.000</span> V</div>
      <div>Zelle 13: <span id="cell13">0.000</span> V</div>
    </div>
  </div>

  <div class="card">
    <h2>Temperaturen & Status</h2>
    <div>Max. Temp: <span id="tempMax">0</span> °C</div>
    <div>Min. Temp: <span id="tempMin">0</span> °C</div>
    <div>Durchschnittstemperatur: <span id="tempAvg">0</span> °C</div>
    <div>Status: <span id="status">-</span></div>
    <div>Max. Zellenspannung: <span id="maxCell">0.000</span> V (Zelle <span id="maxCellNum">0</span>)</div>
    <div>Min. Zellenspannung: <span id="minCell">0.000</span> V (Zelle <span id="minCellNum">0</span>)</div>
    <div>Charge MOS: <span id="chargeMos">AUS</span></div>
    <div>Discharge MOS: <span id="dischargeMos">AUS</span></div>
  </div>

  <div class="card">
    <h2>Zellen-Balancing</h2>
    <div class="cellgrid">
      <div>Zelle 1: <span id="bal1">AUS</span></div>
      <div>Zelle 2: <span id="bal2">AUS</span></div>
      <div>Zelle 3: <span id="bal3">AUS</span></div>
      <div>Zelle 4: <span id="bal4">AUS</span></div>
      <div>Zelle 5: <span id="bal5">AUS</span></div>
      <div>Zelle 6: <span id="bal6">AUS</span></div>
      <div>Zelle 7: <span id="bal7">AUS</span></div>
      <div>Zelle 8: <span id="bal8">AUS</span></div>
      <div>Zelle 9: <span id="bal9">AUS</span></div>
      <div>Zelle 10: <span id="bal10">AUS</span></div>
      <div>Zelle 11: <span id="bal11">AUS</span></div>
      <div>Zelle 12: <span id="bal12">AUS</span></div>
      <div>Zelle 13: <span id="bal13">AUS</span></div>
    </div>
  </div>
</body>
</html>
  )rawliteral";

  server.send(200, "text/html; charset=UTF-8", html);
}

void handleData() {
  DynamicJsonDocument doc(2048);

  // Basisdaten
  doc["voltage"] = String(simData.packVoltage, 2);
  doc["soc"] = String(simData.packSOC, 1);
  doc["current"] = String(simData.packCurrent, 3);

  // Zellspannungen
  JsonArray cells = doc.createNestedArray("cells");
  for(int i=0; i<13; i++) {
    cells.add(String(simData.cellVmV[i] / 1000.0, 3));
  }

  // Temperaturen & Status
  doc["tempMax"] = simData.tempMax;
  doc["tempMin"] = simData.tempMin;
  doc["tempAvg"] = simData.tempAverage;
  doc["status"] = simData.chargeDischargeStatus ? "Laden" : "Entladen";
  doc["maxCell"] = String(simData.maxCellmV / 1000.0, 3);
  doc["maxCellNum"] = simData.maxCellVNum;
  doc["minCell"] = String(simData.minCellmV / 1000.0, 3);
  doc["minCellNum"] = simData.minCellVNum;
  doc["chargeMos"] = simData.chargeFetState ? "AN" : "AUS";
  doc["dischargeMos"] = simData.disChargeFetState ? "AN" : "AUS";

  // Zell-Balancing
  JsonArray balancing = doc.createNestedArray("balancing");
  for(int i=0; i<13; i++) {
    balancing.add(simData.cellBalanceState[i] ? "AN" : "AUS");
  }

  String jsonString;
  serializeJson(doc, jsonString);
  server.send(200, "application/json; charset=UTF-8", jsonString);
}
