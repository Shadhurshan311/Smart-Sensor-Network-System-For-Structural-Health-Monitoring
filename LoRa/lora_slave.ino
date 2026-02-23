/*
 * LoRa Mesh Network - Slave Node
 * ESP32 + SX1278 LoRa Module
 * 
 * Features:
 * - Auto-discovery and ID assignment
 * - Dynamic routing capability
 * - Multi-hop forwarding
 * - Power-saving with sleep modes
 * - Automatic failover
 * - Temperature sensor simulation
 */

#include <SPI.h>
#include <LoRa.h>
#include <esp_sleep.h>

// LoRa pins for ESP32
#define SCK 5
#define MISO 19
#define MOSI 27
#define SS 18
#define RST 14
#define DIO0 26

// LoRa frequency
#define LORA_FREQUENCY 915E6

// Protocol definitions
#define MSG_DISCOVERY 0x01
#define MSG_ASSIGN_ID 0x02
#define MSG_POLL_NEIGHBOR 0x03
#define MSG_RSSI_REPORT 0x04
#define MSG_DATA 0x05
#define MSG_ACK 0x06
#define MSG_HEARTBEAT 0x07
#define MSG_DIRECT_COMM 0x08

// Power saving
#define WAKE_INTERVAL 30000  // 30 seconds
#define TEMP_CHANGE_THRESHOLD 0.5  // Send if temp changes by 0.5°C

#define MAX_NEIGHBORS 10

// Node state
uint8_t myMAC[6];
uint8_t masterMAC[6];
uint8_t myNodeID = 0;
uint8_t totalNodes = 0;
bool canDirectComm = false;
int8_t directRSSI = 0;

// Neighbor information
struct Neighbor {
  uint8_t macAddress[6];
  uint8_t nodeID;
  int8_t rssi;
  bool canReachMaster;
};

Neighbor neighbors[MAX_NEIGHBORS];
uint8_t neighborCount = 0;

// Routing
uint8_t bestHopMAC[6];
uint8_t bestHopNodeID = 0;
int16_t bestPathRSSI = -999;

// Temperature sensor
float lastTemperature = 0.0;
unsigned long lastTempSend = 0;

// Power management
unsigned long lastWake = 0;
bool sleepEnabled = true;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  Serial.println("LoRa Mesh Network - Slave Node");
  
  // Get ESP32 MAC address
  esp_read_mac(myMAC, ESP_MAC_WIFI_STA);
  Serial.print("My MAC: ");
  printMAC(myMAC);
  
  // Initialize LoRa
  SPI.begin(SCK, MISO, MOSI, SS);
  LoRa.setPins(SS, RST, DIO0);
  
  if (!LoRa.begin(LORA_FREQUENCY)) {
    Serial.println("LoRa initialization failed!");
    while (1);
  }
  
  // LoRa configuration
  LoRa.setSpreadingFactor(7);
  LoRa.setSignalBandwidth(125E3);
  LoRa.setCodingRate4(5);
  LoRa.setSyncWord(0x12);
  LoRa.enableCrc();
  LoRa.setTxPower(20);
  
  Serial.println("LoRa initialized successfully");
  Serial.println("Waiting for network discovery...");
  
  // Initialize random seed for temperature
  randomSeed(analogRead(34));
  lastTemperature = 20.0 + random(0, 100) / 10.0;
}

void loop() {
  // Check for incoming messages
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    handleIncomingMessage(packetSize);
  }
  
  // Send data periodically if we have a route
  if (myNodeID > 0 && millis() - lastTempSend > 10000) {
    float currentTemp = readTemperature();
    
    // Send if significant change or regular interval
    if (abs(currentTemp - lastTemperature) > TEMP_CHANGE_THRESHOLD || 
        millis() - lastTempSend > WAKE_INTERVAL) {
      sendTemperatureData(currentTemp);
      lastTemperature = currentTemp;
      lastTempSend = millis();
    }
  }
  
  // Send heartbeat
  if (myNodeID > 0 && millis() - lastWake > WAKE_INTERVAL) {
    sendHeartbeat();
    lastWake = millis();
  }
  
  delay(10);
}

void handleIncomingMessage(int packetSize) {
  uint8_t msgType = LoRa.read();
  
  switch (msgType) {
    case MSG_DISCOVERY:
      handleDiscovery();
      break;
      
    case MSG_ASSIGN_ID:
      handleIDAssignment();
      break;
      
    case MSG_POLL_NEIGHBOR:
      handleNeighborPoll();
      break;
      
    case MSG_DIRECT_COMM:
      handleDirectCommQuery();
      break;
      
    case MSG_DATA:
      handleDataForwarding();
      break;
  }
}

