import pytest

from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


def test_get_sign_in():
    response = client.get("/sign_up")
    assert response.status_code == 200


def test_create_user_already_validated():
    response = client.post(
        "/sign_up",
        json={
            "user_email": "test@example.com",
            "password": "foo",
        },
    )
    assert response.status_code == 400
    assert response.json() == {"user_email_error": "user already created"}


def test_created_user_not_validated():
    pass


def test_post_valid_code():
    pass


def test_post_unvalid_code():
    pass
