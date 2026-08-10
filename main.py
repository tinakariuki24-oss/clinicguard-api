import sys
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, status, Query, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from database.session import create_tables as create_db_and_tables, get_session
from models.user import User, UserCreate, UserResponse as UserRead
from models.patient import Patient, PatientCreate, PatientUpdate, PatientResponse
from models.audit import AuditLog
from auth import (
    hash_password as get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    get_receptionist_or_above,
    get_current_doctor as get_doctor_or_above,
    get_current_admin as get_admin_user,
)

# Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="ClinicGuard API",
    description="Role-Based Access Control Healthcare API",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# --- Portfolio Homepage Endpoint ---

@app.get("/", response_class=HTMLResponse)
async def portfolio():
    html_content = """
<html>
<head>
<title>Student Portfolio - Backend Assignments</title>
<style>
body {
font-family: 'Segoe UI', Arial, sans-serif;
margin: 40px;
background: #f5f5f5;
}
.container {
max-width: 900px;
margin: 0 auto;
background: white;
padding: 30px;
border-radius: 10px;
box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}
h1 {
color: #2c3e50;
border-bottom: 3px solid #3498db;
padding-bottom: 10px;
}
.student-info {
background: #e8f4fd;
padding: 15px;
border-radius: 8px;
margin: 20px 0;
}
.student-info strong {
color: #2c3e50;
}
.admission {
font-size: 1.2em;
color: #2980b9;
font-weight: bold;
}
.assignment {
margin: 12px 0;
padding: 15px;
background: #f8f9fa;
border-radius: 8px;
border-left: 4px solid #3498db;
transition: all 0.3s ease;
}
.assignment:hover {
background: #e8f4fd;
transform: translateX(5px);
}
.assignment a {
color: #0366d6;
text-decoration: none;
font-weight: 500;
display: flex;
align-items: center;
}
.assignment a:hover {
text-decoration: underline;
}
.badge {
display: inline-block;
background: #3498db;
color: white;
padding: 2px 10px;
border-radius: 12px;
font-size: 0.8em;
margin-right: 10px;
}
.lesson-topic {
color: #7f8c8d;
font-size: 0.9em;
margin-left: 10px;
}
.footer {
margin-top: 30px;
text-align: center;
color: #95a5a6;
font-size: 0.9em;
border-top: 1px solid #ecf0f1;
padding-top: 20px;
}
</style>
</head>
<body>
<div class="container">
<h1> Backend Development Portfolio</h1>
<div class="student-info">
<p> <strong>Student Name:</strong> Tina Kariuki</p>
<p> <strong>Admission Number:</strong> <span class="admission">C027-01-0877/2024</span></p>
<p> <strong>Email:</strong> tina.kariuki24@students.dkut.ac.ke</p>
</div>
<h2> Backend Assignments</h2>
<p style="color: #7f8c8d; margin-bottom: 20px;">Click on any assignment to view the complete code on GitHub</p>

<div class="assignment">
<a href="https://github.com/tinakariuki24-oss/book-inventory-api" target="_blank">
<span class="badge">Lesson 1</span>
<span>HTTP & Your First API</span>
<span class="lesson-topic">— FastAPI + Uvicorn, HTTP Methods, Status Codes</span>
</a>
</div>

<div class="assignment">
<a href="https://github.com/tinakariuki24-oss/book-inventory-api" target="_blank">
<span class="badge">Lesson 2</span>
<span>Docker - Packaging Your API</span>
<span class="lesson-topic">— Containers, Dockerfiles, Docker Compose</span>
</a>
</div>

<div class="assignment">
<a href="https://github.com/tinakariuki24-oss/book-inventory-api" target="_blank">
<span class="badge">Lesson 3</span>
<span>Routing, Parameters & Request Bodies</span>
<span class="lesson-topic">— Path Parameters, Query Parameters, Pydantic Validation</span>
</a>
</div>

<div class="assignment">
<a href="https://github.com/tinakariuki24-oss/book-inventory-api" target="_blank">
<span class="badge">Lesson 4</span>
<span>PostgreSQL & SQLModel – Your First Database</span>
<span class="lesson-topic">— ORM, Database Migrations, SQLModel</span>
</a>
</div>

<div class="assignment">
<a href="https://github.com/tinakariuki24-oss/book-inventory-api" target="_blank">
<span class="badge">Lesson 5</span>
<span>CRUD Operations</span>
<span class="lesson-topic">— Create, Read, Update, Delete with Error Handling</span>
</a>
</div>

<div class="assignment">
<a href="https://github.com/tinakariuki24-oss/book-inventory-api" target="_blank">
<span class="badge">Lesson 6</span>
<span>Error Handling & Validation</span>
<span class="lesson-topic">— HTTPException, Custom Validators, Global Handlers</span>
</a>
</div>

<div class="assignment">
<a href="https://github.com/tinakariuki24-oss/healthtrack-api" target="_blank">
<span class="badge">Lesson 7</span>
<span>User Authentication – JWT & Password Hashing</span>
<span class="lesson-topic">— JWT Tokens, bcrypt, Login/Register Endpoints</span>
</a>
</div>

<div class="assignment">
<a href="https://github.com/tinakariuki24-oss/clinicguard-api" target="_blank">
<span class="badge">Lesson 8</span>
<span>Authorization & Rate Limiting</span>
<span class="lesson-topic">— RBAC, Dependency Injection, Rate Limiting</span>
</a>
</div>

<div class="assignment">
<a href="https://github.com/tinakariuki24-oss/clinicguard-api" target="_blank">
<span class="badge">Lesson 9</span>
<span>File Uploads & External APIs</span>
<span class="lesson-topic">— File Validation, httpx, Environment Variables</span>
</a>
</div>

<div class="assignment">
<a href="https://github.com/tinakariuki24-oss/clinicguard-api" target="_blank">
<span class="badge">Lesson 10</span>
<span>Testing & Deployment (Cloud)</span>
<span class="lesson-topic">— Pytest, CI/CD, Render Deployment</span>
</a>
</div>

<div class="footer">
<p> Deployed on Render | Last Updated: August 2026</p>
<p style="font-size: 0.8em;"> Click on any assignment link to view the complete source code on GitHub</p>
</div>
</div>
</body>
</html>
"""
    return HTMLResponse(content=html_content)


