import os
import json
import shutil
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models.models import Case, EvidenceItem, User
from app.models.schemas import EvidenceItemResponse
from app.routers.auth import get_current_user
from app.ml.classifier import get_evidence_classifier
from app.ml.network import get_graph_analyzer
from app.utils.logger import log_audit

router = APIRouter(prefix="/evidence", tags=["Evidence Management"])

# Ensure upload directory exists
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "mp4", "avi", "csv", "txt", "mp3", "wav"}

def allowed_file(filename: str) -> bool:
    return "." in filename and filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS

@router.get("/case/{case_id}", response_model=list[EvidenceItemResponse])
def get_case_evidence(
    case_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    evidence = db.query(EvidenceItem).filter(EvidenceItem.case_id == case_id).all()
    return evidence

@router.post("/upload", response_model=EvidenceItemResponse, status_code=status.HTTP_201_CREATED)
async def upload_evidence(
    request: Request,
    case_id: int = Form(...),
    name: str = Form(...),
    type: str = Form(...), # Explicit type selected by user
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify case exists
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
        
    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File extension not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
        )
        
    # Save file securely
    timestamp_str = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    safe_filename = f"{case.case_number}_{timestamp_str}_{file.filename}"
    filepath = os.path.join(settings.UPLOAD_DIR, safe_filename)
    
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # If the file is text/csv, read some sample text for ML classification
    content_text = ""
    ext = file.filename.split(".")[-1].lower()
    if ext in ["txt", "csv"]:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content_text = f.read(2000) # Read first 2KB
        except Exception:
            pass

    # Run AI Auto Classifier
    classifier = get_evidence_classifier()
    # If user selected 'auto', we assign the predicted category, otherwise we keep their input
    predicted_type, conf_score = classifier.predict(file.filename, content_text)
    final_type = predicted_type if type == "auto" else type
    
    # Initialize Chain of Custody record
    custody_chain = [
        {
            "action": "UPLOADED",
            "handler_id": current_user.id,
            "handler_name": current_user.username,
            "timestamp": datetime.utcnow().isoformat(),
            "location": "Evidence Upload Terminal",
            "remarks": "Initial ingestion into secure storage."
        }
    ]
    
    evidence = EvidenceItem(
        case_id=case_id,
        name=name,
        type=final_type,
        file_path=filepath,
        uploaded_by=current_user.id,
        classification=predicted_type,
        confidence_score=conf_score,
        custody_chain=json.dumps(custody_chain)
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    
    # Dynamically update the case risk score based on new evidence
    all_evidence = db.query(EvidenceItem).filter(EvidenceItem.case_id == case_id).all()
    analyzer = get_graph_analyzer()
    new_risk = analyzer.calculate_case_risk_score(case.__dict__, [e.__dict__ for e in all_evidence])
    case.risk_score = new_risk
    db.commit()
    
    log_audit(db, current_user.id, "Upload Evidence", f"Uploaded evidence file {safe_filename} (ID: {evidence.id}) for case {case.case_number}", request.client.host)
    return evidence

@router.post("/{evidence_id}/custody-transfer")
def transfer_custody(
    evidence_id: int,
    recipient_id: int,
    remarks: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Enables officers to record handovers in the Chain of Custody ledger."""
    evidence = db.query(EvidenceItem).filter(EvidenceItem.id == evidence_id).first()
    if not evidence:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evidence item not found"
        )
        
    recipient = db.query(User).filter(User.id == recipient_id).first()
    if not recipient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recipient officer not found"
        )
        
    custody = json.loads(evidence.custody_chain)
    custody.append({
        "action": "TRANSFERRED",
        "handler_id": recipient.id,
        "handler_name": recipient.username,
        "sender_id": current_user.id,
        "sender_name": current_user.username,
        "timestamp": datetime.utcnow().isoformat(),
        "location": "Physical Vault / Lab Office",
        "remarks": remarks
    })
    
    evidence.custody_chain = json.dumps(custody)
    db.commit()
    
    log_audit(db, current_user.id, "Transfer Custody", f"Transferred evidence ID: {evidence_id} to user ID: {recipient_id}", request.client.host)
    return {"message": "Custody transfer logged successfully", "custody_chain": custody}
