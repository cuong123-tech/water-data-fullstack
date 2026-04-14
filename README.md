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

If scaling this system to handle multi-year autonomous deployments or extremely high-frequency readings, here is the immediate roadmap:

