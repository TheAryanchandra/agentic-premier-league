from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, AliasChoices
from datetime import datetime, timedelta
import os
from typing import List, Dict, Optional
import json

# Firebase imports
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except ImportError:
    print("Firebase not installed, will work in mock mode")

ADMIN_KEY = os.getenv("ADMIN_KEY", "admin")

async def verify_admin(x_admin_key: Optional[str] = Header(None)):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid Staff Access Token")
    return x_admin_key

app = FastAPI(title="Stadium Experience Dashboard")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_firebase():
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate("firebase-key.json")
            firebase_admin.initialize_app(cred)
        return firestore.client()
    except:
        print("⚠️  Firebase not initialized. Using mock data.")
        return None

db = init_firebase()


class Zone(BaseModel):
    id: str
    name: str
    capacity: int
    status: str = "active" # active, maintenance, closed

class DensityUpdate(BaseModel):
    zone_id: str
    current_people: int
    timestamp: float = None

class Alert(BaseModel):
    id: str = None
    message: str = Field(..., validation_alias=AliasChoices("message", "msg"))
    zone_id: str = None
    phone: str = None
    severity: str = "info"  # info, warning, danger
    status: str = "active"  # active, resolved
    timestamp: float = None


MOCK_ZONES = [
    Zone(id="N1", name="North Stand", capacity=5000, status="active"),
    Zone(id="S1", name="South Stand", capacity=4000, status="active"),
    Zone(id="E1", name="East Stand", capacity=3000, status="active"),
    Zone(id="W1", name="West Stand", capacity=3500, status="active"),
    Zone(id="F1", name="Food Court", capacity=500, status="active"),
    Zone(id="R1", name="Restrooms", capacity=200, status="active"),
]

MOCK_DENSITY = {
    "N1": {"current": 2500, "trend": [2000, 2200, 2400, 2500], "last_update": datetime.now().timestamp()},
    "S1": {"current": 1800, "trend": [1500, 1600, 1700, 1800], "last_update": datetime.now().timestamp()},
    "E1": {"current": 1200, "trend": [800, 900, 1000, 1200], "last_update": datetime.now().timestamp()},
    "W1": {"current": 2000, "trend": [1800, 1850, 1950, 2000], "last_update": datetime.now().timestamp()},
    "F1": {"current": 150, "trend": [50, 100, 120, 150], "last_update": datetime.now().timestamp()},
    "R1": {"current": 45, "trend": [30, 35, 40, 45], "last_update": datetime.now().timestamp()},
}

MOCK_ALERTS = []



@app.get("/")
def read_root():
    return {
        "status": "Stadium Experience Dashboard API",
        "version": "1.0.0",
        "endpoints": {
            "zones": "/zones",
            "density": "/density",
            "density/update": "POST /density/update",
            "alerts": "/alerts",
            "alert/create": "POST /alerts/create"
        }
    }


@app.get("/zones", response_model=List[Dict])
def get_zones():
    if db:
        try:
            zones = db.collection("zones").stream()
            return [z.to_dict() for z in zones]
        except:
            return [z.model_dump() for z in MOCK_ZONES]
    return [z.model_dump() for z in MOCK_ZONES]

