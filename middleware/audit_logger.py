from fastapi import BackgroundTasks, Request
from sqlmodel import Session
from database.session import engine
from models.audit import AuditLog

def write_audit_entry(user_id: int | None, patient_id: int | None, action: str, ip: str | None, user_agent: str | None):
    with Session(engine) as session:
        log = AuditLog(
            user_id=user_id,
            patient_id=patient_id,
            action=action,
            ip_address=ip,
            user_agent=user_agent
        )
        session.add(log)
        session.commit()

def log_audit(background_tasks: BackgroundTasks, request: Request, user_id: int | None, action: str, patient_id: int | None = None):
    client_ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    background_tasks.add_task(write_audit_entry, user_id, patient_id, action, client_ip, user_agent)