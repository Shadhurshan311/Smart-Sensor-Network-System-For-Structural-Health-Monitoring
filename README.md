# 🏗️ Smart Sensor Network System for Structural Health Monitoring

## 📌 Project Overview

The **Smart Sensor Network System for Structural Health Monitoring (SHM)** is a final-year undergraduate engineering project focused on the early detection, characterization, and classification of cracks in concrete structures using a combination of **computer vision, embedded sensing, thermal analysis, and machine learning**.

The system integrates vision-based crack localization, custom-built and environmental sensors, thermal imaging, and AI-driven classification models within a networked IoT architecture. A **master–slave communication framework** enables synchronized data collection from multiple sensor nodes, centralized processing, and scalable system expansion for real-world structural monitoring applications.

---

## 🎯 Project Objectives

* Detect and localize surface cracks using image processing techniques
* Monitor crack behavior using custom-designed and environmental sensors
* Analyze thermal signatures to enhance crack characterization
* Fuse multi-modal data for robust machine learning-based classification
* Enable real-time prediction of crack presence, severity, and type
* Implement a scalable master–slave sensor network architecture
* Support future cloud-based monitoring and long-term data analytics

---

## ⚙️ System Architecture & Workflow

The system follows a multi-layer SHM pipeline, combining sensing, intelligence, and communication.

### 1️⃣ Vision-Based Crack Localization

* Structural surface images captured using drones and handheld cameras
* Image preprocessing including grayscale conversion, filtering, and enhancement
* Crack localization using OpenCV-based image processing techniques

### 2️⃣ Sensor Deployment & Data Acquisition

* Sensors deployed at identified crack-prone locations
* Integrated sensing includes:

  * Custom capacitive crack sensor (crack width and variation)
  * Temperature and humidity sensing
  * Thickness measurement
* Thermal camera analysis used to study subsurface crack behavior and heat distribution

### 3️⃣ Multi-Modal Data Collection

* Synchronized acquisition of:

  * Sensor signals
  * Image-derived features
  * Thermal data
* Data stored and structured using CSV-based data modeling for analysis and training

### 4️⃣ Machine Learning & Feature Engineering

* Automated feature extraction from sensor, image, and thermal data
* Machine learning models implemented and evaluated:

  * Support Vector Machine (SVM)
  * XGBoost
  * Multi-Layer Perceptron (MLP – PyTorch)
* Model optimization using hyperparameter tuning, grid search, and cross-validation

### 5️⃣ Networked Operation & Communication

* ESP32-based master–slave architecture with multiple slave sensor nodes
* Custom communication protocol designed for:

  * Reliable data aggregation
  * Low-latency transmission
  * Synchronized node operation
* Centralized processing with support for gateway-level data forwarding

### 6️⃣ Real-Time Prediction & Analysis

* Preliminary ML-based inference performed on collected data
* Outputs include crack detection, classification, and severity indicators
* Designed for extension to cloud-based monitoring platforms

---

## 🔧 Key System Features

* Vision-based crack detection and localization
* Custom-designed capacitive crack sensor
* Multi-parameter sensing (capacitance, temperature, humidity, thickness)
* Thermal image analysis for enhanced crack characterization
* Multi-modal data fusion for improved prediction robustness
* AI/ML-based crack classification using SVM, XGBoost, and MLP
* Master–slave sensor network with custom communication protocols
* Modular and scalable IoT-oriented system design

---

## 🧠 Design & Development Highlights

* **Computer Vision:** OpenCV-based crack localization and feature extraction
* **Sensor Engineering:** Design, fabrication, and calibration of custom capacitive sensors
* **Data Engineering:** Real-world dataset creation, labeling, and normalization
* **Machine Learning:** End-to-end pipeline from feature engineering to real-time inference
* **Networking:** Distributed sensor nodes with synchronized communication
* **Thermal Analysis:** Non-invasive defect characterization using thermal imaging

---

## 🛠️ Technologies, Tools & Components

### 📷 Imaging & Thermal Analysis

| Component      | Description                 |
| -------------- | --------------------------- |
| Cameras        | Drones, handheld cameras    |
| Thermal Camera | Crack heat-pattern analysis |
| Tools          | OpenCV, image preprocessing |

### 🔧 Sensors & Embedded Hardware

| Component                     | Purpose                             |
| ----------------------------- | ----------------------------------- |
| Capacitive Crack Sensor       | Crack width and variation detection |
| Temperature & Humidity Sensor | Environmental monitoring            |
| Thickness Sensor              | Structural parameter measurement    |
| Microcontroller               | ESP32                               |

### 🤖 Machine Learning & Data Processing

| Category     | Tools / Models                   |
| ------------ | -------------------------------- |
| ML Models    | SVM, XGBoost, MLP (PyTorch)      |
| Techniques   | Feature engineering, data fusion |
| Optimization | Grid search, cross-validation    |
| Output       | Real-time crack classification   |

### 🌐 Communication & Networking

| Category     | Details                         |
| ------------ | ------------------------------- |
| Architecture | Master–Slave                    |
| Protocols    | Custom embedded communication   |
| Data Format  | CSV-based modeling              |
| Integration  | Gateway-ready, cloud extensible |

---

## 🎓 Academic Context

| Item           | Details                             |
| -------------- | ----------------------------------- |
| Project Type   | Final Year Project (FYP)            |
| Degree Program | Electrical & Electronic Engineering |
| Focus Areas    | AI & ML, Embedded Systems, IoT, SHM |

---

## 🚀 Learning Outcomes

* Practical experience in AI-driven structural health monitoring
* Integration of computer vision, sensors, and machine learning
* Design of custom sensors and embedded firmware
* Development of real-world ML pipelines
* Understanding of distributed sensor networks and protocols
* Exposure to thermal analysis for non-invasive inspection

---

## 📌 Conclusion

The **Smart Sensor Network System for Structural Health Monitoring** demonstrates a comprehensive approach to modern infrastructure monitoring by combining embedded sensing, thermal analysis, computer vision, and machine learning within a networked IoT framework. The project highlights how intelligent data fusion and communication-aware system design can enable reliable, scalable, and real-time structural health assessment for future smart infrastructure applications.

---

## 👤 Authors

**Sarusan Sivanesan**
Electrical & Electronics Engineering Undergraduate
University of Peradeniya, Sri Lanka

**Ashwinthan Gobinath Kulathunga**
Electrical & Electronics Engineering Undergraduate
University of Peradeniya, Sri Lanka

**Shadhurshan Navaretnam**
Electrical & Electronics Engineering Undergraduate
University of Peradeniya, Sri Lanka

---

## 🎓 Supervisors

**Prof. Maheshi B. Dissanayake**
Professor, Dept. of Electrical & Electronic Engineering
University of Peradeniya, Sri Lanka

* B.Sc. Eng. (First Class Honours, Electrical & Electronic Engineering), University of Peradeniya, 2006
* Ph.D. in Electronic Engineering, University of Surrey, UK, 2010
* Email: [maheshi.dissanayake@eng.pdn.ac.lk](mailto:maheshid@eng.pdn.ac.lk)

**Dr. H. A. D. Samith Buddika**
Senior Lecturer, Department of Civil Engineering
University of Peradeniya, Sri Lanka

* BSc.Eng (First class Hons) , University of Peradeniya, Peradeniya, Sri Lanka (Civil Eng.), 2009
* M.Eng., Tokyo Institute of Technology, Tokyo, Japan (Structural Eng/Earthquake Eng.), 2013.
* PhD, Tokyo Institute of Technology, Tokyo, Japan (Structural Eng/Earthquake Eng.), 2017.
* Email: [samithbuddika@eng.pdn.ac.lk](mailto:samithbuddika@eng.pdn.ac.lk)

---

## 📜 License

This project is developed **strictly for academic and educational purposes** at the **University of Peradeniya, Sri Lanka**.
Unauthorized commercial use or reproduction without proper acknowledgment is not permitted.

---


⭐ *This repository documents the complete Final Year Project, encompassing Phase I (sensing, image processing, and machine learning–based crack detection) and Phase II (distributed sensor networking, communication protocols, and thermal image analysis) within an integrated structural health monitoring system.*


