# 📡 Dynamic RSSI-Based Multi-Hop LoRa Routing (ESP32 + SX1278)

## 📌 Project Overview

This project implements a **dynamic, RSSI-based multi-hop routing mechanism** for a LoRa wireless network using **ESP32** microcontrollers and **SX1278 LoRa modules**. The system is capable of **automatic node discovery, adaptive path selection, and fault-tolerant routing** without relying on fixed node roles or a predefined network topology.

The routing strategy dynamically selects the most reliable communication path based on **Received Signal Strength Indicator (RSSI)** values and automatically switches routes in the event of node or link failure, making it suitable for **low-power, distributed IoT deployments**.

---

## 🚀 System Overview

* One **Master Node**
* Multiple **Slave Nodes** (identical firmware)
* Long-range communication via **LoRa (SX1278)**
* **RSSI-based adaptive routing**
* Automatic **failover and route switching**
* Optimized for **low-power operation**

The system is designed for environments where **node locations are unknown, dynamic, or subject to change**, such as outdoor sensor deployments.

---

## 🧠 Core Routing Concept

* Nodes closer to the master exhibit **higher RSSI values**
* Distant nodes forward data through nearer relay nodes
* Multiple routing paths may exist simultaneously
* The route with the **highest cumulative RSSI** is selected
* If a relay node fails, the system **automatically switches** to the next best available path

---

## 📐 Example Network Topology

```
        Master
         |
     +---+---+
     |       |
   Node 1   Node 2
     \       /
      \     /
       Node 3
```

* **Node 1 & Node 2** are closer to the master
* **Node 3** is farther away and routes data via Node 1 or Node 2
* Best routing path is selected dynamically using RSSI

---

## 🔄 Protocol Workflow

### 1️⃣ Node Discovery

* Master node broadcasts a discovery poll
* All slave nodes respond with RSSI information
* Nodes are ranked based on signal strength

### 2️⃣ Logical Role Assignment

* Nodes are logically labeled according to RSSI strength
* No fixed roles are hardcoded in firmware
* Same firmware runs on all slave nodes

### 3️⃣ Inter-Node RSSI Measurement

* Stronger nodes poll weaker nodes
* RSSI between nodes is measured
* Each node computes:

```
Total RSSI = RSSI(Master ↔ Relay) + RSSI(Relay ↔ Node)
```

### 4️⃣ Best Path Selection

* Node selects the relay with the highest total RSSI
* Routing table is updated locally

### 5️⃣ Data Transmission

* Sensor data is forwarded via the selected relay
* Example payload: temperature data (sensor-based or simulated)

### 6️⃣ Automatic Failover

* If the active relay node fails:

  * Node switches to a backup route automatically
  * No master intervention is required

---

## 📦 Packet Structure

```
TYPE | SOURCE | DESTINATION | PAYLOAD
```

### Packet Types

| Type | Description                       |
| ---: | --------------------------------- |
|    P | Poll message                      |
|    A | Acknowledgment with RSSI feedback |
|    R | Routing / role information        |
|    D | Sensor data payload               |

---

## 🔋 Power Management Strategy

* Nodes operate in **low-power modes**
* Wake-up events include:

  * Poll reception
  * Periodic timer interrupts
  * Significant sensor data changes

This design supports **battery-powered LoRa sensor nodes** for long-term deployments.

---

## 🛠️ Hardware & Software Stack

### 🔧 Hardware Components

| Component          | Description                |
| ------------------ | -------------------------- |
| ESP32 Dev Module   | Main controller            |
| SX1278             | LoRa transceiver           |
| Temperature Sensor | Data source (or simulated) |

### 💻 Software Tools

* Arduino IDE
* LoRa.h library (Sandeep Mistry)
* SPI communication interface

---

## 📄 Code Structure

```
/master
  └── master.ino

/slave
  └── slave.ino   // Identical firmware for all slave nodes
```

🔧 Only the `NODE_ID` parameter is modified per slave device.

---

## 🔁 Key Features

* ✔ Dynamic multi-hop routing
* ✔ RSSI-based path selection
* ✔ Automatic route switching on failure
* ✔ No fixed node roles
* ✔ Identical slave firmware
* ✔ Low-power friendly design
* ✔ Scalable for small LoRa networks

---

## 📈 Application Domains

* Wireless Sensor Networks (WSN)
* Structural Health Monitoring systems
* Smart agriculture deployments
* Remote environmental monitoring
* IoT-based data collection platforms

---

## 🎓 Academic Relevance

This project demonstrates practical implementation of:

* LoRa-based wireless networking
* Adaptive and fault-tolerant routing algorithms
* Energy-efficient IoT system design

It is suitable for **Final Year Projects (FYP)**, research prototypes, and experimental IoT networks.

---

## 🔮 Future Enhancements

* Integration of Link Quality Indicator (LQI)
* Adaptive polling intervals
* Multi-metric routing (RSSI + latency + battery level)
* AES-based encryption
* Scalability toward larger mesh networks

---

## 🤝 Contributors

Final Year Project Team
Faculty of Engineering
University of Peradeniya, Sri Lanka

---

## 📜 License

This project is intended for **academic and research purposes** only.
