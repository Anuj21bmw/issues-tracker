import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import get_db, Base
from app.models import User, Issue, UserRole, IssueStatus, IssueSeverity
from app.core.auth import get_password_hash

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

Base.metadata.create_all(bind=engine)

client = TestClient(app)

@pytest.fixture
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def test_user(db_session):
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpass"),
        full_name="Test User",
        role=UserRole.REPORTER
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def admin_user(db_session):
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpass"),
        full_name="Admin User",
        role=UserRole.ADMIN
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user):
    response = client.post(
        "/api/auth/login",
        data={"username": test_user.email, "password": "testpass"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers(admin_user):
    response = client.post(
        "/api/auth/login",
        data={"username": admin_user.email, "password": "adminpass"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_register_user():
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "newpass",
            "full_name": "New User"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["full_name"] == "New User"

def test_login_user(test_user):
    response = client.post(
        "/api/auth/login",
        data={"username": test_user.email, "password": "testpass"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_current_user(auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"

def test_create_issue(auth_headers, db_session):
    issue_data = {
        "title": "Test Issue",
        "description": "This is a test issue",
        "severity": "MEDIUM"
    }
    response = client.post("/api/issues/", data=issue_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Issue"
    assert data["severity"] == "MEDIUM"

def test_get_issues(auth_headers, test_user, db_session):
    # Create test issue
    issue = Issue(
        title="Test Issue",
        description="Test description",
        severity=IssueSeverity.HIGH,
        reporter_id=test_user.id
    )
    db_session.add(issue)
    db_session.commit()
    
    response = client.get("/api/issues/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= 1

def test_update_issue_status(admin_headers, test_user, db_session):
    # Create test issue
    issue = Issue(
        title="Test Issue",
        description="Test description",
        severity=IssueSeverity.HIGH,
        reporter_id=test_user.id
    )
    db_session.add(issue)
    db_session.commit()
    
    response = client.put(
        f"/api/issues/{issue.id}",
        json={"status": "TRIAGED"},
        headers=admin_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "TRIAGED"

def test_dashboard_stats(admin_headers):
    response = client.get("/api/dashboard/stats", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_issues" in data
    assert "issues_by_severity" in data

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"