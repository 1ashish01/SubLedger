from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_subscription():
    unique_id = uuid4().hex[:8]

    customer_response = client.post(
        "/customers/",
        json={
            "name": "Subscription Customer",
            "email": f"subscription-{unique_id}@example.com",
            "phone": "9876543210",
        },
    )

    assert customer_response.status_code == 201

    customer_id = customer_response.json()["id"]

    plan_response = client.post(
        "/plans/",
        json={
            "name": f"Subscription Plan {unique_id}",
            "description": "Plan for subscription testing",
            "billing_cycle": "monthly",
            "price": "999.00",
            "currency": "INR",
            "status": "active",
        },
    )

    assert plan_response.status_code == 201

    plan_id = plan_response.json()["id"]

    response = client.post(
        "/subscriptions/",
        json={
            "customer_id": customer_id,
            "plan_id": plan_id,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["customer_id"] == customer_id
    assert data["plan_id"] == plan_id
    assert data["status"] == "active"
    assert data["end_date"] is None


def test_create_subscription_with_inactive_plan():
    unique_id = uuid4().hex[:8]

    customer_response = client.post(
        "/customers/",
        json={
            "name": "Inactive Plan Customer",
            "email": f"inactive-plan-{unique_id}@example.com",
            "phone": "9876543210",
        },
    )

    assert customer_response.status_code == 201

    customer_id = customer_response.json()["id"]

    plan_response = client.post(
        "/plans/",
        json={
            "name": f"Inactive Plan {unique_id}",
            "description": "Inactive plan for testing",
            "billing_cycle": "monthly",
            "price": "999.00",
            "currency": "INR",
            "status": "inactive",
        },
    )

    assert plan_response.status_code == 201

    plan_id = plan_response.json()["id"]

    response = client.post(
        "/subscriptions/",
        json={
            "customer_id": customer_id,
            "plan_id": plan_id,
        },
    )

    assert response.status_code == 400


def test_create_duplicate_active_subscription():
    unique_id = uuid4().hex[:8]

    customer_response = client.post(
        "/customers/",
        json={
            "name": "Duplicate Subscription Customer",
            "email": f"duplicate-sub-{unique_id}@example.com",
            "phone": "9876543210",
        },
    )

    assert customer_response.status_code == 201

    customer_id = customer_response.json()["id"]

    plan_response = client.post(
        "/plans/",
        json={
            "name": f"Duplicate Subscription Plan {unique_id}",
            "description": "Plan for duplicate subscription testing",
            "billing_cycle": "monthly",
            "price": "999.00",
            "currency": "INR",
            "status": "active",
        },
    )

    assert plan_response.status_code == 201

    plan_id = plan_response.json()["id"]

    first_response = client.post(
        "/subscriptions/",
        json={
            "customer_id": customer_id,
            "plan_id": plan_id,
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/subscriptions/",
        json={
            "customer_id": customer_id,
            "plan_id": plan_id,
        },
    )

    assert second_response.status_code == 409

def test_get_subscription_by_id():
    unique_id = uuid4().hex[:8]

    customer_response = client.post(
        "/customers/",
        json={
            "name": "Get Subscription Customer",
            "email": f"get-sub-{unique_id}@example.com",
        },
    )

    assert customer_response.status_code == 201

    customer_id = customer_response.json()["id"]

    plan_response = client.post(
        "/plans/",
        json={
            "name": f"Get Subscription Plan {unique_id}",
            "billing_cycle": "monthly",
            "price": "499.00",
            "currency": "INR",
            "status": "active",
        },
    )

    assert plan_response.status_code == 201

    plan_id = plan_response.json()["id"]

    create_response = client.post(
        "/subscriptions/",
        json={
            "customer_id": customer_id,
            "plan_id": plan_id,
        },
    )

    assert create_response.status_code == 201

    subscription_id = create_response.json()["id"]

    response = client.get(
        f"/subscriptions/{subscription_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == subscription_id
    assert data["customer_id"] == customer_id
    assert data["plan_id"] == plan_id
    assert data["status"] == "active"

def test_get_subscriptions_by_customer():
    unique_id = uuid4().hex[:8]

    customer_response = client.post(
        "/customers/",
        json={
            "name": "Customer Subscription List",
            "email": f"customer-list-{unique_id}@example.com",
        },
    )

    assert customer_response.status_code == 201

    customer_id = customer_response.json()["id"]

    plan_response = client.post(
        "/plans/",
        json={
            "name": f"Customer List Plan {unique_id}",
            "billing_cycle": "monthly",
            "price": "499.00",
            "currency": "INR",
            "status": "active",
        },
    )

    assert plan_response.status_code == 201

    plan_id = plan_response.json()["id"]

    create_response = client.post(
        "/subscriptions/",
        json={
            "customer_id": customer_id,
            "plan_id": plan_id,
        },
    )

    assert create_response.status_code == 201

    response = client.get(
        f"/subscriptions/customer/{customer_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["customer_id"] == customer_id
    assert data[0]["plan_id"] == plan_id

def test_get_all_subscriptions():
    unique_id = uuid4().hex[:8]

    customer_response = client.post(
        "/customers/",
        json={
            "name": "All Subscriptions Customer",
            "email": f"all-subscriptions-{unique_id}@example.com",
        },
    )

    assert customer_response.status_code == 201

    customer_id = customer_response.json()["id"]

    plan_response = client.post(
        "/plans/",
        json={
            "name": f"All Subscriptions Plan {unique_id}",
            "billing_cycle": "monthly",
            "price": "499.00",
            "currency": "INR",
            "status": "active",
        },
    )

    assert plan_response.status_code == 201

    plan_id = plan_response.json()["id"]

    create_response = client.post(
        "/subscriptions/",
        json={
            "customer_id": customer_id,
            "plan_id": plan_id,
        },
    )

    assert create_response.status_code == 201

    response = client.get("/subscriptions/")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)

    assert any(
        subscription["id"] == create_response.json()["id"]
        for subscription in data
    )


def test_update_subscription_status():
    unique_id = uuid4().hex[:8]

    customer_response = client.post(
        "/customers/",
        json={
            "name": "Update Subscription Customer",
            "email": f"update-sub-{unique_id}@example.com",
        },
    )

    assert customer_response.status_code == 201

    customer_id = customer_response.json()["id"]

    plan_response = client.post(
        "/plans/",
        json={
            "name": f"Update Subscription Plan {unique_id}",
            "billing_cycle": "monthly",
            "price": "499.00",
            "currency": "INR",
            "status": "active",
        },
    )

    assert plan_response.status_code == 201

    plan_id = plan_response.json()["id"]

    create_response = client.post(
        "/subscriptions/",
        json={
            "customer_id": customer_id,
            "plan_id": plan_id,
        },
    )

    assert create_response.status_code == 201

    subscription_id = create_response.json()["id"]

    response = client.patch(
        f"/subscriptions/{subscription_id}",
        json={
            "status": "cancelled",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == subscription_id
    assert data["status"] == "cancelled"

def test_update_subscription_end_date():
    unique_id = uuid4().hex[:8]

    customer_response = client.post(
        "/customers/",
        json={
            "name": "End Date Customer",
            "email": f"end-date-{unique_id}@example.com",
        },
    )

    assert customer_response.status_code == 201

    customer_id = customer_response.json()["id"]

    plan_response = client.post(
        "/plans/",
        json={
            "name": f"End Date Plan {unique_id}",
            "billing_cycle": "monthly",
            "price": "499.00",
            "currency": "INR",
            "status": "active",
        },
    )

    assert plan_response.status_code == 201

    plan_id = plan_response.json()["id"]

    create_response = client.post(
        "/subscriptions/",
        json={
            "customer_id": customer_id,
            "plan_id": plan_id,
        },
    )

    assert create_response.status_code == 201

    subscription_id = create_response.json()["id"]

    end_date = "2027-01-31T23:59:59"

    response = client.patch(
        f"/subscriptions/{subscription_id}",
        json={
            "end_date": end_date,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == subscription_id
    assert data["end_date"].startswith("2027-01-31")

def test_get_nonexistent_subscription():
    nonexistent_id = str(uuid4())

    response = client.get(
        f"/subscriptions/{nonexistent_id}"
    )

    assert response.status_code == 404