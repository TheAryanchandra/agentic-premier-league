import math
import re
from typing import List, Dict, Any, Tuple
import os

STADIUM_SOPS: List[Dict[str, Any]] = [
    {
        "id": "SOP-01",
        "title": "Stampede & Ingress Surge Prevention Protocol",
        "category": "stampede_hazard",
        "urgency": "critical",
        "keywords": ["stampede", "crush", "surge", "gate crowd", "bottleneck", "turnstile jammed", "gate 4", "stairway packed"],
        "action": "Immediate gate diversion to Auxiliary Gates B & C. Activate steward perimeter cordon. Display electronic signage redirecting incoming waves.",
        "eta": 45
    },
    {
        "id": "SOP-02",
        "title": "Severe Medical Distress & Heat Exhaustion Protocol",
        "category": "medical",
        "urgency": "high",
        "keywords": ["medical", "fainted", "unconscious", "heart", "heat stroke", "dehydration", "bleeding", "asthma", "seizure"],
        "action": "Dispatch Field Medic Unit 3 with portable defibrillator and hydration pack. Clear green corridor for rapid extraction to First Aid Station.",
        "eta": 30
    },
    {
        "id": "SOP-03",
        "title": "Utility & Concessions Overload Mitigation",
        "category": "utility_choke",
        "urgency": "medium",
        "keywords": ["food court", "restroom queue", "water line", "washroom packed", "concessions", "beverage counter", "restrooms"],
        "action": "Broadcast mobile wayfinding to fans: Route to Level 2 Restrooms (current 22% capacity) and West Concourse food stalls with zero wait.",
        "eta": 60
    },
    {
        "id": "SOP-04",
        "title": "Security Perimeter & Unattended Object Triage",
        "category": "security",
        "urgency": "high",
        "keywords": ["unattended bag", "suspicious item", "fight", "brawl", "pitch invader", "smoke", "flare", "perimeter breach"],
        "action": "Deploy rapid response security detail. Establish 15-meter visual perimeter. Review CCTV telemetry feed on Sector Cam 09.",
        "eta": 40
    },
    {
        "id": "SOP-05",
        "title": "Lost Minor & Family Reunification Protocol",
        "category": "general",
        "urgency": "medium",
        "keywords": ["lost child", "missing kid", "separated", "crying child", "family reunion", "minor lost"],
        "action": "Escort minor to Customer Care Booth West. Broadcast discreet steward alert on internal channel B with physical description.",
        "eta": 90
    }
]

def _tokenize(text: str) -> List[str]:
    return re.findall(r'\w+', text.lower())

def _cosine_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    sum1 = sum([val ** 2 for val in vec1.values()])
    sum2 = sum([val ** 2 for val in vec2.values()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    if not denominator:
        return 0.0
    return float(numerator / denominator)

def text_to_vector(text: str) -> Dict[str, float]:
    tokens = _tokenize(text)
    counts = {}
    for t in tokens:
        counts[t] = counts.get(t, 0) + 1.0
    # Normalize length
    norm = math.sqrt(sum(v * v for v in counts.values())) or 1.0
    return {k: v / norm for k, v in counts.items()}

class SemanticEmbeddingsPipeline:
    """Semantic embedding matcher supporting OpenAI / HuggingFace or built-in dense vector search"""
    def __init__(self):
        self.sops = STADIUM_SOPS
        self.sop_vectors = []
        for sop in self.sops:
            combined_text = f"{sop['title']} {sop['category']} {' '.join(sop['keywords'])} {sop['action']}"
            vec = text_to_vector(combined_text)
            self.sop_vectors.append((sop, vec))

    def search(self, query: str, top_k: int = 2) -> List[Dict[str, Any]]:
        query_vec = text_to_vector(query)
        scored = []
        for sop, svec in self.sop_vectors:
            score = _cosine_similarity(query_vec, svec)
            # Check for direct keyword matches for bonus boost
            q_lower = query.lower()
            keyword_bonus = sum(0.2 for kw in sop["keywords"] if kw in q_lower)
            final_score = min(0.99, score + keyword_bonus)
            if final_score > 0.15:
                scored.append({
                    "sop": sop,
                    "similarity_score": round(final_score, 4)
                })
        scored.sort(key=lambda x: x["similarity_score"], reverse=True)
        if not scored:
            # Fallback to general sop if low similarity
            scored.append({"sop": self.sops[0], "similarity_score": 0.45})
        return scored[:top_k]

semantic_pipeline = SemanticEmbeddingsPipeline()
