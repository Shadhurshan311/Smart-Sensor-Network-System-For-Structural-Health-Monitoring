#include <SPI.h>
#include <LoRa.h>

#define MASTER_ID 0x00

void setup() {
  Serial.begin(9600);
  LoRa.begin(433E6);
}

void loop() {
  // DISCOVERY
  LoRa.beginPacket();
  LoRa.print("P,0,ALL,DISCOVER");
  LoRa.endPacket();

  delay(2000);

  // RECEIVE ACKS
  while (LoRa.parsePacket()) {
    String msg = LoRa.readString();
    int rssi = LoRa.packetRssi();
    Serial.println("RX: " + msg + " RSSI: " + String(rssi));
  }

  delay(10000);
}

