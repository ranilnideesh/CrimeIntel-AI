import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.models import User, Case, EvidenceItem, Milestone, Lead
from app.auth.security import get_password_hash
from app.mongodb import get_mongodb
from app.neo4j_db import get_graph_db

# Mock users configuration
MOCK_USERS = [
    {"username": "officer_sharma", "email": "sharma@police.gov.in", "role": "Investigation Officer", "password": "password123"},
    {"username": "analyst_verma", "email": "verma@police.gov.in", "role": "Crime Analyst", "password": "password123"},
    {"username": "forensic_das", "email": "das@police.gov.in", "role": "Forensic Officer", "password": "password123"},
    {"username": "cyber_singh", "email": "singh@police.gov.in", "role": "Cyber Crime Officer", "password": "password123"},
    {"username": "admin_system", "email": "admin@police.gov.in", "role": "Admin", "password": "adminsecure"},
]

# Mock cases configuration
MOCK_CASES = [
    {
        "case_number": "FIR-2026-DEL-041",
        "title": "Jewelry Heist at Connaught Place",
        "description": "Armed burglary at Khanna Jewelers in Connaught Place, New Delhi. Security guard was overpowered at 02:30 AM. Safes were cut using gas torches. Value of stolen assets: 4.5 Crores INR.",
        "status": "Active",
        "risk_score": 85.0,
        "suspect_prediction": "Likely executed by the 'Gas Cutter Gang' led by Vicky alias Gas-Cutter, based on similar modus operandi in Noida and Gurgaon cases in 2025.",
        "prevention_suggestions": "Increase night patrolling near jeweler complexes in central Delhi; establish checkpoints at Noida border entry routes between 1:00 AM and 4:00 AM."
    },
    {
        "case_number": "FIR-2026-BLR-112",
        "title": "Ransomware Attack on FinTech Firm",
        "description": "Cryptolocker ransomware deployment at Bengaluru FinTech Startup 'PayNext'. Servers encrypted; attacker demands 5 BTC. Initial entry point identified as phishing email opened by finance executive.",
        "status": "Active",
        "risk_score": 62.0,
        "suspect_prediction": "Phishing domain registered via anonymous registrar using dynamic DNS. Infrastructure overlaps with active ransomware-as-a-service group 'PhishBlack'.",
        "prevention_suggestions": "Enforce Multi-Factor Authentication (MFA) across all endpoints; isolate active active directory databases; deploy perimeter traffic monitoring on known Tor exit nodes."
    },
    {
        "case_number": "FIR-2025-MUM-908",
        "title": "Highways Cargo Theft Case",
        "description": "Hijacking of a container truck transporting high-end electronics on the Mumbai-Pune Expressway near Lonavala. Driver poisoned using drugged tea at a roadside dhaba.",
        "status": "Solved",
        "risk_score": 30.0,
        "suspect_prediction": "Local highway robbery ring operated by Ashok Kale. Captured near Navi Mumbai warehouse during raid.",
        "prevention_suggestions": "Install CCTV surveillance on Expressway rest stops; verify staff registrations of dhabas."
    }
]

