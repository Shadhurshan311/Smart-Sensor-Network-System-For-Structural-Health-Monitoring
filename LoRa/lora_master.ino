/*
 * LoRa Mesh Network - Master Node
 * ESP32 + SX1278 LoRa Module
 * 
 * Features:
 * - Dynamic node discovery via RSSI polling
 * - Automatic routing table generation
 * - Multi-hop path selection
 * - Automatic failover on node failure
 */

#include <SPI.h>
#include <LoRa.h>

// LoRa pins for ESP32
#define SCK 5
#define MISO 19
#define MOSI 27
#define SS 18
#define RST 14
#define DIO0 26

// LoRa frequency (adjust based on your region)
#define LORA_FREQUENCY 915E6  // 915 MHz for US, use 868E6 for EU

// Protocol definitions
#define MSG_DISCOVERY 0x01
#define MSG_ASSIGN_ID 0x02
#define MSG_POLL_NEIGHBOR 0x03
#define MSG_RSSI_REPORT 0x04
#define MSG_DATA 0x05
#define MSG_ACK 0x06
#define MSG_HEARTBEAT 0x07
#define MSG_DIRECT_COMM 0x08

#define MAX_NODES 10
#define DISCOVERY_TIMEOUT 5000
#define POLL_INTERVAL 30000
#define HEARTBEAT_TIMEOUT 60000

// Node structure
struct Node {
  uint8_t macAddress[6];
  int8_t rssi;
  uint8_t hopCount;
  uint8_t viaNode;  // 0 = direct, >0 = via another node
  unsigned long lastSeen;
  bool active;
  int16_t pathRSSI;  // Total RSSI for the path
};

Node nodes[MAX_NODES];
uint8_t nodeCount = 0;
unsigned long lastDiscovery = 0;
uint8_t masterMAC[6];

void setup() {
  Serial.begin(115200);
  while (!Serial);
  
  Serial.println("LoRa Mesh Network - Master Node");
  
  // Get ESP32 MAC address
  esp_read_mac(masterMAC, ESP_MAC_WIFI_STA);
  Serial.print("Master MAC: ");
  printMAC(masterMAC);
  
  // Initialize LoRa
  SPI.begin(SCK, MISO, MOSI, SS);
  LoRa.setPins(SS, RST, DIO0);
  
  if (!LoRa.begin(LORA_FREQUENCY)) {
    Serial.println("LoRa initialization failed!");
    while (1);
  }
  
  // LoRa configuration for better range and reliability
  LoRa.setSpreadingFactor(7);
  LoRa.setSignalBandwidth(125E3);
  LoRa.setCodingRate4(5);
  LoRa.setSyncWord(0x12);
  LoRa.enableCrc();
  LoRa.setTxPower(20);
  
  Serial.println("LoRa initialized successfully");
  
  // Initialize node array
  for (int i = 0; i < MAX_NODES; i++) {
    nodes[i].active = false;
  }
  
  delay(1000);
  performDiscovery();
}

void loop() {
  // Check for incoming messages
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    handleIncomingMessage(packetSize);
  }
  
  // Periodic discovery and routing update
  if (millis() - lastDiscovery > POLL_INTERVAL) {
    performDiscovery();
    lastDiscovery = millis();
  }
  
  // Check for dead nodes
  checkNodeHealth();
  
  delay(10);
}

void performDiscovery() {
  Serial.println("\n=== Starting Network Discovery ===");
  
  // Reset node count
  nodeCount = 0;
  
  // Step 1: Broadcast discovery to find all nodes
  Serial.println("Step 1: Broadcasting discovery...");
  broadcastDiscovery();
  
  delay(100);
  
  // Step 2: Wait for responses and collect RSSI values
  Serial.println("Step 2: Collecting responses...");
  unsigned long startTime = millis();
  while (millis() - startTime < DISCOVERY_TIMEOUT) {
    int packetSize = LoRa.parsePacket();
    if (packetSize) {
      handleDiscoveryResponse();
    }
  }
  
  Serial.print("Found ");
  Serial.print(nodeCount);
  Serial.println(" nodes");
  
  // Step 3: Sort nodes by RSSI (strongest first)
  sortNodesByRSSI();
  
  // Step 4: Assign node IDs based on RSSI
  assignNodeIDs();
  
  // Step 5: Instruct close nodes to poll distant nodes
  if (nodeCount > 2) {
    instructNeighborPolling();
  }
  
  // Step 6: Build complete routing table
  delay(2000);
  collectRoutingInfo();
  
  // Step 7: Display routing table
  displayRoutingTable();
}

