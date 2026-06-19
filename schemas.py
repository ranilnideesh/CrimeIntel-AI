from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    username: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    role: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    username: str
    password: str

# Case Schemas
class CaseBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = "Active"

class CaseCreate(CaseBase):
    case_number: str

class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    risk_score: Optional[float] = None
    suspect_prediction: Optional[str] = None
    prevention_suggestions: Optional[str] = None

class CaseResponse(CaseBase):
    id: int
    case_number: str
    registered_at: datetime
    assigned_officer_id: Optional[int] = None
    risk_score: float
    suspect_prediction: Optional[str] = None
    prevention_suggestions: Optional[str] = None

    class Config:
        from_attributes = True

# Evidence Item Schemas
class EvidenceItemCreate(BaseModel):
    case_id: int
    name: str
    type: str

class EvidenceItemResponse(BaseModel):
    id: int
    case_id: int
    name: str
    type: str
    file_path: Optional[str] = None
    uploaded_by: int
    uploaded_at: datetime
    classification: Optional[str] = None
    confidence_score: float
    extracted_metadata: Optional[str] = None
    custody_chain: Optional[str] = None

    class Config:
        from_attributes = True

# Milestone Schemas
class MilestoneCreate(BaseModel):
    case_id: int
    title: str
    status: Optional[str] = "Pending"

class MilestoneUpdate(BaseModel):
    status: str

class MilestoneResponse(BaseModel):
    id: int
    case_id: int
    title: str
    status: str
    updated_at: datetime
    updated_by: int

    class Config:
        from_attributes = True

# Lead Schemas
class LeadCreate(BaseModel):
    case_id: int
    title: str
    description: str
    source: str
    confidence_score: float

class LeadResponse(BaseModel):
    id: int
    case_id: int
    title: str
    description: str
    source: str
    confidence_score: float
    generated_at: datetime

    class Config:
        from_attributes = True

# Audit Log Schemas
class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    action: str
    target: Optional[str] = None
    timestamp: datetime
    ip_address: Optional[str] = None

    class Config:
        from_attributes = True

# Chatbot Schemas
class ChatRequest(BaseModel):
    message: str
    case_id: Optional[int] = None

class ChatResponse(BaseModel):
    reply: str
    suggested_actions: List[str]

# Dashboard Stats Schemas
class DashboardStats(BaseModel):
    total_cases: int
    active_cases: int
    solved_cases: int
    evidence_count: int
    recent_leads: List[Dict[str, Any]]
    milestones: List[Dict[str, Any]]
    hotspots: List[Dict[str, Any]]
    suggestions: List[str]
    risk_areas: List[Dict[str, Any]]
