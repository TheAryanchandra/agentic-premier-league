# 🏟️ Stadium Pulse: AI-Driven IPL Venue Management

**Stadium Pulse** is a high-performance, real-time command center and fan engagement dashboard designed for the IPL 2026 match (DC vs Punjab). It transforms stadium management from reactive chaos into predictive coordination.

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
- **Data Persistence**: Firestore (Optional) / In-Memory Mock Mode (Demo).
- **ML Engine**: Custom predictive trend algorithms.

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
