from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # Admin, Investigation Officer, Crime Analyst, Forensic Officer, Cyber Crime Officer
    created_at = Column(DateTime, default=datetime.utcnow)
    
    audit_logs = relationship("AuditLog", back_populates="user")

class Case(Base):
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="Active")  # Active, Solved, Pending
    registered_at = Column(DateTime, default=datetime.utcnow)
    assigned_officer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # AI-Generated insights stored at case level
    risk_score = Column(Float, default=0.0)
    suspect_prediction = Column(Text, nullable=True) # JSON or descriptive text
    prevention_suggestions = Column(Text, nullable=True)
    
    evidence_items = relationship("EvidenceItem", back_populates="case", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="case", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="case", cascade="all, delete-orphan")

class EvidenceItem(Base):
    __tablename__ = "evidence_items"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # Image, CCTV, PDF, Witness Statement, Audio, Call Record, Vehicle, Location, Suspect History, Previous Case File
    file_path = Column(String, nullable=True)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # AI Extraction fields
    classification = Column(String, nullable=True)
    confidence_score = Column(Float, default=0.0)
    extracted_metadata = Column(Text, nullable=True)  # Stored as JSON string
    
    # Chain of custody details
    custody_chain = Column(Text, nullable=True)  # JSON Log string of handling history

    case = relationship("Case", back_populates="evidence_items")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String, nullable=False)  # Login, Upload Evidence, View Case, Download Report, etc.
    target = Column(String, nullable=True)  # Case ID, Evidence ID, User ID, etc.
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)
    
    user = relationship("User", back_populates="audit_logs")

class Milestone(Base):
    __tablename__ = "milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    title = Column(String, nullable=False)
    status = Column(String, default="Pending")  # Completed, Pending, In Progress
    updated_at = Column(DateTime, default=datetime.utcnow)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    case = relationship("Case", back_populates="milestones")

class Lead(Base):
    __tablename__ = "leads"
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    source = Column(String, nullable=False)  # AI Engine, Suspect Match, CCTV Tracker, Witness NLP, CDR Analysis
    confidence_score = Column(Float, default=0.0)
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    case = relationship("Case", back_populates="leads")
