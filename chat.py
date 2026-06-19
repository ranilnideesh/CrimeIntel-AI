from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import Case, EvidenceItem, Lead, User
from app.models.schemas import ChatRequest, ChatResponse
from app.routers.auth import get_current_user

router = APIRouter(prefix="/chat", tags=["AI Chatbot Assistant"])

# Custom navigational guide dictionary
NAV_GUIDE = {
    "dashboard": "You can access the main metrics (active cases, hot spots, officer milestones) on the Dashboard page (/dashboard).",
    "upload": "To upload files, head to the Evidence Upload page (/evidence-upload) where you can input images, CCTV mp4 files, or PDFs.",
    "map": "To see crime coordinate maps and hotspots, visit the Crime Map (/map).",
    "graph": "The Evidence relationship link-prediction graph is visualised under the Evidence Graph page (/graph).",
    "milestones": "Verify investigator checklists on the Officer Milestones page (/milestones)."
}

@router.post("/", response_model=ChatResponse)
def chatbot_assistant(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    msg = payload.message.lower()
    reply = ""
    suggested_actions = ["Check Case Milestones", "View Similar Cases", "Generate PDF Report"]
    
    # 1. Check for Navigation keywords
    for nav_kw, path_desc in NAV_GUIDE.items():
        if nav_kw in msg:
            reply = f"Here is how you navigate the system: {path_desc}"
            suggested_actions = [f"Go to {nav_kw.title()}"]
            return {"reply": reply, "suggested_actions": suggested_actions}
            
    # 2. Case RAG Simulation
    if payload.case_id:
        case = db.query(Case).filter(Case.id == payload.case_id).first()
        if not case:
            raise HTTPException(status_code=404, detail="Case context not found")
            
        evidence = db.query(EvidenceItem).filter(EvidenceItem.case_id == case.id).all()
        leads = db.query(Lead).filter(Lead.case_id == case.id).all()
        
        ev_summary = ", ".join([f"{e.name} ({e.type})" for e in evidence]) or "No evidence uploaded yet"
        lead_summary = "; ".join([l.title for l in leads]) or "No active leads generated"
        
        if "summar" in msg or "explain" in msg:
            reply = (
                f"<b>Case Summary for {case.case_number}:</b><br/>"
                f"Title: {case.title}<br/>"
                f"Description: {case.description}<br/>"
                f"Risk Index: {case.risk_score}%<br/>"
                f"Current evidence cataloged: {ev_summary}.<br/>"
                f"Active Leads: {lead_summary}."
            )
            suggested_actions = ["Run Image Analysis", "Extract Named Entities", "Download Dossier PDF"]
            
        elif "checklist" in msg or "todo" in msg or "next" in msg:
            reply = (
                f"<b>AI Investigation Checklist for {case.case_number}:</b><br/>"
                f"1. [ ] Validate the integrity of these files: {ev_summary or 'None'}.<br/>"
                f"2. [ ] Verify custody signatures of handlers on database logs.<br/>"
                f"3. [ ] Follow up on lead: '{leads[0].title if leads else 'No lead yet'}' with field officers.<br/>"
                f"4. [ ] Request cyber-forensic logs for phishing source IP if applicable.<br/>"
                f"5. [ ] Cross-verify suspect records using MO comparison."
            )
            suggested_actions = ["Mark Milestones Complete", "Compare past cases"]
            
        elif "lead" in msg or "suspect" in msg:
            reply = (
                f"The intelligence engine has flagged {len(leads)} potential leads for {case.case_number}.<br/>"
                f"The highest confidence lead is <b>{leads[0].title if leads else 'None'}</b> "
                f"({leads[0].confidence_score if leads else 0}% confidence) which indicates: "
                f"'{leads[0].description if leads else 'No description available'}'."
            )
            suggested_actions = ["View Evidence Graph", "Locate on Map"]
            
        else:
            reply = (
                f"I am reading the case file for <b>{case.case_number} ({case.title})</b>. "
                f"It mentions '{case.description[:100]}...'. "
                f"You have uploaded {len(evidence)} evidence files and generated {len(leads)} leads. "
                f"Ask me to 'summarize evidence', 'generate checklist', or 'view leads' for case specific insights."
            )
    else:
        # General non-case chat
        if "hello" in msg or "hi" in msg:
            reply = (
                f"Good day Officer {current_user.username}. I am your CrimeIntel AI assistant. "
                f"How may I support your investigation today? I can help with "
                f"navigating the pages, summarizing case files, predicting escape checkpoints, or preparing reports."
            )
        elif "help" in msg or "what can you do" in msg:
            reply = (
                "I am equipped to: <br/>"
                "- Assist with website navigation (e.g. type 'how to upload evidence')<br/>"
                "- Summarize evidence files (select a case context and type 'summarize case')<br/>"
                "- Suggest checklist guidelines (type 'show investigation checklist')<br/>"
                "- Compare new modus operandi against old arrest files"
            )
        else:
            reply = (
                "I understand your query. Please select an active Case Context in the dashboard "
                "or ask general questions about Navigation (e.g. 'how to see hotspots') and I will guide you."
            )
            
    return {"reply": reply, "suggested_actions": suggested_actions}
