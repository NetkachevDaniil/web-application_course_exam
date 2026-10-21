"""Юнит-тесты модели пользователя app/models.py (без БД)."""
from werkzeug.security import generate_password_hash

from app.models import User


def make_user(**overrides):
    row = {
        "id": 1,
        "login": "admin",
        "last_name": "Неткачев",
        "first_name": "Даниил",
        "middle_name": "Евгеньевич",
        "role_id": 1,
        "role_name": "administrator",
        "password_hash": generate_password_hash("password123"),
    }
    row.update(overrides)
    return User(row)


def test_check_password_correct_and_wrong():
    user = make_user()
    assert user.check_password("password123") is True
    assert user.check_password("Password123") is False


def test_check_password_without_hash_is_false():
    assert make_user(password_hash=None).check_password("password123") is False


def test_display_name_and_flask_login_id():
    user = make_user()
    assert user.display_name == "Неткачев Даниил Евгеньевич"
    assert user.get_id() == "1"
    assert make_user(middle_name=None).display_name == "Неткачев Даниил"
