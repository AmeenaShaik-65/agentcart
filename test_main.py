from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_read_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"

def test_read_catalog():
    response = client.get("/catalog")
    assert response.status_code == 200
    assert "available_items" in response.json()

def test_checkout_guardrail_block():
    # To test guardrail without hitting stock limits, let's request items 
    # whose total price exceeds 5000 INR within valid stock (e.g., 5 chargers = 6495 INR)
    response = client.post("/agent/checkout", json={
        "ai_buyer_id": "test_robot_001",
        "items": [{"product_id": "item_001", "quantity": 5}] # 5 * 1299 = 6495 INR (Breaches 5000 limit)
    })
    assert response.status_code == 403
    assert "Blocked by AgentCart Safety Guardrail" in response.json()["detail"]

def test_checkout_bundle_success():
    # Test successful bundle purchase (1 Charger + 1 Cable) within stock limits
    response = client.post("/agent/checkout", json={
        "ai_buyer_id": "test_robot_002",
        "items": [
            {"product_id": "item_001", "quantity": 1},
            {"product_id": "item_002", "quantity": 1}
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "discount_message" in data