import random
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Case, User, EvidenceItem, Lead, Milestone
from app.models.schemas import CaseCreate, CaseResponse, CaseUpdate
from app.routers.auth import get_current_user, require_role
from app.utils.logger import log_audit

router = APIRouter(prefix="/cases", tags=["Case Management"])

@router.get("/", response_model=list[CaseResponse])
def list_cases(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    cases = db.query(Case).all()
    return cases

@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
def create_case(
    case_in: CaseCreate,
    request: Request,
    current_user: User = Depends(require_role(["Investigation Officer", "Admin"])),
    db: Session = Depends(get_db)
):
    # Check if case number exists
    existing = db.query(Case).filter(Case.case_number == case_in.case_number).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Case number / FIR already exists",
        )
        
    # Generate initial suggestions/predictions based on case characteristics
    desc = case_in.description.lower() if case_in.description else ""
    initial_risk = 20.0
    initial_pred = "Analysis pending evidence upload."
    initial_prev = "Maintain standard patrol frequency in area."
    
    if "jewel" in desc or "gold" in desc or "heist" in desc:
        initial_risk = 75.0
        initial_pred = "Modus operandi aligns with organized heist gangs specializing in vaults/safes."
        initial_prev = "Strengthen CCTV perimeter around jeweler shops; audit silent panic alarm logs."
    elif "ransom" in desc or "crypto" in desc or "phish" in desc:
        initial_risk = 55.0
        initial_pred = "Breach vectors suggest ransomware-as-a-service campaign using target phishing."
        initial_prev = "Isolate infected servers; force active directory password changes."
        
    case = Case(
        case_number=case_in.case_number,
        title=case_in.title,
        description=case_in.description,
        status="Active",
        assigned_officer_id=current_user.id,
        risk_score=initial_risk,
        suspect_prediction=initial_pred,
        prevention_suggestions=initial_prev
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    
    # Initialize basic case milestones
    initial_milestones = [
        "FIR Registered & Site Survey Completed",
        "Witness Statements Collected",
        "Forensic Reports Submitted",
        "Suspect Call Records Analyzed",
        "AI Recommendations Reviewed"
    ]
    for title in initial_milestones:
        ms = Milestone(
            case_id=case.id,
            title=title,
            status="Pending",
            updated_by=current_user.id
        )
        db.add(ms)
    db.commit()
    
    log_audit(db, current_user.id, "Create Case", f"Registered new case: {case.case_number}", request.client.host)
    return case

@router.get("/{case_id}", response_model=CaseResponse)
def get_case(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    return case

@router.put("/{case_id}", response_model=CaseResponse)
def update_case(
    case_id: int,
    case_update: CaseUpdate,
    request: Request,
    current_user: User = Depends(require_role(["Investigation Officer", "Crime Analyst", "Admin"])),
    db: Session = Depends(get_db)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
        
    update_data = case_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)
        
    db.commit()
    db.refresh(case)
    log_audit(db, current_user.id, "Update Case", f"Modified case ID: {case.id}", request.client.host)
    return case

@router.delete("/{case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_case(
    case_id: int,
    request: Request,
    current_user: User = Depends(require_role(["Admin"])),
    db: Session = Depends(get_db)
):
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    db.delete(case)
    db.commit()
    log_audit(db, current_user.id, "Delete Case", f"Removed case ID: {case_id}", request.client.host)
    return None
