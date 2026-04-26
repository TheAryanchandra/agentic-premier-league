# 🏟️ Stadium Pulse: AI-Driven IPL Venue Management

**Stadium Pulse** is a high-performance, real-time command center and fan engagement dashboard designed for the IPL 2026 match (DC vs Punjab). It transforms stadium management from reactive chaos into predictive coordination.

## 🔗 Live Demo
👉 **[Stadium Pulse Live Dashboard](https://storage.googleapis.com/aryan-487709-stadium-dashboard/index.html)**

---

## 🌍 The Real-Life Impact: Why This Matters

Large-scale sporting events are high-entropy environments where **Information Asymmetry** leads to danger and frustration. **Stadium Pulse** solves three critical real-world problems:

1. **Stampede Prevention**: By using AI to predict density 10 minutes into the future, stadium staff can preemptively close gates or redirect flow *before* a bottleneck becomes a crush risk.
2. **The "Silent Emergency"**: In a crowd of 50,000, a medical emergency can go unnoticed for minutes. Our **Priority SOS** provides a 1-second trigger to alert HQ with precise coordinates.
3. **Utility Load Balancing**: Most fans rush to the nearest restroom or food stall. Our dashboard directs fans to "Ideal" zones, spreading the load across the venue and reducing average wait times by up to 40%.

---

## 🚀 Main ML Features

### 1. Neural-Trend Crowd Forecasting
The system uses **Linear Regression-based Trend Analysis** to process real-time ingress data. It calculates moving averages and growth vectors to predict crowd density in:
- **5-Minute Window**: Short-term tactical projection.
- **10-Minute Window**: Strategic planning projection.

### 2. Predictive Queue Modeling
An automated reasoning engine evaluates the forecasted density against safety thresholds to provide **Actionable Recommendations**:
- **✅ OK**: Safe occupancy levels; fans encouraged to visit.
- **⚠️ AVOID**: High congestion predicted; fans advised to delay movement to that zone.

---

## 🎮 Dual-Mode Command Architecture

### 🛡️ For Fans (The Mobile Experience)
- **Priority SOS**: Moved to the top for immediate access during emergencies. Fans can broadcast "Rapid Response" signals with location tracking.
- **Real-Time Heatmaps**: Visual indicators (Safe/Crowded/Danger) for every stadium stand and utility zone.
- **Trip Planning**: AI recommendations on the best times to visit food courts or restrooms.

### 🕹️ For Admins (Mission Control)
- **Operational Overrides**: Toggle zones between `Active`, `Maintenance`, or `Closed` status to redirect fan flow instantly.
- **Granular Sync**: Rapid `+/-` buttons allow staff to synchronize physical gate counts with the digital dashboard in seconds.
- **Broadcast System**: Send high-priority safety alerts or general announcements directly to all fan dashboards.
- **Individual Resolution**: Resolve emergencies one-by-one with full audit logs in the System Telemetry feed.

---

## 💎 Simultaneous Value Proposition

| For Fans | For Stadium Staff |
| :--- | :--- |
| **Reduced Wait Times**: Fans avoid long queues at restrooms and food courts. | **Predictive Control**: Staff can deploy stewards to zones *before* they become dangerous. |
| **Safety Assurance**: The SOS system provides a direct lifeline to security. | **Rapid Emergency Response**: Precise location data and message content for SOS alerts. |
| **Enhanced Experience**: A seamless, high-tech match day experience. | **Localized Management**: Manage individual stand status without affecting the whole venue. |

---

## 🛠️ Technical Stack
- **Backend**: FastAPI (Python) with header-based Staff Authentication.
- **Frontend**: React (Single Page Application) with Glassmorphic UI/UX.
- **Data Persistence**: Firestore and In-Memory Mock Mode.
- **ML Engine**: Custom predictive trend algorithms.

---

## 🏗️ System Architecture & Workflow

1. **Data Ingress**: IoT sensors (simulated via Admin Sync) send real-time fan counts to the FastAPI backend.
2. **Intelligence Layer**: The backend runs a **Growth Vector Analysis** to determine if a zone is becoming more or less crowded.
3. **Fan Interface**: Fans receive live recommendations ("✅ IDEAL" or "⚠️ AVOID") on their mobile devices based on AI forecasts.
4. **Command Loop**: Admin staff monitor the **Mission Logistics Feed** and use **Operational Overrides** to respond to live emergencies and AI alerts.

---

## 🔑 Quick Access Guide

### 🏟️ Fan Mode (Public Access)
- **Primary View**: The dashboard defaults to Fan Mode.
- **SOS Priority**: Use the red emergency console at the top for immediate assistance.
- **Smart Planning**: Look for the "AI Crowd Forecast" on each zone card to find the best time to visit utilities.

### 🛡️ Admin Mode (Staff Only)
- **How to Enter**: Click the **"STAFF ADMIN"** toggle in the top right corner.
- **Authentication**: Enter the access token `admin` to unlock the Mission Control dashboard.
- **Capabilities**: Once authenticated, you can adjust live fan counts, toggle zone availability (Active/Maintenance/Closed), and broadcast stadium-wide announcements.

---
*Developed for the IPL 2026 Stadium Experience Challenge.*
