# Self-Healing SDN Controller Framework
### Phase 1: Monitoring and Telemetry Layer

### Project Overview
This project aims to build a self-healing Software-Defined Networking (SDN) framework capable of autonomously detecting, diagnosing, and recovering from network failures. 

**Current Status:** The **Monitoring and Telemetry Layer** is fully implemented. This layer acts as the sensory system of the framework, collecting real-time data from the control plane and data plane to feed into the future Anomaly Detection Engine.

---

## System Architecture (Implemented)
We have established a decoupled monitoring architecture that separates data collection from network control:

1. **Network Infrastructure Layer (Mininet):** A simulated data plane featuring a custom "Triangle Loop" topology. It includes redundant physical links and Spanning Tree Protocol (STP) configuration to facilitate link failure simulations and dynamic path rerouting.

2. **Control Plane (Ryu Controller):** The centralized SDN orchestration logic that manages OpenFlow switches. It runs a custom application to handle packet routing and exposes real-time network state metrics (counters, flow stats) via a dedicated northbound REST API.

3. **Telemetry & Feature Engineering Engine (Python Agent):** A dedicated data aggregation module that polls the Control Plane, computes derivative metrics (such as throughput rates and latency variations), performs statistical normalization (Z-score calculation), and serializes the data for consumption.

4. **Visualization & Time-Series Layer (Grafana + Prometheus):** A monitoring stack comprising a time-series database (Prometheus) for metric storage and a real-time dashboard (Grafana) for visual analysis of network health and performance trends.

5. **Training Data Repository (CSV Logging):** An automated logging system that generates structured, labeled datasets containing the specific 8 LSTM and 12 Isolation Forest features required for training the Machine Learning Anomaly Detection models.

---

## Directory Structure
```text
self-heal-sdn/
├── controller_apps/
│   └── sh_controller.py       # Ryu App with REST API & Traffic Counters
├── mininet_topology/
│   └── topo_healing.py        # Triangle Topology with STP & Link Failure support
├── monitoring_and_telemetry/
│   ├── config/
│   │   └── settings.yaml      # Configuration for IP, ports, and thresholds
│   ├── logs/
│   │   └── training_data.csv  # The ML-Ready Dataset
│   └── telemetry_agent.py     # Main script for Feature Extraction & logging
└── README.md
````

-----

## Component Details

### 1\. Network Topology (`topo_healing.py`)

  * **Features:** Implements a triangle topology with redundant links (`s1-s2`, `s2-s3`, `s3-s1`).
  * **Loop Prevention:** Explicitly enables Spanning Tree Protocol (STP) on Open vSwitch to prevent broadcast storms during loop conditions.
  * **Failure Simulation:** Allows manual link degradation and failure via the Mininet CLI (`link s1 s2 down`).

### 2\. Custom Controller (`sh_controller.py`)

  * **Base:** Built on the Ryu SDN Framework.
  * **Telemetry API:** Exposes a custom REST endpoint (`/stats/sh_features`) that provides atomic counters for `packet_in`, `packet_out`, and `flow_mod`.
  * **Amnesia Mode (Data Generation):** Configured to forcefully route packets via the controller (Control Plane) rather than installing permanent flows. This maximizes data granularity for ML training during the data collection phase.

### 3\. Telemetry Agent (`telemetry_agent.py`)

This is the core monitoring engine. It performs three key tasks:

1.  **Ingestion:** Scrapes raw metrics from the Controller API and System (CPU/RAM).
2.  **Feature Engineering:** transform raw counters into rates (e.g., `packet_in_rate = Δpackets / Δtime`) and statistical metrics (Z-Scores).
3.  **Export:** Pushes live metrics to Prometheus/Grafana and logs history to CSV.

-----

## Features Implemented

The Telemetry Agent automatically generates the exact feature set required by the Anomaly Detection Engine.

#### LSTM Features (Temporal Analysis)

These 8 features are logged to support Time-Series forecasting:

1.  `lstm_cpu`: Controller CPU Load
2.  `lstm_mem`: Controller Memory Usage
3.  `lstm_rtt`: Controller-Switch Latency
4.  `lstm_pkt_in`: Packet-In Rate (Control Plane Load)
5.  `lstm_pkt_out`: Packet-Out Rate (Response Activity)
6.  `lstm_flow_mod`: Flow Modification Rate
7.  `lstm_flows_sec`: New Flows per Second
8.  `lstm_bw`: Bandwidth Usage

#### Isolation Forest Features (Snapshot Analysis)

These 12 features are logged to support outlier detection:

1.  `if_cpu`: CPU Snapshot
2.  `if_mem`: Memory Snapshot
3.  `if_rtt`: Latency Snapshot
4.  `if_pkt_in`: Packet-In Burst detection
5.  `if_pkt_out`: Packet-Out Snapshot
6.  `if_flow_mod`: Flow-Mod Snapshot
7.  `if_table_occ`: Flow Table Occupancy
8.  `if_link_loss`: Link State Status
9.  `if_bw`: Bandwidth Snapshot
10. `if_churn`: Flow Churn Rate
11. `if_zscore_avg`: Statistical deviation of CPU (Z-Score)
12. `if_ratio_pkt_flow`: Ratio of Packets to Flow Mods (Efficiency Metric)

-----

## How to Run the Monitoring Layer

The system requires three separate terminals to run the architectural components in parallel.

**Terminal 1: The Controller**

```bash
cd controller_apps
ryu-manager sh_controller.py --verbose --ofp-tcp-listen-port 6633
```

**Terminal 2: The Network (Mininet)**

```bash
cd mininet_topology
sudo python3 topo_healing.py
# Wait 45s for STP convergence before typing commands
```

**Terminal 3: The Telemetry Agent**

```bash
cd monitoring_and_telemetry
python3 telemetry_agent.py
```

```
```
