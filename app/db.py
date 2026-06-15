import psycopg2
from flask import g
from flask_login import current_user
from psycopg2.extras import RealDictCursor

import config


def _database_url():
    url = config.DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def get_db():
    if "db" not in g:
        if config.DATABASE_URL:
            g.db = psycopg2.connect(_database_url())
        else:
            g.db = psycopg2.connect(
                host=config.POSTGRES_HOST,
                port=config.POSTGRES_PORT,
                user=config.POSTGRES_USER,
                password=config.POSTGRES_PASSWORD,
                dbname=config.POSTGRES_DB,
            )
    return g.db


def get_cursor(dictionary=True):
    conn = get_db()
    if dictionary:
        return conn.cursor(cursor_factory=RealDictCursor)
    return conn.cursor()


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)


def user_has_role(*role_names):
    if not current_user.is_authenticated:
        return False
    return current_user.role_name in role_names


def is_admin():
    return user_has_role("administrator")


def is_admin_or_moderator():
    return user_has_role("administrator", "moderator")
