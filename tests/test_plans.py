
from fastapi.testclient import TestClient
from app.main import app
from uuid import uuid4

client = TestClient(app)


def test_create_plan():
    plan_name = f"Starter-{uuid4().hex[:8]}"

    response = client.post(
        "/plans/",
        json={
            "name": plan_name,
            "description": "Starter monthly subscription plan",
            "billing_cycle": "monthly",
            "price": "499.00",
            "currency": "INR",
            "status": "active",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == plan_name
    assert data["billing_cycle"] == "monthly"
    assert data["price"] == "499.00"
    assert data["currency"] == "INR"
    assert data["status"] == "active"
    assert "id" in data


def test_create_plan_with_zero_price():
    response = client.post(
        "/plans/",
        json={
            "name": f"Invalid-Plan-{uuid4().hex[:8]}",
            "description": "Plan with zero price",
            "billing_cycle": "monthly",
            "price": "0.00",
            "currency": "INR",
            "status": "active",
        },
    )

    assert response.status_code == 422


def test_create_plan_with_invalid_billing_cycle():
    response = client.post(
        "/plans/",
        json={
            "name": f"Invalid-Cycle-{uuid4().hex[:8]}",
            "description": "Plan with invalid billing cycle",
            "billing_cycle": "weekly",
            "price": "499.00",
            "currency": "INR",
            "status": "active",
        },
    )

    assert response.status_code == 422


def test_get_plan_by_id():
    plan_name = f"Get-Plan-{uuid4().hex[:8]}"

    create_response = client.post(
        "/plans/",
        json={
            "name": plan_name,
            "description": "Plan created for GET test",
            "billing_cycle": "monthly",
            "price": "299.00",
            "currency": "INR",
            "status": "active",
        },
    )

    assert create_response.status_code == 201

    plan_id = create_response.json()["id"]

    response = client.get(f"/plans/{plan_id}")

    assert response.status_code == 200
    assert response.json()["id"] == plan_id
    assert response.json()["name"] == plan_name
    assert response.json()["price"] == "299.00"


def test_get_all_plans():
    plan_name = f"List-Plan-{uuid4().hex[:8]}"

    create_response = client.post(
        "/plans/",
        json={
            "name": plan_name,
            "description": "Plan created for list test",
            "billing_cycle": "monthly",
            "price": "199.00",
            "currency": "INR",
            "status": "active",
        },
    )

    assert create_response.status_code == 201

    response = client.get("/plans/")

    assert response.status_code == 200

    plans = response.json()

    assert isinstance(plans, list)
    assert any(plan["name"] == plan_name for plan in plans)


def test_update_plan():
    plan_name = f"Update-Plan-{uuid4().hex[:8]}"

    create_response = client.post(
        "/plans/",
        json={
            "name": plan_name,
            "description": "Plan created for update test",
            "billing_cycle": "monthly",
            "price": "299.00",
            "currency": "INR",
            "status": "active",
        },
    )

    assert create_response.status_code == 201

    plan_id = create_response.json()["id"]

    update_response = client.patch(
        f"/plans/{plan_id}",
        json={
            "price": "599.00",
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["id"] == plan_id
    assert update_response.json()["price"] == "599.00"
    assert update_response.json()["name"] == plan_name


def test_update_plan_with_zero_price():
    plan_name = f"Update-Invalid-{uuid4().hex[:8]}"

    create_response = client.post(
        "/plans/",
        json={
            "name": plan_name,
            "description": "Plan created for invalid update test",
            "billing_cycle": "monthly",
            "price": "299.00",
            "currency": "INR",
            "status": "active",
        },
    )

    assert create_response.status_code == 201

    plan_id = create_response.json()["id"]

    response = client.patch(
        f"/plans/{plan_id}",
        json={
            "price": "0.00",
        },
    )

    assert response.status_code == 422



def test_delete_plan():
    plan_name = f"Delete-Plan-{uuid4().hex[:8]}"

    create_response = client.post(
        "/plans/",
        json={
            "name": plan_name,
            "description": "Plan created for delete test",
            "billing_cycle": "monthly",
            "price": "299.00",
            "currency": "INR",
            "status": "active",
        },
    )

    assert create_response.status_code == 201

    plan_id = create_response.json()["id"]

    delete_response = client.delete(f"/plans/{plan_id}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/plans/{plan_id}")

    assert get_response.status_code == 404
