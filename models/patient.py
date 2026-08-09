from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class Patient(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str = Field(index=True)
    last_name: str = Field(index=True)
    date_of_birth: datetime
    phone: str = Field(index=True)
    email: Optional[str] = None
    address: Optional[str] = None
    medical_notes: Optional[str] = None
    doctor_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_by: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PatientCreate(SQLModel):
    first_name: str
    last_name: str
    date_of_birth: datetime
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    medical_notes: Optional[str] = None
    doctor_id: Optional[int] = None

class PatientUpdate(SQLModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    medical_notes: Optional[str] = None
    doctor_id: Optional[int] = None

class PatientResponse(SQLModel):
    id: int
    first_name: str
    last_name: str
    date_of_birth: datetime
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    medical_notes: Optional[str] = None
    doctor_id: Optional[int] = None
    created_by: int
    created_at: datetime
    updated_at: datetime