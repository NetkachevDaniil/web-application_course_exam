"""Интеграционные тесты аутентификации (Flask + Flask-Login + PostgreSQL)."""
import pytest

from tests.conftest import login

pytestmark = pytest.mark.integration


def test_login_page_renders(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert "== ВХОД ==" in response.get_data(as_text=True)


def test_login_success_redirects_to_catalog(client):
    response = login(client, "admin")
    assert response.status_code == 302
    page = client.get("/").get_data(as_text=True)
    assert "Неткачев Даниил Евгеньевич" in page
    assert "Выйти" in page


def test_login_wrong_password_shows_error(client):
    response = login(client, "admin", "wrong-password")
    assert response.status_code == 200
    assert "Невозможно аутентифицироваться с указанными логином и паролем" in response.get_data(as_text=True)


def test_login_unknown_user_shows_error(client):
    response = login(client, "nobody")
    assert "Невозможно аутентифицироваться" in response.get_data(as_text=True)


def test_logout_returns_guest_view(as_user):
    as_user.get("/logout")
    page = as_user.get("/").get_data(as_text=True)
    assert "Войти" in page
    assert "Петров Пётр Петрович" not in page