void broadcastDiscovery() {
  LoRa.beginPacket();
  LoRa.write(MSG_DISCOVERY);
  LoRa.write(masterMAC, 6);
  LoRa.endPacket();
}

void handleDiscoveryResponse() {
  uint8_t msgType = LoRa.read();
  
  if (msgType == MSG_ACK) {
    uint8_t slaveMAC[6];
    for (int i = 0; i < 6; i++) {
      slaveMAC[i] = LoRa.read();
    }
    
    int rssi = LoRa.packetRssi();
    
    // Add or update node
    int nodeIndex = findOrAddNode(slaveMAC);
    if (nodeIndex >= 0) {
      nodes[nodeIndex].rssi = rssi;
      nodes[nodeIndex].hopCount = 1;
      nodes[nodeIndex].viaNode = 0;  // Direct connection
      nodes[nodeIndex].lastSeen = millis();
      nodes[nodeIndex].active = true;
      nodes[nodeIndex].pathRSSI = rssi;
      
      Serial.print("Node ");
      printMAC(slaveMAC);
      Serial.print(" RSSI: ");
      Serial.println(rssi);
    }
  }
}

int findOrAddNode(uint8_t* mac) {
  // Check if node already exists
  for (int i = 0; i < nodeCount; i++) {
    if (memcmp(nodes[i].macAddress, mac, 6) == 0) {
      return i;
    }
  }
  
  // Add new node
  if (nodeCount < MAX_NODES) {
    memcpy(nodes[nodeCount].macAddress, mac, 6);
    return nodeCount++;
  }
  
  return -1;
}

void sortNodesByRSSI() {
  // Simple bubble sort by RSSI (descending)
  for (int i = 0; i < nodeCount - 1; i++) {
    for (int j = 0; j < nodeCount - i - 1; j++) {
      if (nodes[j].rssi < nodes[j + 1].rssi) {
        Node temp = nodes[j];
        nodes[j] = nodes[j + 1];
        nodes[j + 1] = temp;
      }
    }
  }
}

void assignNodeIDs() {
  Serial.println("\nAssigning Node IDs:");
  for (int i = 0; i < nodeCount; i++) {
    uint8_t nodeID = i + 1;
    
    // Send ID assignment
    LoRa.beginPacket();
    LoRa.write(MSG_ASSIGN_ID);
    LoRa.write(masterMAC, 6);
    LoRa.write(nodes[i].macAddress, 6);
    LoRa.write(nodeID);
    LoRa.write(nodeCount);  // Total number of nodes
    LoRa.endPacket();
    
    Serial.print("  Node ");
    Serial.print(nodeID);
    Serial.print(" (");
    printMAC(nodes[i].macAddress);
    Serial.print(") RSSI: ");
    Serial.println(nodes[i].rssi);
    
    delay(200);
  }
}

void instructNeighborPolling() {
  Serial.println("\nInstructing neighbor polling...");
  
  // Nodes with good RSSI should poll weaker nodes
  for (int i = 0; i < nodeCount - 1 && i < 2; i++) {  // First 2 nodes
    for (int j = 2; j < nodeCount; j++) {  // Poll distant nodes
      // Send instruction to node i to poll node j
      LoRa.beginPacket();
      LoRa.write(MSG_POLL_NEIGHBOR);
      LoRa.write(masterMAC, 6);
      LoRa.write(nodes[i].macAddress, 6);  // Polling node
      LoRa.write(nodes[j].macAddress, 6);  // Target node
      LoRa.endPacket();
      
      delay(300);
    }
  }
}

void collectRoutingInfo() {
  Serial.println("\nCollecting routing information...");
  
  unsigned long startTime = millis();
  while (millis() - startTime < 5000) {
    int packetSize = LoRa.parsePacket();
    if (packetSize) {
      handleRoutingReport();
    }
  }
}

