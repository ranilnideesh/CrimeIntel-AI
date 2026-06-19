import os
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, Base, get_db
from app.utils.test_data import seed_database
from app.routers import auth, cases, evidence, analysis, intelligence, chat, milestones, reports
from app.models.models import Case, EvidenceItem, Lead, Milestone, User
from app.models.schemas import DashboardStats
from app.routers.auth import get_current_user

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Seed database on startup
db_session = Session(bind=engine)
try:
    # If no users exist, seed the DB
    if db_session.query(User).count() == 0:
        seed_database(db_session)
finally:
    db_session.close()

app = FastAPI(
    title=settings.APP_NAME,
    description="Intelligent Evidence Analysis, Crime Pattern Mining & Investigation Support System",
    version="1.0.0",
    docs_url="/docs"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to react dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount evidence uploads folder to be served statically
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/static/evidence", StaticFiles(directory=settings.UPLOAD_DIR), name="evidence_static")

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(cases.router, prefix=settings.API_V1_STR)
app.include_router(evidence.router, prefix=settings.API_V1_STR)
app.include_router(analysis.router, prefix=settings.API_V1_STR)
app.include_router(intelligence.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)
app.include_router(milestones.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    from fastapi.responses import FileResponse
    static_file_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    return FileResponse(static_file_path)

@app.get(settings.API_V1_STR + "/dashboard/stats", response_model=DashboardStats)
def get_dashboard_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve high-level counts, hotspots, and active leads to feed the analytics dashboard."""
    total_cases = db.query(Case).count()
    active_cases = db.query(Case).filter(Case.status == "Active").count()
    solved_cases = db.query(Case).filter(Case.status == "Solved").count()
    evidence_count = db.query(EvidenceItem).count()
    
    # Recent leads
    recent_leads = []
    leads = db.query(Lead).order_by(Lead.generated_at.desc()).limit(5).all()
    for l in leads:
        recent_leads.append({
            "id": l.id,
            "case_id": l.case_id,
            "title": l.title,
            "description": l.description,
            "confidence_score": l.confidence_score,
            "source": l.source
        })
        
    # Milestones (last 5)
    recent_milestones = []
    milestones = db.query(Milestone).order_by(Milestone.updated_at.desc()).limit(5).all()
    for m in milestones:
        recent_milestones.append({
            "id": m.id,
            "case_id": m.case_id,
            "title": m.title,
            "status": m.status,
            "updated_at": m.updated_at
        })
        
    # Hotspots from intelligence
    hotspots = [
        {"lat": 28.6304, "lon": 77.2177, "intensity": 85, "location": "Connaught Place, Delhi"},
        {"lat": 12.9716, "lon": 77.5946, "intensity": 90, "location": "Bengaluru Tech Center"},
        {"lat": 19.0760, "lon": 72.8777, "intensity": 70, "location": "Mumbai Highway rest stops"}
    ]
    
    # Global AI suggestions
    suggestions = [
        "Strengthen Night border checkposts in Noida exit loops (High Threat Priority)",
        "Audit PayNext Active Directory server access tokens (Phishing Alert)",
        "Review highway dhaba staff identity registries around Lonavala (Solved Modus Match)"
    ]
    
    # Risk areas
    risk_areas = [
        {"sector": "Financial / Jewelers Complex (Delhi)", "level": "High Risk", "score": 85.0},
        {"sector": "Fintech / Phishing target sites (Bangalore)", "level": "Medium Risk", "score": 62.0},
        {"sector": "Logistics Expressways (Mumbai)", "level": "Low Risk (Monitored)", "score": 30.0}
    ]
    
    return {
        "total_cases": total_cases,
        "active_cases": active_cases,
        "solved_cases": solved_cases,
        "evidence_count": evidence_count,
        "recent_leads": recent_leads,
        "milestones": recent_milestones,
        "hotspots": hotspots,
        "suggestions": suggestions,
        "risk_areas": risk_areas
    }
