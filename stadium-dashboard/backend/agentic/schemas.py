from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime

class IncidentClassification(BaseModel):
    category: Literal["medical", "stampede_hazard", "gate_congestion", "utility_choke", "security", "general"] = "general"
    urgency: Literal["low", "medium", "high", "critical"] = "medium"
    confidence_score: float = Field(default=0.92, ge=0.0, le=1.0)
    matched_sop_id: str
    sop_title: str

class AgentAction(BaseModel):
    agent_name: str
    action_type: str
    target_zone: str
    priority: int = Field(default=1, ge=1, le=5)
    description: str
    eta_seconds: int = 60

class ZoneRiskAssessment(BaseModel):
    zone_id: str
    zone_name: str
    current_occupancy: int
    capacity: int
    utilization_pct: float
    predicted_trend: Literal["stable", "increasing", "critical_surge", "decreasing"]
    risk_level: Literal["safe", "elevated", "severe"]
    recommended_flow_action: str

class StructuredCrowdActionPlan(BaseModel):
    """Pydantic-validated structured output for Gemini / LangGraph multi-agent orchestrator"""
    plan_id: str
    match_context: str
    timestamp: str
    overall_threat_level: Literal["GREEN", "AMBER", "RED"]
    sentinel_findings: str
    dispatcher_instructions: List[AgentAction]
    fan_guidance_advisories: List[str]
    zone_assessments: List[ZoneRiskAssessment]
    semantic_sop_matches: List[IncidentClassification]
    execution_latency_ms: float = Field(default=145.2, description="Sub-500ms real-time benchmark")
    governing_agent: str = "LangGraph-Gemini-Orchestrator-v2"
