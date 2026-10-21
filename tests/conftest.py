"""Общие фикстуры для юнит- и интеграционных тестов.

Интеграционные тесты работают с настоящей PostgreSQL 16 (в CI она поднимается
отдельным контейнером postgres:16). Перед каждым тестом схема БД пересоздаётся
из файлов schemas/*.sql, поэтому тесты не зависят друг от друга.
"""
import os
import sys
from pathlib import Path

import psycopg2
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SQL_FILES = ["schema.sql", "seed.sql", "seed_data.sql"]
TEST_PASSWORD = "password123"


def _connect():
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5432")),
        user=os.environ.get("POSTGRES_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "postgres"),
        dbname=os.environ.get("POSTGRES_DB", "electronic_library_test"),
    )


@pytest.fixture
def db_conn():
    """Пересоздаёт схему public и заполняет её тестовыми данными проекта."""
    conn = _connect()
    conn.autocommit = True
    with conn.cursor() as cur:
        cur.execute("DROP SCHEMA IF EXISTS public CASCADE; CREATE SCHEMA public;")
        for name in SQL_FILES:
            cur.execute((ROOT / "schemas" / name).read_text(encoding="utf-8"))
    yield conn
    conn.close()


@pytest.fixture
def app(db_conn, tmp_path, monkeypatch):
    """Экземпляр Flask-приложения, настроенный на тестовую БД."""
    import config  # pylint: disable=import-outside-toplevel

    monkeypatch.setattr(config, "UPLOAD_FOLDER", tmp_path / "covers")
    for key in ("POSTGRES_HOST", "POSTGRES_PORT", "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB"):
        if key in os.environ:
            value = os.environ[key]
            monkeypatch.setattr(config, key, int(value) if key == "POSTGRES_PORT" else value)
    if "POSTGRES_DB" not in os.environ:
        monkeypatch.setattr(config, "POSTGRES_DB", "electronic_library_test")

    from app import create_app  # pylint: disable=import-outside-toplevel

    application = create_app()
    application.config.update(TESTING=True)
    yield application


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, login_name, password=TEST_PASSWORD):
    return client.post("/login", data={"login": login_name, "password": password})


@pytest.fixture
def as_admin(client):
    login(client, "admin")
    return client


@pytest.fixture
def as_moderator(client):
    login(client, "moderator")
    return client


@pytest.fixture
def as_user(client):
    login(client, "user1")
    return client


def query_one(conn, sql, params=()):
    with conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchone()