@app.post("/zones/update")
def update_zone_status(zone_id: str, status: str, admin: str = Depends(verify_admin)):
    if status not in ["active", "maintenance", "closed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    for zone in MOCK_ZONES:
        if zone.id == zone_id:
            zone.status = status
            return {"status": "success", "zone_id": zone_id, "new_status": status}
    
    raise HTTPException(status_code=404, detail="Zone not found")

@app.get("/density")
def get_density():
    if db:
        try:
            density_doc = db.collection("venue").document("current_density").get()
            if density_doc.exists:
                return density_doc.to_dict()
        except:
            pass
    

    result = {}
    for zone_id, data in MOCK_DENSITY.items():
        zone = next((z for z in MOCK_ZONES if z.id == zone_id), None)
        if zone:
            percentage = (data["current"] / zone.capacity) * 100
            status = "safe" if percentage < 70 else "crowded" if percentage < 85 else "danger"
            result[zone_id] = {
                "current": data["current"],
                "capacity": zone.capacity,
                "percentage": round(percentage, 1),
                "status": status,
                "trend": data["trend"],
                "last_update": data["last_update"]
            }
    return result



@app.post("/density/update")
def update_density(update: DensityUpdate, admin: str = Depends(verify_admin)):
    zone_id = update.zone_id
    current_people = update.current_people
    timestamp = update.timestamp or datetime.now().timestamp()
    
    if db:
        try:
            # Update in Firestore
            db.collection("venue").document("current_density").update({
                f"{zone_id}.current": current_people,
                f"{zone_id}.last_update": timestamp
            })
            return {"status": "success", "zone_id": zone_id, "people": current_people}
        except:
            pass
    

    if zone_id in MOCK_DENSITY:
        # Keep trend (last 5 values for better ML)
        MOCK_DENSITY[zone_id]["trend"] = MOCK_DENSITY[zone_id]["trend"][1:] + [current_people]
        MOCK_DENSITY[zone_id]["current"] = current_people
        MOCK_DENSITY[zone_id]["last_update"] = timestamp
        return {"status": "success", "zone_id": zone_id, "people": current_people}
    
    raise HTTPException(status_code=404, detail="Zone not found")

# Get all alerts
@app.get("/alerts")
def get_alerts():
    if db:
        try:
            alerts = db.collection("alerts").order_by("timestamp", direction="DESCENDING").limit(20).stream()
            return [a.to_dict() for a in alerts]
        except:
            pass
    return MOCK_ALERTS[::-1]  # Return local alerts in reverse chronological order

# Create alert (for staff or fans)
@app.post("/alerts/create")
def create_alert(alert: Alert, x_admin_key: Optional[str] = Header(None)):
    # SOS alerts (danger) don't need admin key (from fans), but general info/warning alerts do
    if alert.severity != "danger" and x_admin_key != ADMIN_KEY:
         raise HTTPException(status_code=403, detail="Unauthorized Staff Access")

    alert.timestamp = alert.timestamp or datetime.now().timestamp()
    
    if db:
        try:
            db.collection("alerts").add(alert.model_dump())
            return {"status": "success", "alert": alert.model_dump()}
        except:
            pass
    
    # Store in local memory for mock mode
    MOCK_ALERTS.append(alert.model_dump())
    return {"status": "success", "alert": alert.model_dump()}

# Resolve a specific alert
@app.post("/alerts/resolve/{alert_index}")
def resolve_alert(alert_index: int, admin: str = Depends(verify_admin)):
    if 0 <= alert_index < len(MOCK_ALERTS):
        MOCK_ALERTS[alert_index]["status"] = "resolved"
        return {"status": "success", "message": "Alert resolved"}
    raise HTTPException(status_code=404, detail="Alert index not found")

# Clear all alerts (Admin only)
@app.delete("/alerts/clear")
def clear_alerts(admin: str = Depends(verify_admin)):
    if db:
        try:
            # In a real app, you'd batch delete. Here we just try to clear local for mock.
            docs = db.collection("alerts").stream()
            for doc in docs:
                doc.reference.delete()
        except:
            pass
            
    MOCK_ALERTS.clear()
    return {"status": "success", "message": "All alerts cleared"}

# Get queue prediction for a zone
@app.get("/queue/prediction/{zone_id}")
def get_queue_prediction(zone_id: str):
    """Simple ML: trend-based queue time prediction"""
    if zone_id not in MOCK_DENSITY:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    trend = MOCK_DENSITY[zone_id]["trend"]
    current = MOCK_DENSITY[zone_id]["current"]
    
    # Simple moving average for prediction
    avg_growth = sum([trend[i+1] - trend[i] for i in range(len(trend)-1)]) / (len(trend) - 1)
    predicted_in_5min = max(0, int(current + (avg_growth * 0.5)))
    predicted_in_10min = max(0, int(current + (avg_growth * 1)))
    
    return {
        "zone_id": zone_id,
        "current": current,
        "predicted_5min": predicted_in_5min,
        "predicted_10min": predicted_in_10min,
        "trend": "increasing" if avg_growth > 0 else "decreasing",
        "recommendation": "avoid" if predicted_in_10min > 250 else "ok"
    }

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
