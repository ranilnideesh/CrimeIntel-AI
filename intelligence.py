import math
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Case, Lead, EvidenceItem, User
from app.routers.auth import get_current_user
from app.ml.similarity import get_similarity_finder
from app.ml.network import get_graph_analyzer
from app.utils.logger import log_audit

router = APIRouter(prefix="/intelligence", tags=["Crime Intelligence & Leads"])

@router.get("/leads/{case_id}")
def get_investigation_leads(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves all AI generated leads for a case."""
    leads = db.query(Lead).filter(Lead.case_id == case_id).all()
    return leads

@router.post("/compare/{case_id}")
def compare_with_historical_cases(
    case_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Computes textual and MO similarities against past case records."""
    target_case = db.query(Case).filter(Case.id == case_id).first()
    if not target_case:
        raise HTTPException(status_code=404, detail="Target case not found")
        
    other_cases = db.query(Case).filter(Case.id != case_id).all()
    historical_data = [{"id": c.id, "case_number": c.case_number, "title": c.title, "description": c.description} for c in other_cases]
    
    finder = get_similarity_finder()
    similarity_results = finder.calculate_similarity(target_case.description, historical_data)
    
    log_audit(db, current_user.id, "Compare Case", f"Compared case ID: {case_id} against historical DB", request.client.host)
    return {
        "case_id": case_id,
        "matches": similarity_results
    }

@router.get("/hotspots")
def get_crime_hotspots(current_user: User = Depends(get_current_user)):
    """
    Returns coordinate clusters representing hot spots (DBSCAN simulation).
    Coordinates are set near primary cities in India (Delhi, Mumbai, Bengaluru).
    """
    return [
        # Delhi Connaught Place Area
        {"id": 1, "city": "Delhi", "lat": 28.6304, "lon": 77.2177, "type": "Armed Burglary", "intensity": 85, "radius_meters": 500},
        {"id": 2, "city": "Delhi", "lat": 28.5900, "lon": 77.3000, "type": "Vehicle Theft", "intensity": 62, "radius_meters": 350},
        # Bengaluru Tech Corridors
        {"id": 3, "city": "Bengaluru", "lat": 12.9716, "lon": 77.5946, "type": "Cyber / Phishing", "intensity": 90, "radius_meters": 800},
        {"id": 4, "city": "Bengaluru", "lat": 12.9279, "lon": 77.6271, "type": "Extortion", "intensity": 45, "radius_meters": 200},
        # Mumbai Highways
        {"id": 5, "city": "Mumbai", "lat": 19.0760, "lon": 72.8777, "type": "Highway Cargo Hijack", "intensity": 70, "radius_meters": 600}
    ]

@router.post("/escape-route")
def predict_escape_route(
    scene_lat: float,
    scene_lon: float,
    escape_heading: str = "Noida",
    current_user: User = Depends(get_current_user)
):
    """
    Calculates a list of map markers representing an escape path.
    Simulates Dijkstra highway routing from crime scene towards border exits.
    """
    # Delhi Connaught place scene coordinates
    path = []
    num_steps = 6
    
    # Target checkpoint (e.g. Noida borders)
    target_lat = 28.5900
    target_lon = 77.3000
    
    # Generate linear points with slight noise to mimic GPS tracking/road bends
    for i in range(num_steps):
        t = i / (num_steps - 1)
        lat = scene_lat + t * (target_lat - scene_lat) + (math.sin(t * math.pi) * 0.005)
        lon = scene_lon + t * (target_lon - scene_lon) + (math.cos(t * math.pi) * 0.005)
        path.append([lat, lon])
        
    return {
        "escape_path": path,
        "checkpoints": [
            {"name": "Connaught Place Exit Roundabout", "lat": scene_lat, "status": "Passed"},
            {"name": "Yamuna Expressway Toll Booth", "lat": scene_lat + 0.5*(target_lat-scene_lat), "status": "Alert Triggered"},
            {"name": "Noida Border Checkpoint 4", "lat": target_lat, "status": "Sealed"}
        ],
        "tactical_alert": "Suspects likely headed toward Noida sector 62 safehouse. Establish roadblocks at Yamuna Toll."
    }

@router.get("/outcome-analysis/{case_id}")
def analyze_case_outcomes(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Predicts prosecution success rate, charge sheet delays and legal risks based on evidence quality."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    all_evidence = db.query(EvidenceItem).filter(EvidenceItem.case_id == case_id).all()
    num_items = len(all_evidence)
    
    # Predictive outcomes calculations
    prosecution_rate = min(30.0 + (num_items * 10.0), 92.0)
    chargesheet_delay_days = max(90 - (num_items * 8), 15)
    
    # Factor evidence categories
    has_digital = any(e.type in ["CCTV", "Call Record"] for e in all_evidence)
    has_physical = any(e.type in ["Image", "Weapon"] for e in all_evidence)
    
    evidence_stability_index = 40.0
    if has_digital:
        evidence_stability_index += 25.0
    if has_physical:
        evidence_stability_index += 25.0
        
    return {
        "case_id": case_id,
        "prosecution_probability": round(prosecution_rate, 1),
        "estimated_chargesheet_days": chargesheet_delay_days,
        "evidence_stability_index": round(evidence_stability_index, 1),
        "legal_risks": [
            "Witness retraction risk (moderate)" if not has_digital else "Low witness risk due to digital evidence backup",
            "Technical challenges due to IP proxy servers" if "ransomware" in case.description.lower() else "Chain-of-custody verification required for CCTV footage"
        ]
    }
