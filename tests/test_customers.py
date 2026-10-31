
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_create_customer():
    customer_email = f"customer-{uuid4().hex[:8]}@example.com"

    response = client.post(
        "/customers/",
        json={
            "name": "Test Customer",
            "email": customer_email,
            "phone": "9876543210",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Test Customer"
    assert data["email"] == customer_email
    assert data["phone"] == "9876543210"
    assert "id" in data


def test_create_customer_with_invalid_email():
    response = client.post(
        "/customers/",
        json={
            "name": "Invalid Email Customer",
            "email": "not-an-email",
            "phone": "9876543210",
        },
    )

    assert response.status_code == 422


def test_create_customer_with_duplicate_email():
    customer_email = f"duplicate-{uuid4().hex[:8]}@example.com"

    first_response = client.post(
        "/customers/",
        json={
            "name": "First Customer",
            "email": customer_email,
            "phone": "9876543210",
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/customers/",
        json={
            "name": "Second Customer",
            "email": customer_email,
            "phone": "9876543211",
        },
    )

    assert second_response.status_code == 409



def test_get_customer_by_id():
    customer_email = f"get-customer-{uuid4().hex[:8]}@example.com"

    create_response = client.post(
        "/customers/",
        json={
            "name": "Customer GET Test",
            "email": customer_email,
            "phone": "9876543210",
        },
    )

    assert create_response.status_code == 201

    customer_id = create_response.json()["id"]

    response = client.get(f"/customers/{customer_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == customer_id
    assert data["name"] == "Customer GET Test"
    assert data["email"] == customer_email



def test_get_all_customers():
    customer_email = f"list-customer-{uuid4().hex[:8]}@example.com"

    create_response = client.post(
        "/customers/",
        json={
            "name": "Customer List Test",
            "email": customer_email,
            "phone": "9876543210",
        },
    )

    assert create_response.status_code == 201

    response = client.get("/customers/")

    assert response.status_code == 200

    customers = response.json()

    assert isinstance(customers, list)
    assert any(
        customer["email"] == customer_email
        for customer in customers
    )



def test_update_customer():
    customer_email = f"update-customer-{uuid4().hex[:8]}@example.com"

    create_response = client.post(
        "/customers/",
        json={
            "name": "Original Customer",
            "email": customer_email,
            "phone": "9876543210",
        },
    )

    assert create_response.status_code == 201

    customer_id = create_response.json()["id"]

    update_response = client.patch(
        f"/customers/{customer_id}",
        json={
            "name": "Updated Customer",
        },
    )

    assert update_response.status_code == 200

    data = update_response.json()

    assert data["id"] == customer_id
    assert data["name"] == "Updated Customer"
    assert data["email"] == customer_email

def test_delete_customer():
    customer_email = f"delete-customer-{uuid4().hex[:8]}@example.com"

    create_response = client.post(
        "/customers/",
        json={
            "name": "Customer To Delete",
            "email": customer_email,
            "phone": "9876543210",
        },
    )

    assert create_response.status_code == 201

    customer_id = create_response.json()["id"]

    delete_response = client.delete(
        f"/customers/{customer_id}"
    )

    assert delete_response.status_code == 204

    get_response = client.get(
        f"/customers/{customer_id}"
    )

    assert get_response.status_code == 404