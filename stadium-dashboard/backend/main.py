from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, AliasChoices
from datetime import datetime
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

ADMIN_KEY = os.getenv("ADMIN_KEY", "admin")
# MongoDB Atlas URI — reads from env var, falls back to real cluster
_ATLAS_URI = "mongodb+srv://aryanchandra3456_db_user:usB9HryhQd2PhI8U@stadiumpulse.i5eaqkc.mongodb.net/StadiumPulse?retryWrites=true&w=majority&appName=StadiumPulse"
MONGODB_URI = os.getenv("MONGODB_URI", os.getenv("MONGO_URL", _ATLAS_URI))
DB_NAME = "StadiumPulse"

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

class Zone(BaseModel):
    id: str
    name: str
    capacity: int
    status: str = "active" # active, maintenance, closed

class DensityUpdate(BaseModel):
    zone_id: str
    current_people: int
    timestamp: Optional[float] = None

class Alert(BaseModel):
    id: Optional[str] = None
    message: str = Field(..., validation_alias=AliasChoices("message", "msg"))
    zone_id: Optional[str] = None
    phone: Optional[str] = None
    severity: str = "info"  # info, warning, danger
    status: str = "active"  # active, resolved
    timestamp: Optional[float] = None

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

def init_db():
    if not MONGODB_URI:
        print("⚠️ MongoDB URI not set. Operating in mock mode.")
        return None
    try:
        from pymongo import MongoClient
        client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        database = client[DB_NAME]
        
        # Seed default zones if empty
        if database.zones.count_documents({}) == 0:
            database.zones.insert_many([z.model_dump() for z in MOCK_ZONES])
            
        # Seed density if empty
        if not database.venue.find_one({"_id": "current_density"}):
            database.venue.insert_one({"_id": "current_density", **MOCK_DENSITY})
            
        print(" Connected to MongoDB Atlas - Cluster:", DB_NAME)
        return database
    except Exception as e:
        print(f"⚠️ MongoDB connection failed: {e}. Falling back to mock data.")
        return None

db = init_db()

@app.get("/")
def read_root():
    return {
        "status": "Stadium Experience Dashboard API",
        "version": "2.0.0",
        "database": "MongoDB Atlas" if db is not None else "Mock In-Memory",
        "cluster": DB_NAME,
        "endpoints": {
            "zones": "/zones",
            "density": "/density",
            "density/update": "POST /density/update",
            "alerts": "/alerts",
            "alert/create": "POST /alerts/create",
            "health": "/health"
        }
    }

@app.get("/zones", response_model=List[Dict])
def get_zones():
    if db is not None:
        try:
            zones = list(db.zones.find({}, {"_id": 0}))
            if zones:
                return zones
        except Exception as e:
            print("MongoDB get_zones error:", e)
    return [z.model_dump() for z in MOCK_ZONES]

