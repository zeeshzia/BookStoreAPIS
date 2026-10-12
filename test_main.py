import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

from fastapi.testclient import TestClient
from database import Base, engine
import models
from main import app

Base.metadata.create_all(bind=engine)
client = TestClient(app)


def get_token(username, password):
    resp = client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )
    return resp.json()["access_token"]


def test_register_author():
    resp = client.post("/auth/register", json={
        "username": "pytest_author",
        "email": "pytest_author@test.com",
        "password": "123456",
        "role": "author",
    })
    assert resp.status_code == 201
    assert resp.json()["role"] == "author"


def test_register_duplicate_username_fails():
    resp = client.post("/auth/register", json={
        "username": "pytest_author",
        "email": "another@test.com",
        "password": "123456",
        "role": "author",
    })
    assert resp.status_code == 400


def test_register_reader():
    resp = client.post("/auth/register", json={
        "username": "pytest_reader",
        "email": "pytest_reader@test.com",
        "password": "123456",
        "role": "reader",
    })
    assert resp.status_code == 201


def test_login_success():
    token = get_token("pytest_author", "123456")
    assert token is not None


def test_login_wrong_password_fails():
    resp = client.post(
        "/auth/login",
        data={"username": "pytest_author", "password": "wrongpass"},
    )
    assert resp.status_code == 401


def test_author_can_add_book():
    token = get_token("pytest_author", "123456")
    resp = client.post(
        "/books/",
        json={"title": "Test Book", "description": "desc", "price": 10, "stock": 5},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["title"] == "Test Book"


def test_reader_cannot_add_book():
    token = get_token("pytest_reader", "123456")
    resp = client.post(
        "/books/",
        json={"title": "Not Allowed", "description": "desc", "price": 10, "stock": 5},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 403


def test_reader_can_buy_book():
    token = get_token("pytest_reader", "123456")
    books = client.get("/books/").json()
    book_id = books[0]["id"]

    resp = client.post(
        "/orders/",
        json={"book_id": book_id, "quantity": 1},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    assert resp.json()["quantity"] == 1


def test_buy_more_than_stock_fails():
    token = get_token("pytest_reader", "123456")
    books = client.get("/books/").json()
    book_id = books[0]["id"]

    resp = client.post(
        "/orders/",
        json={"book_id": book_id, "quantity": 9999},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 400