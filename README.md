# AquaBot Marine Water Quality Data Pipeline

## Overview
This repository contains a full-stack data ingestion, anomaly detection, and visualization pipeline for AquaBot surveys. Marine data inevitably contains noisy readings. Sensors drift, collect biofouling, glitch, or simply report impossible edge cases. 

This pipeline aims to parse the corrupted data reliably, highlight out-of-bounds readings, detect context-based anomalies, and serve the results cleanly on an interactive dashboard.

---

## 🚀 Quick Start

Ensure you have Python 3.9+ installed.

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Development Server**
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. **Access the Dashboard**
   Open your browser and navigate to: `http://localhost:8000/`

---

## 🏗️ Project Architecture

The application focuses on simplicity, responsiveness, and minimal overhead for ease of deployment.

- **Backend Framework**: Built with **FastAPI**. Chosen for its asynchronous speed and capability of self-hosting the REST API endpoints and static frontend simultaneously.
- **Data Engine**: **Pandas** handles the heavy lifting via in-memory dataframe manipulations. It ensures high-speed vectorized operations suitable for smaller deployments.
- **Frontend Layer**: Crafted using high-fidelity **Vanilla HTML/CSS/JS**. The UI eliminates the need for heavyweight frontend frameworks while offering an incredibly aesthetic **Deep Marine Environment** design (Glassmorphism layout + glowing accent traces).
- **Visualization engine**: **Plotly.js** powers the responsive web charts. It elegantly separates primary data points from overlayed anomalies.

---

## 🧠 Anomaly Detection Strategies

The pipeline cleans structural timestamp errors on instantiation, before applying the following dual-layered anomaly detection logic:

### 1. Range Validation
- **What it does**: Cross-check telemetry bounds against standard marine physical constants (e.g., Turbidity cannot be negative; Dissolved Oxygen generally sits between 4.0 - 12.0 mg/L).
- **Why we chose this**: Some errors are catastrophic hardware faults where sensors report nonsensical extreme values. Hard constraint checking prevents downstream processing from being biased by mathematically impossible data points.

### 2. Rolling Window Z-Score
- **What it does**: Computes local moving averages and standard deviations over a specific window of observation (e.g., 6 contiguous readings or ~1 hour). Data points exceeding a threshold `Z-Score` factor (typically `> 3.2`) are flagged as anomalous spikes/drops.
- **Why we chose this**: Often, sensors fail 'quietly'. For example, an unexpected sudden change from `pH 8.1` to `pH 7.6` in a span of 10 minutes is completely valid locally within the context of physical minimums, but mathematically highly suspicious compared to the localized surrounding rolling window. The rolling Z-Score handles sudden shifts perfectly.

---

## 🔭 Discussion & Future Improvements

If scaling this system to handle multi-year autonomous deployments or extremely high-frequency readings, and moving towards production, here is the immediate roadmap:

### 1. Scaling for High-Frequency Data
To handle years of high-frequency data (e.g., readings every second), we would transition from an in-memory Pandas dataframe to a dedicated time-series database (TSDB) like **InfluxDB** or **TimescaleDB**. The data ingestion could be decoupled using a message broker (like Apache Kafka, MQTT or RabbitMQ) to buffer incoming sensor streams, and anomaly detection could run asynchronously via distributed workers to prevent blocking the ingestion pipeline.

### 2. Edge Processing vs. Cloud Processing
Running anomaly detection on the edge (e.g., Raspberry Pi on the AquaBot) vs. the cloud involves distinct tradeoffs:
- **Edge Processing**: Reduces telemetry bandwidth and enables real-time autonomous reaction (e.g., surfacing if critical sensors fail). However, onboard compute is limited, power consumption increases, and updating models requires over-the-air updates.
- **Cloud Processing**: Offers vast compute for complex machine learning models, easier system updates, and holistic analysis across an entire bot fleet. The downside is reliance on potentially spotty marine data connections.
- **Ideal Setup**: A hybrid approach. The edge runs lightweight checks (like Range Validation) to trigger immediate safety alerts or discard clearly corrupted packets, while the cloud runs the intensive rolling historical checks and deep learning models.

### 3. Handling Sensor Calibration Drift
Sensor drift is tricky because readings remain physically valid but slowly lose accuracy. To tackle this, we could:
- **Baseline Drift Compensation**: Use long-term moving averages (over weeks instead of hours) to detect slow, steady monotonic trends that do not correlate with natural cyclical patterns.
- **Redundant Sensor Voting**: Compare readings with secondary on-board sensors. If the primary optical DO sensor shows a slow decline while the galvanic DO sensor is stable, flag as probable drift.

### 4. Production Alerting System
For a true production alerting system, passive logging isn't enough:
- **Alert Triage/Debouncing**: Implement a rule-engine to prevent notification spam. A single anomaly might just be logged, but 5 consecutive anomalies within 10 minutes escalates to an alert.
- **Push Notifications & Webhooks**: Dispatch critical severity alerts to Slack, Microsoft Teams, or PagerDuty for on-call researchers. 
- **Live UI Updates**: Transition the dashboard to Server-Sent Events (SSE) or WebSockets to display notifications instantly as data streams in.