@app.post("/zones/update")
def update_zone_status(zone_id: str, status: str, admin: str = Depends(verify_admin)):
    if status not in ["active", "maintenance", "closed"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    if db is not None:
        try:
            result = db.zones.update_one({"id": zone_id}, {"$set": {"status": status}})
            if result.matched_count > 0:
                return {"status": "success", "zone_id": zone_id, "new_status": status}
        except Exception as e:
            print("MongoDB update_zone error:", e)
    
    for zone in MOCK_ZONES:
        if zone.id == zone_id:
            zone.status = status
            return {"status": "success", "zone_id": zone_id, "new_status": status}
    
    raise HTTPException(status_code=404, detail="Zone not found")

@app.get("/density")
def get_density():
    density_map = MOCK_DENSITY
    zone_capacities = {z.id: z.capacity for z in MOCK_ZONES}

    if db is not None:
        try:
            doc = db.venue.find_one({"_id": "current_density"})
            if doc:
                doc.pop("_id", None)
                density_map = doc
            z_docs = list(db.zones.find({}, {"_id": 0, "id": 1, "capacity": 1}))
            if z_docs:
                zone_capacities = {z["id"]: z["capacity"] for z in z_docs}
        except Exception as e:
            print("MongoDB get_density error:", e)

    result = {}
    for zone_id, data in density_map.items():
        capacity = zone_capacities.get(zone_id, 3000)
        current = data.get("current", 0)
        percentage = (current / capacity) * 100 if capacity > 0 else 0
        status = "safe" if percentage < 70 else "crowded" if percentage < 85 else "danger"
        result[zone_id] = {
            "current": current,
            "capacity": capacity,
            "percentage": round(percentage, 1),
            "status": status,
            "trend": data.get("trend", [current]),
            "last_update": data.get("last_update", datetime.now().timestamp())
        }
    return result

@app.post("/density/update")
def update_density(update: DensityUpdate, admin: str = Depends(verify_admin)):
    zone_id = update.zone_id
    current_people = update.current_people
    timestamp = update.timestamp or datetime.now().timestamp()
    
    if db is not None:
        try:
            doc = db.venue.find_one({"_id": "current_density"})
            if doc and zone_id in doc:
                old_trend = doc[zone_id].get("trend", [current_people])
                new_trend = old_trend[1:] + [current_people]
                db.venue.update_one(
                    {"_id": "current_density"},
                    {"$set": {
                        f"{zone_id}.current": current_people,
                        f"{zone_id}.trend": new_trend,
                        f"{zone_id}.last_update": timestamp
                    }}
                )
                return {"status": "success", "zone_id": zone_id, "people": current_people}
        except Exception as e:
            print("MongoDB update_density error:", e)
    
    if zone_id in MOCK_DENSITY:
        MOCK_DENSITY[zone_id]["trend"] = MOCK_DENSITY[zone_id]["trend"][1:] + [current_people]
        MOCK_DENSITY[zone_id]["current"] = current_people
        MOCK_DENSITY[zone_id]["last_update"] = timestamp
        return {"status": "success", "zone_id": zone_id, "people": current_people}
    
    raise HTTPException(status_code=404, detail="Zone not found")

@app.get("/alerts")
def get_alerts():
    if db is not None:
        try:
            alerts = list(db.alerts.find({}, {"_id": 0}).sort("timestamp", -1).limit(20))
            return alerts
        except Exception as e:
            print("MongoDB get_alerts error:", e)
    return MOCK_ALERTS[::-1]

@app.post("/alerts/create")
def create_alert(alert: Alert, x_admin_key: Optional[str] = Header(None)):
    if alert.severity != "danger" and x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized Staff Access")

    alert_dict = alert.model_dump()
    alert_dict["timestamp"] = alert.timestamp or datetime.now().timestamp()
    if not alert_dict.get("id"):
        alert_dict["id"] = f"alert_{int(datetime.now().timestamp() * 1000)}"
    
    if db is not None:
        try:
            db.alerts.insert_one(dict(alert_dict))
            return {"status": "success", "alert": alert_dict}
        except Exception as e:
            print("MongoDB create_alert error:", e)
    
    MOCK_ALERTS.append(alert_dict)
    return {"status": "success", "alert": alert_dict}

@app.post("/alerts/resolve/{alert_id}")
def resolve_alert(alert_id: str, admin: str = Depends(verify_admin)):
    if db is not None:
        try:
            res = db.alerts.update_one(
                {"$or": [{"id": alert_id}, {"zone_id": alert_id}]},
                {"$set": {"status": "resolved"}}
            )
            if res.matched_count > 0:
                return {"status": "success", "message": "Alert resolved"}
        except Exception as e:
            print("MongoDB resolve_alert error:", e)
            
    try:
        idx = int(alert_id)
        if 0 <= idx < len(MOCK_ALERTS):
            MOCK_ALERTS[idx]["status"] = "resolved"
            return {"status": "success", "message": "Alert resolved"}
    except ValueError:
        pass
        
    return {"status": "success", "message": "Alert resolved"}

@app.delete("/alerts/clear")
def clear_alerts(admin: str = Depends(verify_admin)):
    if db is not None:
        try:
            db.alerts.delete_many({})
        except Exception as e:
            print("MongoDB clear_alerts error:", e)
            
    MOCK_ALERTS.clear()
    return {"status": "success", "message": "All alerts cleared"}

@app.get("/queue/prediction/{zone_id}")
def get_queue_prediction(zone_id: str):
    density_map = MOCK_DENSITY
    if db is not None:
        try:
            doc = db.venue.find_one({"_id": "current_density"})
            if doc:
                density_map = doc
        except Exception as e:
            print("MongoDB prediction error:", e)

    if zone_id not in density_map:
        raise HTTPException(status_code=404, detail="Zone not found")
    
    trend = density_map[zone_id].get("trend", [1000])
    current = density_map[zone_id].get("current", 1000)
    
    avg_growth = 0
    if len(trend) > 1:
        avg_growth = sum([trend[i+1] - trend[i] for i in range(len(trend)-1)]) / (len(trend) - 1)
    predicted_in_5min = max(0, int(current + (avg_growth * 0.5)))
    predicted_in_10min = max(0, int(current + (avg_growth * 1)))
    
    return {
        "zone_id": zone_id,
        "current": current,
        "predicted_5min": predicted_in_5min,
        "predicted_10min": predicted_in_10min,
        "trend": "increasing" if avg_growth > 0 else "decreasing",
        "recommendation": "avoid" if predicted_in_10min > 2500 else "ok"
    }


# --- LangGraph Multi-Agent Orchestration & Semantic SOP Endpoints ---
try:
    from agentic import orchestrator, semantic_pipeline, StructuredCrowdActionPlan
except ImportError:
    from .agentic import orchestrator, semantic_pipeline, StructuredCrowdActionPlan

@app.post("/agentic/orchestrate", response_model=StructuredCrowdActionPlan)
@app.get("/agentic/orchestrate")
def run_agentic_orchestration(match_name: Optional[str] = None):
    current_zones = [z.model_dump() for z in MOCK_ZONES]
    if db is not None:
        try:
            z_docs = list(db.zones.find({}, {"_id": 0}))
            if z_docs:
                current_zones = z_docs
        except Exception:
            pass
    density_data = get_density()
    alerts_data = get_alerts()
    return orchestrator.run(
        match_name=match_name or "IPL 2026: DC vs Punjab",
        zones=current_zones,
        density=density_data,
        alerts=alerts_data
    )

@app.get("/agentic/semantic-search")
@app.post("/agentic/semantic-search")
def semantic_sop_search(q: str = "stampede crowd hazard"):
    results = semantic_pipeline.search(q, top_k=3)
    return {
        "query": q,
        "pipeline": "OpenAI/HuggingFace-Compatible Cosine Vector Matcher",
        "results": [
            {
                "sop_id": r["sop"]["id"],
                "title": r["sop"]["title"],
                "category": r["sop"]["category"],
                "urgency": r["sop"]["urgency"],
                "similarity_score": r["similarity_score"],
                "immediate_action": r["sop"]["action"],
                "eta_seconds": r["sop"]["eta"]
            }
            for r in results
        ]
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected" if db is not None else "mock-fallback",
        "cluster": DB_NAME,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
