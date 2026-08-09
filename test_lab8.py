import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


# Helper function to register and log in a user, returning the access token
def get_auth_token(username: str, email: str, role: str) -> str:
    # 1. Register
    reg_response = client.post(
        "/register",
        json={
            "username": username,
            "email": email,
            "password": "SecurePassword123!",
            "full_name": f"Test {role.capitalize()}",
            "role": role,
        },
    )
    
    # 2. Login
    login_response = client.post(
        "/login",
        data={"username": username, "password": "SecurePassword123!"},
    )
    return login_response.json()["access_token"]


@pytest.fixture(scope="module")
def admin_headers():
    token = get_auth_token("admin_test", "admin@test.com", "admin")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def doctor_headers():
    token = get_auth_token("doctor_test", "doctor@test.com", "doctor")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="module")
def receptionist_headers():
    token = get_auth_token("receptionist_test", "receptionist@test.com", "receptionist")
    return {"Authorization": f"Bearer {token}"}


# --- Exercise 2 Tests: Unassigned Workflow & Claiming ---

def test_create_unassigned_patient(receptionist_headers):
    # Receptionist creates patient with doctor_id = None
    payload = {
        "first_name": "Jane",
        "last_name": "Doe",
        "date_of_birth": "1990-01-01T00:00:00",
        "phone": "+254700000000",
        "email": "jane@example.com",
    }
    response = client.post("/patients", json=payload, headers=receptionist_headers)
    assert response.status_code == 201
    assert response.json()["doctor_id"] is None


def test_list_and_claim_unassigned_patient(doctor_headers):
    # Doctor views unassigned patients
    unassigned_res = client.get("/patients/unassigned", headers=doctor_headers)
    assert unassigned_res.status_code == 200
    unassigned_list = unassigned_res.json()
    assert len(unassigned_list) > 0

    patient_id = unassigned_list[0]["id"]

    # Doctor claims the patient
    claim_res = client.patch(f"/patients/{patient_id}/claim", headers=doctor_headers)
    assert claim_res.status_code == 200
    assert claim_res.json()["patient"]["doctor_id"] is not None


# --- Exercise 3 Tests: Secure Patient Search ---

def test_search_patients(doctor_headers):
    # Search by first name
    response = client.get("/patients/search?q=Jane", headers=doctor_headers)
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) > 0
    assert results[0]["first_name"] == "Jane"


# --- Exercise 1 Tests: Audit Logs ---

def test_audit_log_created_and_accessible_by_admin(admin_headers, receptionist_headers):
    # 1. Trigger an audit log event by viewing a patient record
    patients_list = client.get("/patients", headers=admin_headers).json()
    patient_id = patients_list[0]["id"]
    
    view_res = client.get(f"/patients/{patient_id}", headers=admin_headers)
    assert view_res.status_code == 200

    # 2. Check that admin can access audit logs
    audit_res = client.get("/admin/audit-logs", headers=admin_headers)
    assert audit_res.status_code == 200
    logs = audit_res.json()
    assert len(logs) > 0

    # 3. Non-admin should be denied access to audit logs
    forbidden_res = client.get("/admin/audit-logs", headers=receptionist_headers)
    assert forbidden_res.status_code == 403