def seed_database(db: Session):
    """Seed relational database, NoSQL collections, and Graph collections with synthetic data."""
    # 1. Seed SQL Users
    db_users = []
    for user_data in MOCK_USERS:
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing:
            hashed_pw = get_password_hash(user_data["password"])
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                role=user_data["role"],
                password_hash=hashed_pw
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            db_users.append(user)
        else:
            db_users.append(existing)
            
    officer_id = db_users[0].id if db_users else 1
    
    # 2. Seed SQL Cases & Associated items
    for case_data in MOCK_CASES:
        existing_case = db.query(Case).filter(Case.case_number == case_data["case_number"]).first()
        if not existing_case:
            case = Case(
                case_number=case_data["case_number"],
                title=case_data["title"],
                description=case_data["description"],
                status=case_data["status"],
                assigned_officer_id=officer_id,
                risk_score=case_data["risk_score"],
                suspect_prediction=case_data["suspect_prediction"],
                prevention_suggestions=case_data["prevention_suggestions"]
            )
            db.add(case)
            db.commit()
            db.refresh(case)
            
            # Create Milestones
            milestones_list = [
                "FIR Registered & Site Survey Completed",
                "Witness Statements Collected",
                "Forensic Reports Submitted",
                "Suspect Call Records Analyzed",
                "AI Recommendations Reviewed"
            ]
            for i, title in enumerate(milestones_list):
                milestone = Milestone(
                    case_id=case.id,
                    title=title,
                    status="Completed" if (i < 3 or case.status == "Solved") else "Pending",
                    updated_by=officer_id,
                    updated_at=datetime.utcnow() - timedelta(days=(5-i))
                )
                db.add(milestone)
            
            # Create AI Generated Leads
            if case.status == "Active":
                leads_list = [
                    ("Gas Cutter Tanker Match", "A white Mahindra pickup with registration DL-3C-AS-9988 was spotted leaving Connaught Place at 02:45 AM, matching gas cutter gang escape pattern.", "CCTV Vehicle Tracker", 87.5),
                    ("Tower Dump Correlation", "Mobile number +91-98765-43210 registered under fake ID was active near Khanna Jewelers at the time of heist and later pinged Noida Expressway tower.", "CDR Analysis", 92.0),
                    ("Witness Clue", "Witness statement describes a tall man with a scar on left hand speaking in Haryanvi dialect, matching former convict Rajesh alias Scar.", "Witness NLP Analyzer", 78.4)
                ] if "Jewelry" in case.title else [
                    ("Phishing Origin", "Malicious attachment originated from IP 185.220.101.44 (known TOR exit node hosted in Germany).", "Cyber Logs Analyzer", 80.0),
                    ("Bitcoin Address Activity", "Demanded ransom address has processed 14 BTC in the last 72 hours, transferring funds to mixer coinjoin services.", "Crypto Ledger Tracker", 89.0)
                ]
                
                for title, desc, source, conf in leads_list:
                    lead = Lead(
                        case_id=case.id,
                        title=title,
                        description=desc,
                        source=source,
                        confidence_score=conf
                    )
                    db.add(lead)
            
            db.commit()

    # 3. Seed MongoDB/JSON Document Store with raw logs and transcripts
    mongo_db = get_mongodb()
    
    # CCTV logs document
    cctv_meta = {
        "evidence_id": "cctv_del_041",
        "case_number": "FIR-2026-DEL-041",
        "objects_detected": [
            {"class": "person", "confidence": 0.94, "box": [120, 340, 280, 580]},
            {"class": "car", "confidence": 0.88, "box": [450, 200, 720, 910], "license_plate": "DL-3C-AS-9988"},
            {"class": "gas cylinder", "confidence": 0.82, "box": [290, 400, 380, 480], "type": "oxygen/acetylene"}
        ]
    }
    # Check if already exists in local json database
    if not mongo_db.find("evidence_metadata", {"case_number": "FIR-2026-DEL-041"}):
        mongo_db.insert_one("evidence_metadata", cctv_meta)
        
        # Seed CDR records
        cdr_meta = {
            "case_number": "FIR-2026-DEL-041",
            "calls": [
                {"caller": "+91-98765-43210", "receiver": "+91-90001-23456", "timestamp": "2026-06-19T02:22:00Z", "duration_sec": 45, "tower_lat": 28.6304, "tower_lon": 77.2177, "target_name": "Rajesh (Scar)"},
                {"caller": "+91-90001-23456", "receiver": "+91-98888-77777", "timestamp": "2026-06-19T02:48:00Z", "duration_sec": 12, "tower_lat": 28.5900, "tower_lon": 77.3000, "target_name": "Vicky (Gas-Cutter)"}
            ]
        }
        mongo_db.insert_one("cdr_records", cdr_meta)
        
        # Seed suspect profile
        suspect_meta = {
            "suspect_id": "susp_rajesh_01",
            "name": "Rajesh alias Scar",
            "aliases": ["Scar", "Haryanvi Gangster"],
            "known_modus_operandi": "Burglary using industrial gas torches; targets bank ATMs and high-end jewelry stores; operates primarily between 02:00 AM and 04:00 AM.",
            "associated_gang": "Gas Cutter Gang",
            "criminal_records": [
                {"year": 2022, "offense": "Grand Theft", "jail_term_months": 18, "city": "Gurgaon"},
                {"year": 2024, "offense": "Attempted Safe Robbery", "jail_term_months": 12, "city": "Noida"}
            ]
        }
        mongo_db.insert_one("suspect_profiles", suspect_meta)

    # 4. Seed Neo4j Graph DB with case entities
    graph_db = get_graph_db()
    
    # Add Nodes
    graph_db.add_node("CASE_CP_HEIST", "Case", {"name": "CP Jewelry Heist", "number": "FIR-2026-DEL-041"})
    graph_db.add_node("SUSP_RAJESH", "Suspect", {"name": "Rajesh alias Scar", "phone": "+91-98765-43210"})
    graph_db.add_node("SUSP_VICKY", "Suspect", {"name": "Vicky (Gas-Cutter)", "phone": "+91-90001-23456"})
    graph_db.add_node("VEH_MAHINDRA", "Vehicle", {"plate": "DL-3C-AS-9988", "model": "Mahindra Pickup"})
    graph_db.add_node("LOC_CP", "Location", {"name": "Connaught Place, Delhi", "lat": 28.6304, "lon": 77.2177})
    graph_db.add_node("LOC_NOIDA", "Location", {"name": "Noida Expressway, UP", "lat": 28.5900, "lon": 77.3000})
    graph_db.add_node("WEAP_GAS_CUTTER", "Weapon", {"type": "Oxy-Acetylene Gas Cutter"})

    # Add Edges
    graph_db.add_edge("SUSP_RAJESH", "CASE_CP_HEIST", "SUSPECT_IN", {"confidence": 0.88})
    graph_db.add_edge("SUSP_VICKY", "CASE_CP_HEIST", "SUSPECT_IN", {"confidence": 0.92})
    graph_db.add_edge("SUSP_RAJESH", "SUSP_VICKY", "ACCOMPLICE", {"last_interaction": "2026-06-19T02:22:00Z"})
    graph_db.add_edge("SUSP_VICKY", "VEH_MAHINDRA", "OWNER_OF")
    graph_db.add_edge("VEH_MAHINDRA", "LOC_CP", "SEEN_AT", {"timestamp": "2026-06-19T02:45:00Z"})
    graph_db.add_edge("VEH_MAHINDRA", "LOC_NOIDA", "SEEN_AT", {"timestamp": "2026-06-19T03:15:00Z"})
    graph_db.add_edge("SUSP_RAJESH", "LOC_CP", "PRESENT_AT", {"method": "Tower Ping"})
    graph_db.add_edge("WEAP_GAS_CUTTER", "CASE_CP_HEIST", "USED_IN")
    
    print("Database seeding completed.")