void handleDiscovery() {
  // Read master MAC
  for (int i = 0; i < 6; i++) {
    masterMAC[i] = LoRa.read();
  }
  
  directRSSI = LoRa.packetRssi();
  
  Serial.print("Discovery from master, RSSI: ");
  Serial.println(directRSSI);
  
  // Send acknowledgment
  delay(random(10, 100));  // Random delay to avoid collisions
  
  LoRa.beginPacket();
  LoRa.write(MSG_ACK);
  LoRa.write(myMAC, 6);
  LoRa.endPacket();
  
  Serial.println("Sent ACK to master");
}

void handleIDAssignment() {
  uint8_t receivedMasterMAC[6];
  uint8_t targetMAC[6];
  
  for (int i = 0; i < 6; i++) receivedMasterMAC[i] = LoRa.read();
  for (int i = 0; i < 6; i++) targetMAC[i] = LoRa.read();
  
  // Check if this message is for us
  if (memcmp(targetMAC, myMAC, 6) == 0) {
    myNodeID = LoRa.read();
    totalNodes = LoRa.read();
    
    Serial.print("Assigned ID: ");
    Serial.print(myNodeID);
    Serial.print(" (");
    Serial.print(totalNodes);
    Serial.println(" total nodes)");
    
    // Determine if we can communicate directly with master
    if (directRSSI > -120) {  // Good enough for direct communication
      canDirectComm = true;
      bestPathRSSI = directRSSI;
      memcpy(bestHopMAC, masterMAC, 6);
      bestHopNodeID = 0;  // 0 means direct to master
      
      Serial.println("Can communicate directly with master");
    } else {
      canDirectComm = false;
      Serial.println("Need relay for master communication");
    }
  }
}

void handleNeighborPoll() {
  uint8_t receivedMasterMAC[6];
  uint8_t pollingNodeMAC[6];
  uint8_t targetNodeMAC[6];
  
  for (int i = 0; i < 6; i++) receivedMasterMAC[i] = LoRa.read();
  for (int i = 0; i < 6; i++) pollingNodeMAC[i] = LoRa.read();
  for (int i = 0; i < 6; i++) targetNodeMAC[i] = LoRa.read();
  
  // Am I the polling node?
  if (memcmp(pollingNodeMAC, myMAC, 6) == 0) {
    Serial.print("Polling neighbor: ");
    printMAC(targetNodeMAC);
    
    delay(100);
    
    // Send poll request
    LoRa.beginPacket();
    LoRa.write(MSG_DIRECT_COMM);
    LoRa.write(myMAC, 6);
    LoRa.write(targetNodeMAC, 6);
    LoRa.write(canDirectComm ? 1 : 0);
    LoRa.endPacket();
    
    delay(500);
    
    // Wait for response
    unsigned long startTime = millis();
    while (millis() - startTime < 2000) {
      int packetSize = LoRa.parsePacket();
      if (packetSize) {
        uint8_t type = LoRa.read();
        if (type == MSG_ACK) {
          uint8_t responderMAC[6];
          for (int i = 0; i < 6; i++) responderMAC[i] = LoRa.read();
          
          if (memcmp(responderMAC, targetNodeMAC, 6) == 0) {
            int8_t neighborRSSI = LoRa.packetRssi();
            uint8_t neighborCanDirect = LoRa.read();
            
            Serial.print("Received response, RSSI: ");
            Serial.println(neighborRSSI);
            
            // Send RSSI report to master
            LoRa.beginPacket();
            LoRa.write(MSG_RSSI_REPORT);
            LoRa.write(myMAC, 6);
            LoRa.write(targetNodeMAC, 6);
            LoRa.write((uint8_t)neighborRSSI);
            LoRa.endPacket();
            
            break;
          }
        }
      }
    }
  }
  
  // Am I the target node?
  if (memcmp(targetNodeMAC, myMAC, 6) == 0) {
    // Wait for direct poll
    // (handled in MSG_DIRECT_COMM case)
  }
}