# --- Audit Logging Helper ---

def log_action(
    session: Session,
    user_id: int,
    action: str,
    patient_id: Optional[int] = None,
    ip_address: Optional[str] = None,
):
    log_entry = AuditLog(
        user_id=user_id,
        patient_id=patient_id,
        action=action,
        ip_address=ip_address,
    )
    session.add(log_entry)
    session.commit()


# --- Authentication Endpoints ---

@app.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/hour")
def register(request: Request, user_data: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.exec(
        select(User).where(
            (User.username == user_data.username) | (User.email == user_data.email)
        )
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists")

    hashed_pw = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_pw,
        full_name=user_data.full_name,
        role=user_data.role,
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@app.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, session: Session = Depends(get_session)):
    content_type = request.headers.get("content-type", "")
    
    if "application/json" in content_type:
        body = await request.json()
        username = body.get("username")
        password = body.get("password")
    else:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

    user = session.exec(select(User).where(User.username == username)).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    user.last_login = datetime.utcnow()
    session.add(user)
    session.commit()

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role, "user_id": user.id}
    )
    return {"access_token": access_token, "token_type": "bearer"}


# --- Patient Management Endpoints ---

@app.post("/patients", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/hour")
def create_patient(
    request: Request,
    patient_data: PatientCreate,
    current_user: User = Depends(get_receptionist_or_above),
    session: Session = Depends(get_session),
):
    if patient_data.doctor_id:
        doctor = session.get(User, patient_data.doctor_id)
        if not doctor or doctor.role not in ["admin", "doctor"]:
            raise HTTPException(status_code=400, detail="Assigned user must be an active doctor")

    db_patient = Patient(**patient_data.model_dump(), created_by=current_user.id)
    session.add(db_patient)
    session.commit()
    session.refresh(db_patient)

    log_action(session, current_user.id, "CREATE_PATIENT", db_patient.id, request.client.host)
    return db_patient


@app.get("/patients", response_model=List[PatientResponse])
def get_patients(
    request: Request,
    current_user: User = Depends(get_receptionist_or_above),
    session: Session = Depends(get_session),
):
    if current_user.role == "doctor":
        statement = select(Patient).where(Patient.doctor_id == current_user.id)
    else:
        statement = select(Patient)

    patients = session.exec(statement).all()
    log_action(session, current_user.id, "VIEW_PATIENT_LIST", ip_address=request.client.host)
    return patients


@app.get("/patients/unassigned", response_model=List[PatientResponse])
def get_unassigned_patients(
    request: Request,
    current_user: User = Depends(get_doctor_or_above),
    session: Session = Depends(get_session),
):
    statement = select(Patient).where(Patient.doctor_id == None)
    patients = session.exec(statement).all()
    log_action(session, current_user.id, "VIEW_UNASSIGNED_PATIENTS", ip_address=request.client.host)
    return patients


@app.get("/patients/search", response_model=List[PatientResponse])
def search_patients(
    request: Request,
    q: str = Query(..., min_length=1, description="Search term for name or phone"),
    current_user: User = Depends(get_receptionist_or_above),
    session: Session = Depends(get_session),
):
    search_term = f"%{q}%"
    statement = select(Patient).where(
        (Patient.first_name.ilike(search_term))
        | (Patient.last_name.ilike(search_term))
        | (Patient.phone.ilike(search_term))
    )

    if current_user.role == "doctor":
        statement = statement.where(Patient.doctor_id == current_user.id)

    results = session.exec(statement).all()
    log_action(session, current_user.id, f"SEARCH_PATIENTS:{q}", ip_address=request.client.host)
    return results


@app.get("/patients/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: int,
    request: Request,
    current_user: User = Depends(get_receptionist_or_above),
    session: Session = Depends(get_session),
):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    if current_user.role == "doctor" and patient.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access forbidden: Patient not assigned to you")

    log_action(session, current_user.id, "VIEW_PATIENT_DETAIL", patient.id, request.client.host)
    return patient


@app.patch("/patients/{patient_id}/claim")
def claim_patient(
    patient_id: int,
    request: Request,
    current_user: User = Depends(get_doctor_or_above),
    session: Session = Depends(get_session),
):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    if patient.doctor_id is not None:
        raise HTTPException(status_code=400, detail="Patient is already assigned to a doctor")

    patient.doctor_id = current_user.id
    patient.updated_at = datetime.utcnow()
    session.add(patient)
    session.commit()
    session.refresh(patient)

    log_action(session, current_user.id, "CLAIM_PATIENT", patient.id, request.client.host)
    
    return {
        "message": "Patient claimed successfully",
        "patient": PatientResponse.model_validate(patient).model_dump(),
    }


@app.patch("/patients/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient_data: PatientUpdate,
    request: Request,
    current_user: User = Depends(get_receptionist_or_above),
    session: Session = Depends(get_session),
):
    patient = session.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    if current_user.role == "doctor" and patient.doctor_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access forbidden: Cannot update unassigned patient")

    update_dict = patient_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(patient, key, value)

    patient.updated_at = datetime.utcnow()
    session.add(patient)
    session.commit()
    session.refresh(patient)

    log_action(session, current_user.id, "UPDATE_PATIENT", patient.id, request.client.host)
    return patient


# --- Admin Audit Endpoints ---

@app.get("/admin/audit-logs", response_model=List[AuditLog])
def get_audit_logs(
    request: Request,
    current_user: User = Depends(get_admin_user),
    session: Session = Depends(get_session),
):
    logs = session.exec(select(AuditLog).order_by(AuditLog.timestamp.desc())).all()
    return logs