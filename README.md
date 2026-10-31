# 🛡️ FinGraph: Real-Time Financial Fraud Syndicate & Graph Network Analytics
> **Enterprise Financial Intelligence & Anti-Money Laundering (AML) Platform**  
> *Developed by **Sujal** | Infotact Solutions Virtual Internship Project 1*

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Neo4j GDS](https://img.shields.io/badge/Neo4j-Graph%20Data%20Science-008CC1?logo=neo4j&logoColor=white)](https://neo4j.com/)
[![Apache Kafka](https://img.shields.io/badge/Streaming-Apache%20Kafka-231F20?logo=apachekafka&logoColor=white)](https://kafka.apache.org/)
[![Apache Flink](https://img.shields.io/badge/Stream%20Processing-Apache%20Flink-E6526F?logo=apacheflink&logoColor=white)](https://flink.apache.org/)
[![Streamlit](https://img.shields.io/badge/Live%20App-Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)

---

## 📌 Executive Summary & Problem Statement

Modern financial crime syndicates evade legacy rule-based detection systems by distributing illicit capital across hundreds of seemingly unrelated accounts before routing funds into offshore tax havens (Panama, Cayman Islands, Switzerland, Bahamas). Traditional tabular databases (SQL/Relational) fail to detect these multi-hop relationships because querying recursive relationships requires computationally expensive self-joins ($O(N^k)$ complexity).

**FinGraph** models millions of financial transactions as a **Directional Graph Network** $G = (V, E)$, where accounts represent vertices ($V$) and money flows represent weighted, timestamped edges ($E$). By combining **Distributed Stream Ingestion (Kafka/Flink)**, **Graph Data Science (GDS) algorithms**, and a **Real-Time Rules Engine**, FinGraph identifies and neutralizes coordinated money laundering rings with sub-second latency.

---

## 🏗️ System Architecture & End-to-End Pipeline

```
  +---------------------------------------------------------------------------------+
  |                             FinGraph Event Pipeline                             |
  +---------------------------------------------------------------------------------+
                                         |
                                         v
   +-------------------+       +--------------------+       +-------------------+
   |   Synthetic TX    | ----> |    Apache Kafka    | ----> |   Apache Flink    |
   | Generator Engine  |       |  Topic: tx_stream  |       | Complex Event (CEP)|
   +-------------------+       +--------------------+       +-------------------+
                                                                      |
                                         +----------------------------+
                                         |
                                         v
   +----------------------------------------------------------------------------+
   |                       Graph Database & Analytics                           |
   +----------------------------------------------------------------------------+
   |  • Neo4j Graph Database: (Account)-[:TRANSFERRED_TO]->(Account)            |
   |  • Louvain Modularity: Uncovers synthetic money mule communities           |
   |  • PageRank & Degree Centrality: Identifies orchestrator hubs              |
   |  • Weakly Connected Components (WCC): Maps isolated laundering clusters     |
   +----------------------------------------------------------------------------+
                                         |
                                         v
   +----------------------------------------------------------------------------+
   |                     Security Alerting & Visual Operations                  |
   +----------------------------------------------------------------------------+
   |  • Cyber-Fintech Operations Console (Flask SSE Real-Time Stream)           |
   |  • Interactive Cloud Analytics App (Streamlit Community Cloud)             |
   |  • 1-Click "Freeze Account" automated AML intervention hook               |
   +----------------------------------------------------------------------------+
```

---

## 🎯 Coordinated Fraud Pattern Recognition

FinGraph is specifically engineered to flag the 3 primary stages of international money laundering:

```
  [ 1. PLACEMENT ]            [ 2. LAYERING ]                  [ 3. INTEGRATION ]
Small structured deposits   Rapid multi-hop transfers         Consolidation into
below $10,000 threshold     across 5+ intermediate "Mules"    Offshore Shell Entities
       │                              │                                  │
       ▼                              ▼                                  ▼
[ Smurf Accounts ] ───────> [ Mule Network (Fan-Out) ] ───────> [ Offshore Tax Haven ]
```

1. **Smurfing / Structuring:**
   - Automated detection of micro-deposits deliberately capped below reporting thresholds (e.g., $\$9,900$) across short timeframes.
2. **Mule Fan-In & Fan-Out Networks:**
   - High in-degree centrality nodes aggregating funds from dozens of smurfs and dispersing them within seconds.
3. **Offshore Tax-Haven Flight:**
   - Cross-border transfers originating from domestic accounts and terminating in non-cooperative offshore banking jurisdictions (Panama, Cayman Islands, Switzerland, Bahamas).

---

## 🧠 Graph Data Science (GDS) & Centrality Metrics

| Algorithm | Graph Topology Metric | Operational AML Objective |
| :--- | :--- | :--- |
| **Louvain Modularity** | Community Detection | Identifies tightly-bound criminal syndicates operating in collusion. |
| **PageRank** | Influx / Prestige Centrality | Pinpoints the ultimate beneficiary accounts collecting laundered funds. |
| **Betweenness Centrality** | Bridge Frequency | Detects money mule middlemen connecting disparate criminal clusters. |
| **Weakly Connected Components** | Subgraph Isolation | Segregates isolated laundering rings from normal retail traffic. |

---

## 📊 Live Operations Dashboard

FinGraph provides two operational interfaces:

1. **Cyber-Fintech Operations Console (`app.py` / Flask)**:
   - High-throughput Server-Sent Events (SSE) streaming live transactions at 60 FPS.
   - Real-time audit metrics: Total Scanned, High-Risk Accounts, Intercepted Capital.
   - Instant "Freeze Account" security triggers with incident logging.
2. **Interactive Cloud App (`streamlit_app.py` / Streamlit Cloud)**:
   - Interactive NetworkX graph visualizer color-coded by node risk.
   - Dynamic threshold filters for transaction amounts and fraud patterns.
   - Automated Suspicious Activity Report (SAR) CSV/JSON export.

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/sujalborisha-blip/FinGraph-Analytics-.git
cd FinGraph-Analytics-
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch with Streamlit (Recommended)
```bash
streamlit run streamlit_app.py
```

### 4. Launch with Flask Operations Console
```bash
# Terminal 1: Run transaction simulator
python simulator.py

# Terminal 2: Run Flask dashboard
python app.py
```
Open your browser at `http://127.0.0.1:5000`.

---

## 📂 Project Structure

```
FinGraph-Analytics-/
├── app.py                      # Flask Server-Sent Events (SSE) web server
├── streamlit_app.py            # Streamlit Cloud interactive analytical app
├── simulator.py                # Synthetic transaction stream generator (Faker)
├── rules_engine.py             # Real-time pattern detection & alerting engine
├── analytics.py                # Batch syndicate fraud reporting engine
├── flink_processor.py          # Apache Flink stream processing interface
├── kafka_producer.py           # Kafka broker topic producer
├── accounts.json               # Account database (Normal, Mules, Offshore)
├── transactions.log            # Audit trail ledger
├── requirements.txt            # Python dependencies
├── neo4j/                      # Cypher queries, constraints & GDS schema
│   ├── constaints.cypher.txt
│   ├── graph_algorithms.cypher
│   ├── optimization.cypher
│   ├── sample_data.cypher
│   └── schema.md
└── templates/                  # Cyber-Fintech UI templates
    └── index.html
```

---

## 👨‍💻 Author & Acknowledgements

* **Lead Analyst:** Sujal
* **Internship Program:** Infotact Solutions Virtual Data Analytics Internship
* **Domain Specialization:** Graph Theory, Financial Risk Analytics & Big Data Systems
