import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "CrimeIntel AI"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    # JWT Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "SUPER_SECRET_POLICE_TOKEN_KEY_987654321")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    
    # Database Settings (Dual Mode)
    # Default to SQLite for easy local execution
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./crimeintel_sql.db")
    
    # MongoDB Settings (Dual Mode)
    # If not set, app falls back to local JSON file-based document DB
    MONGODB_URL: str = os.getenv("MONGODB_URL", "")
    
    # Neo4j Settings (Dual Mode)
    # If not set, app falls back to local NetworkX-based JSON graph DB
    NEO4J_URI: str = os.getenv("NEO4J_URI", "")
    NEO4J_USER: str = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD: str = os.getenv("NEO4J_PASSWORD", "password")
    
    # Storage settings
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./evidence_storage")
    
    class Config:
        case_sensitive = True

# Add pydantic-settings dependency check and fallback
try:
    settings = Settings()
except Exception:
    # If pydantic-settings isn't installed yet, use a simple class
    class FallbackSettings:
        APP_NAME = "CrimeIntel AI"
        DEBUG = True
        API_V1_STR = "/api/v1"
        SECRET_KEY = "SUPER_SECRET_POLICE_TOKEN_KEY_987654321"
        ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = 120
        DATABASE_URL = "sqlite:///./crimeintel_sql.db"
        MONGODB_URL = ""
        NEO4J_URI = ""
        NEO4J_USER = "neo4j"
        NEO4J_PASSWORD = "password"
        UPLOAD_DIR = "./evidence_storage"
    settings = FallbackSettings()
