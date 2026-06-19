import os
import json
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import EvidenceItem, User
from app.routers.auth import get_current_user
from app.ml.detector import get_object_detector
from app.ml.ocr_nlp import get_ocr_nlp_engine
from app.utils.logger import log_audit

router = APIRouter(prefix="/analysis", tags=["AI Image & NLP Analysis"])

@router.post("/image/{evidence_id}")
def analyze_crime_scene_image(
    evidence_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Triggers CV object detection (YOLOv8 simulation) on uploaded images."""
    evidence = db.query(EvidenceItem).filter(EvidenceItem.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence item not found")
        
    if evidence.type not in ["Image", "CCTV"]:
        raise HTTPException(status_code=400, detail="Only Image or CCTV media can be analyzed by CV engine")
        
    # Setup paths
    input_path = evidence.file_path
    if not os.path.exists(input_path):
        raise HTTPException(status_code=404, detail="Raw evidence file missing from disk")
        
    filename = os.path.basename(input_path)
    output_filename = f"analyzed_{filename}"
    output_path = os.path.join(os.path.dirname(input_path), output_filename)
    
    # Run Detector
    detector = get_object_detector()
    detections = detector.analyze_image(input_path, output_path)
    
    # Update Evidence record with findings
    evidence.extracted_metadata = json.dumps({
        "detections": detections,
        "annotated_file": output_path
    })
    evidence.classification = "Analyzed Image"
    db.commit()
    
    log_audit(db, current_user.id, "Analyze Image", f"Ran CV object detection on evidence ID: {evidence_id}", request.client.host)
    return {
        "status": "Success",
        "detections": detections,
        "annotated_file_url": f"/api/v1/evidence/file/{output_filename}" # Static file url placeholder
    }

@router.post("/ocr-ner/{evidence_id}")
def analyze_document_text(
    evidence_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Triggers OCR extraction and BERT/Transformer Named Entity Extraction on text/PDF files."""
    evidence = db.query(EvidenceItem).filter(EvidenceItem.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence item not found")
        
    # Check if text or PDF
    if evidence.type not in ["FIR PDF", "Witness Statement", "Suspect History", "Previous Case File"]:
        raise HTTPException(status_code=400, detail="Only document text/PDF items can be processed by OCR/NER")
        
    engine = get_ocr_nlp_engine()
    raw_text = engine.extract_text_from_file(evidence.file_path)
    entities = engine.extract_entities(raw_text)
    
    # Save results to evidence model
    evidence.extracted_metadata = json.dumps({
        "raw_text": raw_text,
        "entities": entities
    })
    db.commit()
    
    log_audit(db, current_user.id, "Analyze Document", f"Ran OCR/NER extraction on evidence ID: {evidence_id}", request.client.host)
    return {
        "status": "Success",
        "raw_text": raw_text,
        "entities": entities
    }