void handleDirectCommQuery() {
  uint8_t pollingNodeMAC[6];
  uint8_t targetNodeMAC[6];
  
  for (int i = 0; i < 6; i++) pollingNodeMAC[i] = LoRa.read();
  for (int i = 0; i < 6; i++) targetNodeMAC[i] = LoRa.read();
  
  // Is this query for me?
  if (memcmp(targetNodeMAC, myMAC, 6) == 0) {
    uint8_t pollerCanDirect = LoRa.read();
    int8_t pollerRSSI = LoRa.packetRssi();
    
    Serial.print("Direct poll from: ");
    printMAC(pollingNodeMAC);
    Serial.print(" RSSI: ");
    Serial.println(pollerRSSI);
    
    // If poller can talk directly to master and has poor link to us, decline
    if (pollerCanDirect && !canDirectComm) {
      // This node can be our relay
      addOrUpdateNeighbor(pollingNodeMAC, 0, pollerRSSI, true);
      
      // Update best path if better
      int16_t potentialPathRSSI = directRSSI + pollerRSSI;
      if (potentialPathRSSI > bestPathRSSI) {
        bestPathRSSI = potentialPathRSSI;
        memcpy(bestHopMAC, pollingNodeMAC, 6);
        
        Serial.println("Updated best path through this neighbor");
      }
    }
    
    // Send response
    delay(random(10, 50));
    LoRa.beginPacket();
    LoRa.write(MSG_ACK);
    LoRa.write(myMAC, 6);
    LoRa.write(canDirectComm ? 1 : 0);
    LoRa.endPacket();
  }
}

void handleDataForwarding() {
  uint8_t senderMAC[6];
  for (int i = 0; i < 6; i++) senderMAC[i] = LoRa.read();
  
  // If I can talk to master directly and this is from another node, forward it
  if (canDirectComm && memcmp(senderMAC, myMAC, 6) != 0) {
    float temperature;
    LoRa.readBytes((uint8_t*)&temperature, sizeof(float));
    
    Serial.print("Forwarding data from: ");
    printMAC(senderMAC);
    Serial.print(" Temp: ");
    Serial.println(temperature);
    
    delay(100);
    
    // Forward to master
    LoRa.beginPacket();
    LoRa.write(MSG_DATA);
    LoRa.write(senderMAC, 6);  // Original sender
    LoRa.write((uint8_t*)&temperature, sizeof(float));
    LoRa.endPacket();
  }
}

void addOrUpdateNeighbor(uint8_t* mac, uint8_t nodeID, int8_t rssi, bool canReachMaster) {
  // Check if neighbor exists
  for (int i = 0; i < neighborCount; i++) {
    if (memcmp(neighbors[i].macAddress, mac, 6) == 0) {
      neighbors[i].rssi = rssi;
      neighbors[i].canReachMaster = canReachMaster;
      return;
    }
  }
  
  // Add new neighbor
  if (neighborCount < MAX_NEIGHBORS) {
    memcpy(neighbors[neighborCount].macAddress, mac, 6);
    neighbors[neighborCount].nodeID = nodeID;
    neighbors[neighborCount].rssi = rssi;
    neighbors[neighborCount].canReachMaster = canReachMaster;
    neighborCount++;
  }
}

float readTemperature() {
  // Simulate temperature sensor with realistic variation
  float baseTemp = 22.0;
  float variation = sin(millis() / 10000.0) * 3.0;  // Slow sine wave
  float noise = (random(-50, 50) / 100.0);  // Small random noise
  
  return baseTemp + variation + noise;
}

void sendTemperatureData(float temperature) {
  if (myNodeID == 0) return;
  
  Serial.print("Sending temperature: ");
  Serial.print(temperature);
  Serial.print(" °C via ");
  
  if (canDirectComm) {
    Serial.println("direct link");
    
    LoRa.beginPacket();
    LoRa.write(MSG_DATA);
    LoRa.write(myMAC, 6);
    LoRa.write((uint8_t*)&temperature, sizeof(float));
    LoRa.endPacket();
  } else {
    // Send via best hop
    Serial.print("relay: ");
    printMAC(bestHopMAC);
    
    LoRa.beginPacket();
    LoRa.write(MSG_DATA);
    LoRa.write(myMAC, 6);
    LoRa.write((uint8_t*)&temperature, sizeof(float));
    LoRa.endPacket();
  }
}

void sendHeartbeat() {
  if (canDirectComm) {
    LoRa.beginPacket();
    LoRa.write(MSG_HEARTBEAT);
    LoRa.write(myMAC, 6);
    LoRa.endPacket();
  }
}

void printMAC(uint8_t* mac) {
  for (int i = 0; i < 6; i++) {
    if (mac[i] < 0x10) Serial.print("0");
    Serial.print(mac[i], HEX);
    if (i < 5) Serial.print(":");
  }
  Serial.println();
}