void handleRoutingReport() {
  uint8_t msgType = LoRa.read();
  
  if (msgType == MSG_RSSI_REPORT) {
    uint8_t pollingNode[6], targetNode[6];
    
    for (int i = 0; i < 6; i++) pollingNode[i] = LoRa.read();
    for (int i = 0; i < 6; i++) targetNode[i] = LoRa.read();
    
    int hopRSSI = (int8_t)LoRa.read();
    
    // Find nodes
    int pollingIdx = findNode(pollingNode);
    int targetIdx = findNode(targetNode);
    
    if (pollingIdx >= 0 && targetIdx >= 0) {
      // Calculate total path RSSI: Master->Polling + Polling->Target
      int totalPathRSSI = nodes[pollingIdx].rssi + hopRSSI;
      
      // Update if this path is better
      if (nodes[targetIdx].hopCount > 1 || totalPathRSSI > nodes[targetIdx].pathRSSI) {
        nodes[targetIdx].hopCount = 2;
        nodes[targetIdx].viaNode = pollingIdx + 1;  // Store node ID (1-indexed)
        nodes[targetIdx].pathRSSI = totalPathRSSI;
        
        Serial.print("Updated route to Node ");
        Serial.print(targetIdx + 1);
        Serial.print(" via Node ");
        Serial.print(pollingIdx + 1);
        Serial.print(" (Total RSSI: ");
        Serial.print(totalPathRSSI);
        Serial.println(")");
      }
    }
  }
}

int findNode(uint8_t* mac) {
  for (int i = 0; i < nodeCount; i++) {
    if (memcmp(nodes[i].macAddress, mac, 6) == 0) {
      return i;
    }
  }
  return -1;
}

void handleIncomingMessage(int packetSize) {
  uint8_t msgType = LoRa.read();
  
  switch (msgType) {
    case MSG_DATA: {
      uint8_t senderMAC[6];
      for (int i = 0; i < 6; i++) senderMAC[i] = LoRa.read();
      
      float temperature;
      LoRa.readBytes((uint8_t*)&temperature, sizeof(float));
      
      int nodeIdx = findNode(senderMAC);
      if (nodeIdx >= 0) {
        nodes[nodeIdx].lastSeen = millis();
        
        Serial.print("\n[DATA] Node ");
        Serial.print(nodeIdx + 1);
        Serial.print(" Temperature: ");
        Serial.print(temperature);
        Serial.print(" °C, RSSI: ");
        Serial.println(LoRa.packetRssi());
      }
      break;
    }
    
    case MSG_HEARTBEAT: {
      uint8_t senderMAC[6];
      for (int i = 0; i < 6; i++) senderMAC[i] = LoRa.read();
      
      int nodeIdx = findNode(senderMAC);
      if (nodeIdx >= 0) {
        nodes[nodeIdx].lastSeen = millis();
        nodes[nodeIdx].rssi = LoRa.packetRssi();
      }
      break;
    }
    
    case MSG_RSSI_REPORT:
      handleRoutingReport();
      break;
  }
}

void checkNodeHealth() {
  static unsigned long lastCheck = 0;
  if (millis() - lastCheck < 10000) return;
  lastCheck = millis();
  
  bool routingChanged = false;
  
  for (int i = 0; i < nodeCount; i++) {
    if (nodes[i].active && (millis() - nodes[i].lastSeen > HEARTBEAT_TIMEOUT)) {
      Serial.print("Node ");
      Serial.print(i + 1);
      Serial.println(" appears offline");
      nodes[i].active = false;
      routingChanged = true;
    }
  }
  
  if (routingChanged) {
    Serial.println("Routing table changed, recalculating...");
    performDiscovery();
  }
}

void displayRoutingTable() {
  Serial.println("\n=== Routing Table ===");
  Serial.println("ID | MAC Address       | RSSI | Hops | Via  | Path RSSI");
  Serial.println("---+-------------------+------+------+------+----------");
  
  for (int i = 0; i < nodeCount; i++) {
    Serial.print(" ");
    Serial.print(i + 1);
    Serial.print(" | ");
    printMAC(nodes[i].macAddress);
    Serial.print(" | ");
    Serial.print(nodes[i].rssi);
    Serial.print(" | ");
    Serial.print(nodes[i].hopCount);
    Serial.print("    | ");
    if (nodes[i].viaNode == 0) {
      Serial.print("DIR  | ");
    } else {
      Serial.print(nodes[i].viaNode);
      Serial.print("    | ");
    }
    Serial.println(nodes[i].pathRSSI);
  }
  Serial.println("=====================\n");
}

void printMAC(uint8_t* mac) {
  for (int i = 0; i < 6; i++) {
    if (mac[i] < 0x10) Serial.print("0");
    Serial.print(mac[i], HEX);
    if (i < 5) Serial.print(":");
  }
}
