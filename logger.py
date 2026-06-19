import logging
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import AuditLog

# Setup standard python logger for file logging
logging.basicConfig(
    filename="crimeintel_audit.log",
    level=logging.INFO,
    format="%(asctime)s - [AUDIT] - %(message)s"
)
logger = logging.getLogger("audit")

def log_audit(db: Session, user_id: int, action: str, target: str = None, ip_address: str = None):
    """Log security-critical operations in both database and audit log file."""
    # Write to local encrypted/secure text log file
    log_msg = f"User {user_id} performed {action} on {target or 'None'} (IP: {ip_address or 'Unknown'})"
    logger.info(log_msg)
    
    # Write to SQL database for audit query capability
    try:
        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            target=target,
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        db.add(audit_entry)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to save database audit log: {str(e)}")
        db.rollback()
