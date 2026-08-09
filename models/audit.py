from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    patient_id: Optional[int] = Field(default=None, foreign_key="patient.id", index=True)
    action: str = Field(index=True)
    ip_address: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)