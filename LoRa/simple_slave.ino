#include <SPI.h>
#include <LoRa.h>

#define NODE_ID 0x03   // change only this
int bestNextHop = MASTER_ID;
int rssiToMaster = -200;

void setup() {
  Serial.begin(9600);
  LoRa.begin(433E6);
}

void loop() {
  int packetSize = LoRa.parsePacket();
  if (packetSize) {
    String msg = LoRa.readString();
    int rssi = LoRa.packetRssi();

    if (msg.startsWith("P,0")) {
      // Master poll
      rssiToMaster = rssi;

      LoRa.beginPacket();
      LoRa.print("A," + String(NODE_ID) + ",0," + String(rssi));
      LoRa.endPacket();
    }

    if (msg.startsWith("P")) {
      // Inter-node poll
      LoRa.beginPacket();
      LoRa.print("A," + String(NODE_ID) + ",NODE," + String(rssi));
      LoRa.endPacket();
    }
  }

  sendSensorData();
  delay(15000);
}

void sendSensorData() {
  float temp = random(250, 350) / 10.0;

  LoRa.beginPacket();
  LoRa.print("D," + String(NODE_ID) + "," + String(bestNextHop) +
             ",TEMP=" + String(temp));
  LoRa.endPacket();
}
