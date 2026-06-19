from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Milestone, User
from app.models.schemas import MilestoneResponse, MilestoneUpdate
from app.routers.auth import get_current_user
from app.utils.logger import log_audit

router = APIRouter(prefix="/milestones", tags=["Officer Milestones"])

@router.get("/case/{case_id}", response_model=list[MilestoneResponse])
def get_case_milestones(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    milestones = db.query(Milestone).filter(Milestone.case_id == case_id).all()
    return milestones

@router.put("/{milestone_id}", response_model=MilestoneResponse)
def update_milestone_status(
    milestone_id: int,
    payload: MilestoneUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")
        
    milestone.status = payload.status
    milestone.updated_at = datetime.utcnow()
    milestone.updated_by = current_user.id
    db.commit()
    db.refresh(milestone)
    
    log_audit(db, current_user.id, "Update Milestone", f"Set milestone ID: {milestone_id} to status: {payload.status}", request.client.host)
    return milestone
