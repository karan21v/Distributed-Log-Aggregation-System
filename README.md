# Distributed-Log-Aggregation-System

##  Project Overview
This project is an enterprise-grade **Distributed Log Aggregator** designed to handle high-throughput telemetry data from hundreds of remote nodes. Operating over the User Datagram Protocol (UDP) for maximum ingestion speed, the system solves the inherent challenges of UDP (packet loss and out-of-order delivery) using custom data structures and congestion control algorithms.

Coupled with an **Enterprise Network Operations Center (NOC) Dashboard**, this system provides real-time observability into network latency, processing throughput, and individual machine health within the distributed cluster.

#  Core Features & Technical Achievements

* **Min-Heap Jitter Buffer:** UDP does not guarantee chronological packet delivery. This server implements a priority queue (`heapq`) to sort incoming packets by their generation timestamp, re-sequencing the data stream before writing it to the disk.
* **Dynamic Backpressure (Congestion Control):** To prevent memory exhaustion during a DDoS attack or network flood, the server enforces a strict `MAX_QUEUE` limit. Packets exceeding this limit are intentionally dropped at the network boundary, ensuring the server remains online.
* **Cryptographic Security:** All telemetry data is encrypted in transit using symmetric key encryption (`cryptography.fernet`), protecting system logs from packet sniffing.
* **Dual-Pane Telemetry Visualization:** A 300+ line Tkinter dashboard featuring live Matplotlib charts, allowing administrators to compare the raw inbound stream against the processed verdict stream.

##  System Architecture

1. **The Producers (`generator.py`):** A multi-threaded simulation of distributed servers. Each thread securely transmits randomized log events (INFO, WARN, ERROR) over UDP.
2. **The Aggregator (`server.py`):** The central consumer. It decrypts incoming packets, buffers them in a Min-Heap, calculates network jitter, and flushes sorted batches to an aggregated log file.
3. **The NOC Dashboard (`gui.py`):** The presentation layer. It tails the aggregated log file to update KPI cards, dynamic charts, and node-wise health metrics in real-time.

---

##  Installation & Setup

**1. Clone the repository**
```bash
git clone [https://github.com/karan21v/Distributed-Log-Aggregation-System)
cd distributed-log-aggregator
