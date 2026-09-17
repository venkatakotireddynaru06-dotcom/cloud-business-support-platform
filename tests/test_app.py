
import pytest
from app import app
from models import db, User, Customer
from werkzeug.security import generate_password_hash

@pytest.fixture()
def client():
    app.config.update(TESTING=True, SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.add(User(name="Test User", email="test@example.com", role="Admin",
                            password_hash=generate_password_hash("Password@123")))
        db.session.add(Customer(company_name="Test Co", contact_person="Test Person",
                                email="testco@example.com", phone="123", industry="IT"))
        db.session.commit()
    with app.test_client() as client:
        yield client

def login(client):
    return client.post("/login", data={"email":"test@example.com","password":"Password@123"},
                       follow_redirects=True)

def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"

def test_login(client):
    response = login(client)
    assert response.status_code == 200
    assert b"Business Dashboard" in response.data

def test_api_requires_authentication(client):
    response = client.get("/api/dashboard")
    assert response.status_code == 401

def test_dashboard_api(client):
    login(client)
    response = client.get("/api/dashboard")
    assert response.status_code == 200
    assert response.json["customers"] == 1

def test_create_ticket_api(client):
    login(client)
    response = client.post("/api/tickets", json={
        "title": "Report access issue",
        "description": "Cannot open report",
        "priority": "High",
        "customer_id": 1
    })
    assert response.status_code == 201
    assert response.json["priority"] == "High"
