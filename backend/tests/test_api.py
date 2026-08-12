import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import io

from backend.app.core.database import Base, get_db
from backend.app.core.config import settings
from backend.main import app

# Setup test SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_eureka.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override database session dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    import os
    if os.path.exists("./test_eureka.db"):
        os.remove("./test_eureka.db")

client = TestClient(app)

def test_admin_login_success():
    payload = {
        "username": settings.ADMIN_USERNAME,
        "password": settings.ADMIN_PASSWORD
    }
    response = client.post("/api/eureka/admin/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_admin_login_failure():
    payload = {
        "username": "wrong_user",
        "password": "wrong_password"
    }
    response = client.post("/api/eureka/admin/login", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"

def test_register_startup_validation_errors():
    # Test submission with invalid email, short phone, and missing fields
    invalid_data = {
        "startup_name": "Test Co",
        "category": "AI / ML",
        "stage": "Ideation / Concept",
        "description": "Short",  # Min 10 characters required
        "problem_statement": "Problem details...",
        "solution": "Solution details...",
        "is_existing": False,
        "team_size": 2,
        "team_members": [
            {
                "name": "Lead Founder",
                "email": "invalid-email-format",  # Invalid email structure
                "phone": "123",  # Must be 10 digits
                "college": "My College",
                "is_lead": True
            },
            {
                "name": "Member 2",
                "email": "member2@college.edu",
                "phone": "9876543210",
                "college": "My College",
                "is_lead": False
            }
        ]
    }
    
    response = client.post(
        "/api/eureka/register",
        data={"data": json.dumps(invalid_data)}
    )
    # Pydantic validation fails, returns 422
    assert response.status_code == 422
    assert "errors" in response.json()["detail"]

def test_register_startup_success_no_file():
    valid_data = {
        "startup_name": "AI Spark Ltd",
        "category": "AI / ML",
        "stage": "Prototype / MVP Underway",
        "description": "We are building an agentic AI coding workspace that saves developers time.",
        "problem_statement": "Writing software is extremely slow and tedious for developers.",
        "solution": "We automate code changes using specialized agent teams.",
        "is_existing": True,
        "website": "https://aispark.dev",
        "current_stage": "Prototype / MVP Underway",
        "team_size": 2,
        "revenue": "No Revenue",
        "registration_details": "Incubated at Campus",
        "has_pitch_deck": False,
        "team_members": [
            {
                "name": "Ananya Sharma",
                "email": "ananya@nec.edu",
                "phone": "9876543210",
                "college": "National Engineering College",
                "department": "IT",
                "year": "3rd Year",
                "nec_id": "NEC1002",
                "is_lead": True
            },
            {
                "name": "Rahul Kumar",
                "email": "rahul@nec.edu",
                "phone": "9988776655",
                "college": "National Engineering College",
                "nec_id": "NEC1005",
                "is_lead": False
            }
        ]
    }
    
    response = client.post(
        "/api/eureka/register",
        data={"data": json.dumps(valid_data)}
    )
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["registration_id"] == "ER001"
    assert res_data["startup_name"] == "AI Spark Ltd"
    assert res_data["status"] == "Pending"
    assert len(res_data["team_members"]) == 2


def test_register_startup_success_with_pdf():
    valid_data = {
        "startup_name": "PDF Pitch Co",
        "category": "SaaS",
        "stage": "Prototype / MVP Underway",
        "description": "We are testing a workflow tool for pitch submissions.",
        "problem_statement": "Teams need a reliable way to submit pitch decks online.",
        "solution": "We provide a streamlined web form and review pipeline.",
        "is_existing": False,
        "team_size": 2,
        "has_pitch_deck": True,
        "team_members": [
            {
                "name": "Lead Tester",
                "email": "lead@test.edu",
                "phone": "9876543210",
                "college": "Test College",
                "is_lead": True
            },
            {
                "name": "Member Tester",
                "email": "member@test.edu",
                "phone": "9988776655",
                "college": "Test College",
                "is_lead": False
            }
        ]
    }

    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"

    response = client.post(
        "/api/eureka/register",
        data={"data": json.dumps(valid_data)},
        files={"pitch_deck": ("pitch.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
    )

    assert response.status_code == 200
    res_data = response.json()
    assert res_data["has_pitch_deck"] is True
    assert res_data["pitch_deck_path"].startswith("/uploads/eureka/")

def test_admin_endpoints():
    # 1. Login to get token
    login_payload = {
        "username": settings.ADMIN_USERNAME,
        "password": settings.ADMIN_PASSWORD
    }
    login_res = client.post("/api/eureka/admin/login", json=login_payload)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get registrations
    response = client.get("/api/eureka/admin/registrations", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["registrations"]) >= 1
    assert data["counts"]["pending"] >= 1
    
    db_id = data["registrations"][0]["id"]

    # 3. Update status to Approved
    status_payload = {"status": "Approved"}
    response = client.patch(
        f"/api/eureka/admin/registrations/{db_id}/status",
        json=status_payload,
        headers=headers
    )
    assert response.status_code == 200
    assert response.json()["status"] == "Approved"

    # 4. Export to Excel spreadsheet
    response = client.get("/api/eureka/admin/export", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert len(response.content) > 0  # Binary content exists
