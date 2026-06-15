import mysql.connector
from flask import g
from flask_login import current_user

import config


def get_db():
    if "db" not in g:
        g.db = mysql.connector.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            database=config.MYSQL_DATABASE,
            autocommit=False,
        )
    return g.db


def get_cursor(dictionary=True):
    return get_db().cursor(dictionary=dictionary)


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
